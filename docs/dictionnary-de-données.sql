========================================================================
         DICTIONNAIRE DE DONNÉES - DATAMART OPENFOODFACTS
========================================================================

1. TABLE DE DIMENSION : dim_product
------------------------------------------------------------------------
Description : Stocke les informations descriptives des produits avec 
gestion de l'historique SCD Type 2

COLONNE             | TYPE          | DESCRIPTION
--------------------|---------------|------------------------------------
product_sk          | INT (PK)      | Clé technique auto-incrémentée
code                | VARCHAR(50)   | Code-barres unique (EAN-13)
product_name        | VARCHAR(255)  | Nom du produit (priorité FR)
brand_sk            | INT (FK)      | Lien vers la marque (dim_brand)
primary_category_sk | INT (FK)      | Lien vers la catégorie (dim_category)
effective_from      | DATE          | Début de validité (SCD2)
effective_to        | DATE          | Fin de validité (SCD2).
is_current          | TINYINT(1)    | Version active = 1, ancienne = 0


2. TABLE DE FAITS : fact_nutrition_snapshot
------------------------------------------------------------------------
Description : Mesures nutritionnelles pour 100g et indicateurs de 
qualité par produit et par date

COLONNE             | TYPE          | DESCRIPTION
--------------------|---------------|------------------------------------
fact_id             | INT (PK)      | Identifiant unique de la mesure
product_sk          | INT (FK)      | Référence au produit (dim_product)
time_sk             | INT (FK)      | Référence au temps (dim_time)
energy_kcal_100g    | DECIMAL(10,2) | Énergie en kcal[cite:
fat_100g            | DECIMAL(10,2) | Matières grasses totales
saturated_fat_100g  | DECIMAL(10,2) | Acides gras saturés
sugars_100g         | DECIMAL(10,2) | Sucres (0 ≤ x ≤ 100)[cite:
salt_100g           | DECIMAL(10,2) | Sel (Harmonisé 2.5 * sodium)
proteins_100g       | DECIMAL(10,2) | Protéines
fiber_100g          | DECIMAL(10,2) | Fibres
nutriscore_grade    | CHAR(1)       | Grade A, B, C, D ou 
nova_group          | INT           | Groupe NOVA (1 à 4)
ecoscore_grade      | CHAR(1)       | Grade environnemental
completeness_score  | DECIMAL(3,2)  | Score de complétude 
quality_issues_json | JSON          | Liste des anomalies 


3. TABLE DE DIMENSION : dim_time
------------------------------------------------------------------------
Description : Référentiel temporel pour les analyses hebdo

COLONNE             | TYPE          | DESCRIPTION
--------------------|---------------|------------------------------------
time_sk             | INT (PK)      | Format AAAAMMDD (ex: 20260127)
date                | DATE          | Date complète
year                | INT           | Année civile
month               | INT           | Numéro du mois
iso_week            | VARCHAR(10)   | Format YYYY-Www


4. TABLE DE DIMENSION : dim_brand
------------------------------------------------------------------------
Description : Référentiel des marques

COLONNE             | TYPE          | DESCRIPTION
--------------------|---------------|------------------------------------
brand_sk            | INT (PK)      | Clé technique
brand_name          | VARCHAR(255)  | Nom normalisé de la marque

========================================================================
RÈGLES MÉTIER & QUALITÉ (Silver layer)
------------------------------------------------------------------------
* Dédoublonnage : Uniquement le produit avec last_modified_t 
* Harmonisation : Sel = 2.5 * Sodium
* Bornes : 0 <= Nutriments <= 100g
* Langue : Nom produit français prioritaire
========================================================================