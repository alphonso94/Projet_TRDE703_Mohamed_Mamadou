from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import *

# --- CONFIGURATION ---
# UNIQUE_CHECKS=0 pour gérer les conflits de caractères spéciaux (ex: grec)
MYSQL_URL = "jdbc:mysql://localhost:8889/openfoodfacts_datamart?sessionVariables=FOREIGN_KEY_CHECKS=0,UNIQUE_CHECKS=0"
DB_PROPERTIES = {
    "user": "root",
    "password": "root",
    "driver": "com.mysql.cj.jdbc.Driver",
    "batchsize": "500" # Batch réduit pour éviter la saturation disque (OS errno 28)
}

spark = SparkSession.builder \
    .appName("OFF_StarSchema_Final_Production") \
    .config("spark.jars.packages", "com.mysql:mysql-connector-j:8.3.0") \
    .getOrCreate()

# --- FONCTION DE LOG (LIVRABLE QUALITÉ) ---
def log_step_metrics(step_name, input_df, output_df):
    try:
        in_count = input_df.count()
        out_count = output_df.count()
        log_schema = StructType([
            StructField("job_name", StringType(), True),
            StructField("step_name", StringType(), True),
            StructField("input_count", IntegerType(), True),
            StructField("output_count", IntegerType(), True),
            StructField("rejected_count", IntegerType(), True)
        ])
        log_data = [("OFF_StarSchema_Prod", step_name, in_count, out_count, in_count - out_count)]
        spark.createDataFrame(log_data, log_schema).write.jdbc(MYSQL_URL, "etl_metrics_logs", mode="append", properties=DB_PROPERTIES)
        print(f"📊 LOG: {step_name} enregistré.")
    except Exception as e:
        print(f"⚠️ Erreur de log: {e}")

