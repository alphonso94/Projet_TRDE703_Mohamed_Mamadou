import os
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import *

# --- RÉCUPÉRATION DES VARIABLES D'ENVIRONNEMENT DOCKER ---
MYSQL_URL = os.getenv("MYSQL_URL", "jdbc:mysql://localhost:3306/openfoodfacts_datamart")
DB_PROPERTIES = {
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "root"),
    "driver": os.getenv("MYSQL_DRIVER", "com.mysql.cj.jdbc.Driver"),
    "batchsize": "2000"
}

# Configuration du SparkSession pour Docker (JAR localisé dans /opt/spark/jars/)
spark = SparkSession.builder \
    .appName("OFF_StarSchema_Production_Docker") \
    .config("spark.driver.extraClassPath", "/opt/spark/jars/mysql-connector-j-8.3.0.jar") \
    .getOrCreate()

def run_star_schema_etl():
    print(f"🚀 Connexion à : {MYSQL_URL}")
    
    # 1. CHARGEMENT & NETTOYAGE SILVER
    # Note : Le chemin du CSV doit correspondre au volume dans Docker (/app/...)
    raw_df = spark.read.csv(
        "/app/openfoodfacts.csv", 
        sep="\t", header=True, inferSchema=True
    ).limit(1000)
    
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
    
    w = Window.partitionBy("code").orderBy(F.col("last_modified_t").desc())
    silver_df = silver_df.withColumn("rn", F.row_number().over(w)) \
        .filter(F.col("rn") == 1).drop("rn").cache()

    # 2. DIM_TIME
    dim_time_final = silver_df.select("last_modified_t") \
        .withColumn("ts_obj", F.from_unixtime(F.col("last_modified_t")).cast("timestamp")) \
        .withColumn("time_sk", F.date_format("ts_obj", "yyyyMMdd").cast(IntegerType())) \
        .select(
            "time_sk", F.to_date("ts_obj").alias("date"), F.year("ts_obj").alias("year"),
            F.month("ts_obj").alias("month"), F.dayofmonth("ts_obj").alias("day"),
            F.weekofyear("ts_obj").alias("week"),
            F.concat(F.year("ts_obj"), F.lit("-W"), 
                    F.format_string("%02d", F.weekofyear("ts_obj"))).alias("iso_week")
        ).distinct()
    
    dim_time_final.repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_time", mode="overwrite", properties=DB_PROPERTIES)

    # 3. DIM_BRAND & CATEGORY & COUNTRY
    print("🏭 Alimentation des dimensions de base...")
    silver_df.select("brand_name").distinct().filter(F.col("brand_name").isNotNull()) \
        .repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_brand", mode="overwrite", properties=DB_PROPERTIES)

    silver_df.select("category_code").distinct().filter(F.col("category_code").isNotNull()) \
        .withColumn("category_name_fr", F.col("category_code")) \
        .withColumn("parent_category_sk", F.lit(None).cast(IntegerType())) \
        .repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_category", mode="overwrite", properties=DB_PROPERTIES)

    silver_df.select(F.lower(F.trim(F.split("countries_multi", ",")[0])).alias("country_code")) \
        .distinct().filter(F.col("country_code").isNotNull()) \
        .withColumn("country_name_fr", F.col("country_code")) \
        .repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_country", mode="overwrite", properties=DB_PROPERTIES)

    # 4. DIM_PRODUCT
    print("📦 Alimentation de dim_product...")
    db_brands = spark.read.jdbc(MYSQL_URL, "dim_brand", properties=DB_PROPERTIES).select("brand_sk", "brand_name")
    db_cats = spark.read.jdbc(MYSQL_URL, "dim_category", properties=DB_PROPERTIES).select("category_sk", "category_code")
    
    dim_product_final = silver_df.join(db_brands, "brand_name", "left") \
        .join(db_cats, "category_code", "left") \
        .select(
            "code", "product_name", "brand_sk", 
            F.col("category_sk").alias("primary_category_sk"),
            "countries_multi", F.current_date().alias("effective_from"),
            F.lit(None).cast("date").alias("effective_to"), F.lit(1).alias("is_current")
        ).dropDuplicates(["code"])
    
    dim_product_final.repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_product", mode="overwrite", properties=DB_PROPERTIES)

    # 5. FACT_NUTRITION
    print("📊 Alimentation de la table de faits...")
    # Correction DataType Mismatch : Cast en Int de is_current
    db_products = spark.read.jdbc(MYSQL_URL, "dim_product", properties=DB_PROPERTIES) \
        .withColumn("is_current_int", F.col("is_current").cast("int")) \
        .filter(F.col("is_current_int") == 1) \
        .select("product_sk", "code")

    fact_nutrition_final = silver_df.join(db_products, "code", "inner") \
        .withColumn("time_sk", F.date_format(F.from_unixtime(F.col("last_modified_t")).cast("timestamp"), "yyyyMMdd").cast(IntegerType())) \
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

    fact_nutrition_final.repartition(1).write.jdbc(
        MYSQL_URL, "fact_nutrition_snapshot", 
        mode="overwrite", properties=DB_PROPERTIES
    )

    print("🎉 ETL TERMINÉ AVEC SUCCÈS DANS DOCKER !")

if __name__ == "__main__":
    run_star_schema_etl()