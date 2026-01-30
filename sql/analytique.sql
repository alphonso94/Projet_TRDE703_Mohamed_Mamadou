


-- Requête analytique : Top 10 des marques avec la meilleure proportion de produits Nutri-Score A et B

SELECT 
    brand_name,
    COUNT(*) AS total_produits,
    SUM(CASE WHEN nutriscore_grade IN ('a', 'b') THEN 1 ELSE 0 END) AS nb_bons_scores,
    ROUND(SUM(CASE WHEN nutriscore_grade IN ('a', 'b') THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS proportion_A_B
FROM reporting_kpi
GROUP BY brand_name
HAVING total_produits > 5
ORDER BY proportion_A_B DESC
LIMIT 10;

--Tableau croisé : Répartition des produits par catégorie et Nutri-Score

SELECT 
    category,
    nutriscore_grade,
    COUNT(*) AS nombre_produits
FROM reporting_kpi
WHERE nutriscore_grade IS NOT NULL
GROUP BY category, nutriscore_grade
ORDER BY category, nutriscore_grade;

--heatmap: Moyenne de sucre pour 100g par pays et catégorie de produit

SELECT 
    country,
    category,
    ROUND(AVG(sugars_100g), 2) AS moyenne_sucre_100g
FROM reporting_kpi
WHERE country IS NOT NULL AND sugars_100g IS NOT NULL
GROUP BY country, category
ORDER BY moyenne_sucre_100g DESC;

--  Taux de complétude moyen des données par marque
SELECT 
    brand_name,
    ROUND(AVG(completeness_score) * 100, 2) AS taux_completude_moyen
FROM reporting_kpi
GROUP BY brand_name
ORDER BY taux_completude_moyen DESC;

--list des anomalies nutritionnelles : produits avec des niveaux excessifs de sel, sucre ou calories
SELECT 
    barcode,
    product_name,
    brand_name,
    salt_100g,
    sugars_100g
FROM reporting_kpi
WHERE salt_100g > 25 
   OR sugars_100g > 80
   OR energy_kcal_100g > 900; 

-- Évolution hebdomadaire du taux de complétude des données
   SELECT 
    iso_week,
    ROUND(AVG(completeness_score) * 100, 2) AS completude_hebdo
FROM reporting_kpi
GROUP BY iso_week
ORDER BY iso_week ASC;

-- ETL Metrics Extraction
-Description: Requête SQL pour extraire les métriques ETL des logs
SELECT 
    step_name, 
    input_count AS 'Entrée (Bronze)', 
    output_count AS 'Sortie (Gold)', 
    rejected_count AS 'Rejets (Nettoyage)',
    ROUND((output_count / input_count) * 100, 2) AS 'Taux de Validité %'
FROM etl_metrics_logs
ORDER BY timestamp DESC;