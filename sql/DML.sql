-- Création de la table de synthèse pour les indicateurs (KPI)
CREATE VIEW reporting_kpi AS
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






