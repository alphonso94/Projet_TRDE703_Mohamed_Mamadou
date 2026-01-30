-- Initialisation de la base de données
CREATE DATABASE IF NOT EXISTS openfoodfacts_datamart;
USE openfoodfacts_datamart;

SET FOREIGN_KEY_CHECKS = 0;
-- 1. Table Dimension Temps
DROP TABLE IF EXISTS dim_time;
CREATE TABLE dim_time (
    time_sk INT PRIMARY KEY,
    date DATE,
    year INT,
    month INT,
    day INT,
    week INT,
    iso_week VARCHAR(10)
) ENGINE=InnoDB;

-- 2. Table Dimension Marque
DROP TABLE IF EXISTS dim_brand;
CREATE TABLE dim_brand (
    brand_sk INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(255) UNIQUE -- L'unicité est gérée ici
) ENGINE=InnoDB;

-- 3. Table Dimension Catégorie
DROP TABLE IF EXISTS dim_category;
CREATE TABLE dim_category (
    category_sk INT AUTO_INCREMENT PRIMARY KEY,
    category_code VARCHAR(255) UNIQUE,
    category_name_fr VARCHAR(255),
    parent_category_sk INT
) ENGINE=InnoDB;

-- 4. Table Dimension Pays
DROP TABLE IF EXISTS dim_country;
CREATE TABLE dim_country (
    country_sk INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(100) UNIQUE,
    country_name_fr VARCHAR(255)
) ENGINE=InnoDB;

-- 5. Table Dimension Produit (SCD Type 2 ready)
DROP TABLE IF EXISTS dim_product;
CREATE TABLE dim_product (
    product_sk INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50),
    product_name TEXT,
    brand_sk INT,
    primary_category_sk INT,
    countries_multi TEXT,
    effective_from DATE,
    effective_to DATE,
    is_current TINYINT(1),
    INDEX (code)
) ENGINE=InnoDB;

-- 6. Table de Faits (Snapshot Nutritionnel)
DROP TABLE IF EXISTS fact_nutrition_snapshot;
CREATE TABLE fact_nutrition_snapshot (
    fact_sk INT AUTO_INCREMENT PRIMARY KEY,
    product_sk INT,
    time_sk INT,
    energy_kcal_100g DECIMAL(10,2),
    fat_100g DECIMAL(10,2),
    saturated_fat_100g DECIMAL(10,2),
    sugars_100g DECIMAL(10,2),
    salt_100g DECIMAL(10,2),
    proteins_100g DECIMAL(10,2),
    fiber_100g DECIMAL(10,2),
    sodium_100g DECIMAL(10,2),
    nutriscore_grade CHAR(1),
    nova_group INT,
    ecoscore_grade CHAR(1),
    completeness_score DECIMAL(3,2),
    quality_issues_json JSON,
    FOREIGN KEY (product_sk) REFERENCES dim_product(product_sk),
    FOREIGN KEY (time_sk) REFERENCES dim_time(time_sk)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;
