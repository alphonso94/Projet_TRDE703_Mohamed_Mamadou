========================================================================
         DICTIONNAIRE DE DONNÉES - DATAMART OPENFOODFACTS
========================================================================

1. TABLE DE DIMENSION : dim_product
------------------------------------------------------------------------
Description : Stocke les informations descriptives des produits avec 
gestion de l'historique SCD Type 2[cite: 

COLONNE             | TYPE          | DESCRIPTION
--------------------|---------------|------------------------------------
product_sk          | INT (PK)      | Clé technique auto-incrémentée[cite: 63].
code                | VARCHAR(50)   | Code-barres unique (EAN-13)[cite: 63, 72].
product_name        | VARCHAR(255)  | Nom du produit (priorité FR)[cite: 63, 77].
brand_sk            | INT (FK)      | Lien vers la marque (dim_brand)[cite: 63].
primary_category_sk | INT (FK)      | Lien vers la catégorie (dim_category)[cite: 63].
countries_multi     | JSON          | Liste des pays de vente[cite: 63].
effective_from      | DATE          | Début de validité (SCD2)[cite: 63, 88].
effective_to        | DATE          | Fin de validité (SCD2)[cite: 63, 88].
is_current          | TINYINT(1)    | Version active = 1, ancienne = 0[cite: 63, 88].


2. TABLE DE FAITS : fact_nutrition_snapshot
------------------------------------------------------------------------
Description : Mesures nutritionnelles pour 100g et indicateurs de 
qualité par produit et par date[cite: 66, 67].

COLONNE             | TYPE          | DESCRIPTION
--------------------|---------------|------------------------------------
fact_id             | INT (PK)      | Identifiant unique de la mesure[cite: 67].
product_sk          | INT (FK)      | Référence au produit (dim_product)[cite: 67].
time_sk             | INT (FK)      | Référence au temps (dim_time)[cite: 67].
energy_kcal_100g    | DECIMAL(10,2) | Énergie en kcal[cite: 67].
fat_100g            | DECIMAL(10,2) | Matières grasses totales[cite: 67].
saturated_fat_100g  | DECIMAL(10,2) | Acides gras saturés[cite: 67].
sugars_100g         | DECIMAL(10,2) | Sucres (0 ≤ x ≤ 100)[cite: 67, 75].
salt_100g           | DECIMAL(10,2) | Sel (Harmonisé 2.5 * sodium)[cite: 67, 76].
proteins_100g       | DECIMAL(10,2) | Protéines[cite: 67].
fiber_100g          | DECIMAL(10,2) | Fibres[cite: 67].
nutriscore_grade    | CHAR(1)       | Grade A, B, C, D ou E[cite: 68, 70].
nova_group          | INT           | Groupe NOVA (1 à 4)[cite: 68, 70].
ecoscore_grade      | CHAR(1)       | Grade environnemental[cite: 68, 70].
completeness_score  | DECIMAL(3,2)  | Score de complétude (0 à 1)[cite: 68, 73].
quality_issues_json | JSON          | Liste des anomalies détectées[cite: 68, 82].


3. TABLE DE DIMENSION : dim_time
------------------------------------------------------------------------
Description : Référentiel temporel pour les analyses hebdo[cite: 55, 82].

COLONNE             | TYPE          | DESCRIPTION
--------------------|---------------|------------------------------------
time_sk             | INT (PK)      | Format AAAAMMDD (ex: 20260127)[cite: 55].
date                | DATE          | Date complète[cite: 55].
year                | INT           | Année civile[cite: 55].
month               | INT           | Numéro du mois[cite: 55].
iso_week            | VARCHAR(10)   | Format YYYY-Www[cite: 55].


4. TABLE DE DIMENSION : dim_brand
------------------------------------------------------------------------
Description : Référentiel des marques[cite: 56].

COLONNE             | TYPE          | DESCRIPTION
--------------------|---------------|------------------------------------
brand_sk            | INT (PK)      | Clé technique[cite: 56].
brand_name          | VARCHAR(255)  | Nom normalisé de la marque[cite: 56].

========================================================================
RÈGLES MÉTIER & QUALITÉ (Silver layer)
------------------------------------------------------------------------
* Dédoublonnage : Uniquement le produit avec last_modified_t 
* Harmonisation : Sel = 2.5 * Sodium
* Bornes : 0 <= Nutriments <= 100g
* Langue : Nom produit français prioritaire
========================================================================