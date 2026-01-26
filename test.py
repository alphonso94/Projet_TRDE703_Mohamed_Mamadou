from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import *
import os

# --- CONFIGURATION ---
# FOREIGN_KEY_CHECKS=0 est essentiel pour permettre le TRUNCATE sur les tables liées
MYSQL_URL = "jdbc:mysql://localhost:8889/openfoodfacts_datamart?sessionVariables=FOREIGN_KEY_CHECKS=0"
DB_PROPERTIES = {
    "user": "root",
    "password": "root",
    "driver": "com.mysql.cj.jdbc.Driver",
    "batchsize": "2000"
}

spark = SparkSession.builder \
    .appName("OFF_StarSchema_Final_Production") \
    .config("spark.jars.packages", "com.mysql:mysql-connector-j:8.3.0") \
    .getOrCreate()

def run_star_schema_etl():
    print("🚀 Démarrage de l'ETL - Nettoyage et Normalisation...")
    
    # 1. CHARGEMENT & NETTOYAGE INITIAL (SILVER)
    raw_df = spark.read.csv(
        "/Users/admin/Projet_TRDE703_Mohamed_Mamadou/openfoodfacts.csv", 
        sep="\t", header=True, inferSchema=True
    ).limit(1000)
    
    # Normalisation stricte : trim et passage en minuscules pour les clés textuelles
    silver_df = raw_df.select(
        F.col("code").cast(StringType()),
        F.trim(F.col("product_name")).alias("product_name"),
        F.lower(F.trim(F.col("brands"))).alias("brand_name"),
        F.lower(F.trim(F.col("main_category"))).alias("category_code"),
        F.trim(F.col("countries")).alias("countries_multi"),
        F.col("last_modified_t").cast(LongType()).alias("last_modified_t"),
        "nutriscore_grade", "nova_group", "environmental_score_grade",
        F.col("energy-kcal_100g").alias("energy_kcal_100g"), 
        "fat_100g", 
        F.col("saturated-fat_100g").alias("saturated_fat_100g"), 
        "sugars_100g", "salt_100g", "proteins_100g", 
        "fiber_100g", "sodium_100g"         
    ).filter(F.col("code").isNotNull())
    
    # Déduplication technique pour ne garder que la version la plus récente par code produit
    w = Window.partitionBy("code").orderBy(F.col("last_modified_t").desc())
    silver_df = silver_df.withColumn("rn", F.row_number().over(w)) \
        .filter(F.col("rn") == 1).drop("rn").cache()

    # 2. DIM_TIME
    print("⏳ Alimentation de dim_time...")
    dim_time_final = silver_df.select("last_modified_t") \
        .withColumn("ts_obj", F.from_unixtime(F.col("last_modified_t")).cast("timestamp")) \
        .withColumn("time_sk", F.date_format("ts_obj", "yyyyMMdd").cast(IntegerType())) \
        .select(
            "time_sk",
            F.to_date("ts_obj").alias("date"),
            F.year("ts_obj").alias("year"),
            F.month("ts_obj").alias("month"),
            F.dayofmonth("ts_obj").alias("day"),
            F.weekofyear("ts_obj").alias("week"),
            F.concat(F.year("ts_obj"), F.lit("-W"), 
                    F.format_string("%02d", F.weekofyear("ts_obj"))).alias("iso_week")
        ).distinct()
    
    dim_time_final.repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_time", mode="overwrite", properties=DB_PROPERTIES)

    # 3. DIM_BRAND
    print("🏭 Alimentation de dim_brand...")
    silver_df.select("brand_name").distinct() \
        .filter(F.col("brand_name").isNotNull() & (F.col("brand_name") != "")) \
        .repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_brand", mode="overwrite", properties=DB_PROPERTIES)

    # 4. DIM_CATEGORY
    print("🏭 Alimentation de dim_category...")
    silver_df.select("category_code").distinct() \
        .filter(F.col("category_code").isNotNull() & (F.col("category_code") != "")) \
        .withColumn("category_name_fr", F.col("category_code")) \
        .withColumn("parent_category_sk", F.lit(None).cast(IntegerType())) \
        .repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_category", mode="overwrite", properties=DB_PROPERTIES)

    # 5. DIM_COUNTRY
    print("🌍 Alimentation de dim_country...")
    silver_df.select(F.lower(F.trim(F.split("countries_multi", ",")[0])).alias("country_code")) \
        .distinct().filter(F.col("country_code").isNotNull() & (F.col("country_code") != "")) \
        .withColumn("country_name_fr", F.col("country_code")) \
        .repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_country", mode="overwrite", properties=DB_PROPERTIES)

    # 6. DIM_PRODUCT
    print("📦 Alimentation de dim_product...")
    # Récupération des clés étrangères depuis MySQL
    dim_brand_db = spark.read.jdbc(MYSQL_URL, "dim_brand", properties=DB_PROPERTIES).select("brand_sk", "brand_name")
    dim_cat_db = spark.read.jdbc(MYSQL_URL, "dim_category", properties=DB_PROPERTIES).select("category_sk", "category_code")
    
    dim_product_final = silver_df.join(dim_brand_db, "brand_name", "left") \
        .join(dim_cat_db, "category_code", "left") \
        .select(
            "code", "product_name", "brand_sk", 
            F.col("category_sk").alias("primary_category_sk"),
            "countries_multi", 
            F.current_date().alias("effective_from"),
            F.lit(None).cast("date").alias("effective_to"),
            F.lit(1).alias("is_current")
        ).dropDuplicates(["code"])
    
    dim_product_final.repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_product", mode="overwrite", properties=DB_PROPERTIES)

    # 7. FACT_NUTRITION

    print("📊 Alimentation de fact_nutrition_snapshot...")
    
    # SOLUTION : On cast explicitement en Integer pour éviter le conflit Boolean/Int
    dim_prod_db = spark.read.jdbc(MYSQL_URL, "dim_product", properties=DB_PROPERTIES) \
        .withColumn("is_current_int", F.col("is_current").cast("int")) \
        .filter(F.col("is_current_int") == 1) \
        .select("product_sk", "code")

    fact_nutrition_final = silver_df.join(dim_prod_db, "code", "inner") \
        .withColumn("time_sk", F.date_format(
            F.from_unixtime(F.col("last_modified_t")).cast("timestamp"), "yyyyMMdd"
        ).cast(IntegerType())) \
        .withColumn("completeness_score", (
            F.when(F.col("product_name").isNotNull(), 0.4).otherwise(0) + 
            F.when(F.col("nutriscore_grade").isNotNull(), 0.3).otherwise(0) + 
            F.when(F.col("brand_name").isNotNull(), 0.3).otherwise(0)
        ).cast(DecimalType(3,2))) \
        .withColumn("quality_issues_json", F.lit('[]')) \
        .select(
            "product_sk", "time_sk",
            F.col("energy_kcal_100g").cast(DecimalType(10,2)),
            F.col("fat_100g").cast(DecimalType(10,2)),
            F.col("saturated_fat_100g").cast(DecimalType(10,2)),
            F.col("sugars_100g").cast(DecimalType(10,2)),
            F.col("salt_100g").cast(DecimalType(10,2)),
            F.col("proteins_100g").cast(DecimalType(10,2)),
            F.col("fiber_100g").cast(DecimalType(10,2)),
            F.col("sodium_100g").cast(DecimalType(10,2)),
            "nutriscore_grade", "nova_group", 
            F.col("environmental_score_grade").alias("ecoscore_grade"),
            "completeness_score", "quality_issues_json"
        ).distinct()

    # Écriture finale
    fact_nutrition_final.repartition(1).write.jdbc(
        MYSQL_URL, "fact_nutrition_snapshot", 
        mode="overwrite", properties=DB_PROPERTIES
    )

    print("🎉 ETL TERMINÉ : Le Star Schema est à jour dans MySQL.")

if __name__ == "__main__":
    run_star_schema_etl()