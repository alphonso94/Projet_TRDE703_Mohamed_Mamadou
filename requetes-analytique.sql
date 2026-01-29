-- Création de la table de synthèse pour les indicateurs (KPI)
CREATE VIEW all_kpi AS
SELECT 
    -- Dimensions temporelles
    t.date,
    t.year,
    t.week,
    t.iso_week,
    
    -- Dimensions descriptives
    b.brand_name,
    p.product_name,
    p.code AS barcode,
    
    -- Mesures nutritionnelles (pour 100g)
    f.energy_kcal_100g,
    f.fat_100g,
    f.saturated_fat_100g,
    f.sugars_100g,
    f.salt_100g,
    f.proteins_100g,
    f.fiber_100g,
    
    -- Scores et Qualité
    f.nutriscore_grade,
    f.nova_group,
    f.ecoscore_grade,
    f.completeness_score,
    f.quality_issues_json
FROM fact_nutrition_snapshot f
JOIN dim_product p ON f.product_sk = p.product_sk
JOIN dim_brand b ON p.brand_sk = b.brand_sk
JOIN dim_time t ON f.time_sk = t.time_sk;

-- Ajout d'index pour optimiser les futures requêtes analytiques
ALTER TABLE all_kpi ADD INDEX (brand_name);
ALTER TABLE all_kpi ADD INDEX (nutriscore_grade);
ALTER TABLE all_kpi ADD INDEX (iso_week);


-- Requête analytique : Top 10 des marques avec la meilleure proportion de produits Nutri-Score A et B

SELECT 
    brand_name,
    COUNT(*) AS total_produits,
    SUM(CASE WHEN nutriscore_grade IN ('a', 'b') THEN 1 ELSE 0 END) AS nb_bons_scores,
    ROUND(SUM(CASE WHEN nutriscore_grade IN ('a', 'b') THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS proportion_A_B
FROM all_kpi
GROUP BY brand_name
HAVING total_produits > 5 -- Filtre pour éviter les marques avec un seul produit
ORDER BY proportion_A_B DESC
LIMIT 10;

-- Requête analytique : Évolution hebdomadaire moyenne des teneurs en sucres pour les produits de la catégorie "Boissons"
--Évolution hebdomadaire de la complétude des nutriments

--Permet de suivre l'amélioration de la qualité de la base de données au fil du temps.


SQL
SELECT 
    iso_week,
    ROUND(AVG(completeness_score), 4) AS completude_moyenne,
    COUNT(*) AS nb_produits_ajoutes_ou_modifies
FROM all_kpi
GROUP BY iso_week
ORDER BY iso_week ASC;