def run_star_schema_etl():
    print("🚀 Démarrage de l'ETL (Mode Robustesse Totale)...")
    
    # 1. CHARGEMENT & SILVER
    raw_df = spark.read.csv("/Users/admin/Projet_TRDE703_Mohamed_Mamadou/openfoodfacts.csv", 
                            sep="\t", header=True, inferSchema=True)
    
    # Stratégie linguistique dynamique
    cols = raw_df.columns
    name_priority = []
    if "product_name_fr" in cols: name_priority.append(F.trim(F.col("product_name_fr")))
    if "product_name_en" in cols: name_priority.append(F.trim(F.col("product_name_en")))
    name_priority.append(F.trim(F.col("product_name")))

    # Nettoyage avec troncature préventive (255) et bornes nutritionnelles
    silver_df = raw_df.select(
        F.col("code").cast(StringType()),
        F.substring(F.coalesce(*name_priority), 1, 255).alias("product_name"),
        F.substring(F.lower(F.trim(F.col("brands"))), 1, 255).alias("brand_name"),
        F.substring(F.lower(F.trim(F.col("main_category"))), 1, 255).alias("category_code"),
        F.trim(F.col("countries")).alias("countries_multi"),
        F.col("last_modified_t").cast(LongType()).alias("last_modified_t"),
        "nutriscore_grade", "nova_group", "environmental_score_grade",
        F.when(F.col("energy-kcal_100g").between(0, 1000), F.col("energy-kcal_100g")).otherwise(None).alias("energy_kcal_100g"), 
        F.when(F.col("fat_100g").between(0, 100), F.col("fat_100g")).otherwise(None).alias("fat_100g"), 
        F.when(F.col("saturated-fat_100g").between(0, 100), F.col("saturated-fat_100g")).otherwise(None).alias("saturated_fat_100g"), 
        F.when(F.col("sugars_100g").between(0, 100), F.col("sugars_100g")).otherwise(None).alias("sugars_100g"), 
        F.when(F.col("salt_100g").between(0, 100), F.col("salt_100g"))
            .otherwise(F.when(F.col("sodium_100g").isNotNull(), F.col("sodium_100g") * 2.5).otherwise(None))
            .alias("salt_100g"),
        F.when(F.col("proteins_100g").between(0, 100), F.col("proteins_100g")).otherwise(None).alias("proteins_100g"), 
        F.when(F.col("fiber_100g").between(0, 100), F.col("fiber_100g")).otherwise(None).alias("fiber_100g"), 
        F.col("sodium_100g")         
    ).filter(F.col("code").isNotNull()).limit(500000)
    
    w = Window.partitionBy("code").orderBy(F.col("last_modified_t").desc())
    silver_df = silver_df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn").cache()
    log_step_metrics("1_SILVER_CLEANING", raw_df, silver_df)

    # 2. DIM_TIME
    print("⏳ Alimentation de dim_time...")
    dim_time_final = silver_df.select("last_modified_t").distinct().filter("last_modified_t IS NOT NULL") \
        .withColumn("ts_obj", F.from_unixtime("last_modified_t").cast("timestamp")) \
        .withColumn("time_sk", F.date_format("ts_obj", "yyyyMMdd").cast(IntegerType())) \
        .select("time_sk", F.to_date("ts_obj").alias("date"), F.year("ts_obj").alias("year")).distinct()
    dim_time_final.repartition(1).write.jdbc(MYSQL_URL, "dim_time", mode="overwrite", properties=DB_PROPERTIES)

    # 3. DIM_BRAND
    print("🏭 Alimentation de dim_brand...")
    dim_brand_df = silver_df.select("brand_name").distinct().filter("brand_name IS NOT NULL AND brand_name != ''")
    dim_brand_df.repartition(1).write.option("truncate", "true").jdbc(MYSQL_URL, "dim_brand", mode="overwrite", properties=DB_PROPERTIES)

    # 4. DIM_CATEGORY
    print("🏭 Alimentation de dim_category...")
    dim_cat_df = silver_df.select("category_code").distinct().filter("category_code IS NOT NULL") \
        .withColumn("category_name_fr", F.col("category_code")) \
        .withColumn("parent_category_sk", F.lit(None).cast(IntegerType()))
    dim_cat_df.repartition(1).write.option("truncate", "true").jdbc(MYSQL_URL, "dim_category", mode="overwrite", properties=DB_PROPERTIES)

    # 5. DIM_COUNTRY
    print("🌍 Alimentation de dim_country...")
    dim_country_df = silver_df.select(
        F.lower(F.trim(F.split("countries_multi", ",")[0])).alias("country_code")
    ).distinct().filter("country_code IS NOT NULL AND country_code != ''") \
     .withColumn("country_name_fr", F.col("country_code"))
    
    # repartition(1) + truncate pour garantir l'écriture propre vers MySQL
    dim_country_df.repartition(1).write.option("truncate", "true") \
        .jdbc(MYSQL_URL, "dim_country", mode="overwrite", properties=DB_PROPERTIES)
    
    log_step_metrics("5_DIM_COUNTRY", silver_df, dim_country_df)

    # 6. DIM_PRODUCT
    print("📦 Alimentation de dim_product...")
    brand_db = spark.read.jdbc(MYSQL_URL, "dim_brand", properties=DB_PROPERTIES).select("brand_sk", "brand_name")
    cat_db = spark.read.jdbc(MYSQL_URL, "dim_category", properties=DB_PROPERTIES).select("category_sk", "category_code")
    
    dim_product_final = silver_df.join(brand_db, "brand_name", "left").join(cat_db, "category_code", "left") \
        .select("code", "product_name", "brand_sk", F.col("category_sk").alias("primary_category_sk"),
                "countries_multi", F.current_date().alias("effective_from"), F.lit(True).alias("is_current")).dropDuplicates(["code"])
    dim_product_final.repartition(1).write.option("truncate", "true").jdbc(MYSQL_URL, "dim_product", mode="overwrite", properties=DB_PROPERTIES)

    # 7. FACT_NUTRITION
    print("📊 Alimentation de fact_nutrition_snapshot...")
    prod_db = spark.read.jdbc(MYSQL_URL, "dim_product", properties=DB_PROPERTIES).filter(F.col("is_current") == True).select("product_sk", "code")

    fact_nutrition_final = silver_df.join(prod_db, "code", "inner") \
        .withColumn("time_sk", F.date_format(F.from_unixtime("last_modified_t"), "yyyyMMdd").cast(IntegerType())) \
        .withColumn("completeness_score", (
            F.when(F.col("product_name").isNotNull(), 0.4).otherwise(0) + 
            F.when(F.col("nutriscore_grade").isNotNull(), 0.3).otherwise(0) + 
            F.when(F.col("brand_name").isNotNull(), 0.3).otherwise(0)
        ).cast(DecimalType(3,2))) \
        .select(
            "product_sk", "time_sk", F.col("energy_kcal_100g").cast(DecimalType(10,2)),
            F.col("fat_100g").cast(DecimalType(10,2)), F.col("saturated_fat_100g").cast(DecimalType(10,2)),
            F.col("sugars_100g").cast(DecimalType(10,2)), F.col("salt_100g").cast(DecimalType(10,2)),
            F.col("proteins_100g").cast(DecimalType(10,2)), F.col("fiber_100g").cast(DecimalType(10,2)),
            F.col("sodium_100g").cast(DecimalType(10,2)), "nutriscore_grade", "nova_group", 
            F.col("environmental_score_grade").alias("ecoscore_grade"), "completeness_score"
        ).distinct()

    fact_nutrition_final.repartition(1).write.jdbc(MYSQL_URL, "fact_nutrition_snapshot", mode="overwrite", properties=DB_PROPERTIES)
    
    silver_df.unpersist() # Libération mémoire système
    print("🎉 ETL TERMINÉ avec succès.")

if __name__ == "__main__":
    run_star_schema_etl()