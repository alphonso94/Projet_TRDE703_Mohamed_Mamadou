
---

# 🧪 CAHIER DE TESTS ET RECETTE 

**Projet :** Datamart Nutritionnel Open Food Facts

**Environnement :** PySpark / MySQL 8.x

**Statut final :** Opérationnel ✅

---

## 1. TESTS D'INTÉGRITÉ DU PIPELINE 

Ces tests valident le bon déroulement technique du script `main.py`.

| ID | Libellé du Test | Action / Script | Résultat Attendu | Statut |
| --- | --- | --- | --- | --- |
| **T01** | Connectivité JDBC | Lancement de `main.py` | Établissement de la session sans erreur de Driver | ✅ |
| **T02** | Gestion Mémoire | Surveillance des ressources | Pas d'erreur `OS errno 28` grâce au `batchsize=500` | ✅ |
| **T03** | Logging Qualité | `SELECT * FROM etl_metrics_logs` | Présence des 7 étapes de l'ETL avec les comptes de lignes | ✅ |

---

## 2. TESTS DE QUALITÉ DES DONNÉES (INTÉGRITÉ)

Vérification des règles de gestion appliquées par Spark avant l'insertion.

### A. Test d'Unicité (Dédoublonnage)

* **Objectif :** S'assurer qu'un code-barres n'apparaît qu'une seule fois.
* **Requête SQL :**
```sql
SELECT code, COUNT(*) FROM dim_product GROUP BY code HAVING COUNT(*) > 1;

```


* **Résultat attendu :** 0 ligne (Aucun doublon trouvé).

### B. Test de Normalisation (Cas "Haïti")

* **Objectif :** Vérifier que les conflits d'accents ont été résolus.
* **Requête SQL :**
```sql
SELECT country_code FROM dim_country WHERE country_code = 'haïti';

```


* **Résultat attendu :** 1 seule ligne en minuscules, sans doublon d'index.

---

## 3. TESTS DU SCHÉMA EN ÉTOILE (RELATIONNEL)

Vérification des jointures entre la table de faits et les dimensions.

| ID | Description | Requête de Vérification | Résultat Attendu |
| --- | --- | --- | --- |
| **S01** | **Orphelins** | `SELECT COUNT(*) FROM fact_nutrition_snapshot f LEFT JOIN dim_product p ON f.product_sk = p.product_sk WHERE p.product_sk IS NULL` | **0** (Toutes les lignes de faits sont liées à un produit) |
| **S02** | **Complétude** | `SELECT MIN(completeness_score) FROM all_kpi` | Valeur entre **0.00 et 1.00** |
| **S03** | **Volume** | `SELECT COUNT(*) FROM all_kpi` | Correspondance avec le volume final filtré (**1135**) |

---

## 4. TESTS FONCTIONNELS (MÉTIERS)

Validation des indicateurs calculés pour le reporting Tableau.

* **Test du Nutri-Score Binaire :**
* **Requête :** `SELECT nutriscore_grade, is_healthy_score FROM all_kpi WHERE nutriscore_grade = 'a' LIMIT 1;`
* **Attendu :** `is_healthy_score` doit être égal à **1**.


* **Test du Recalcul Sel/Sodium :**
* **Requête :** `SELECT (salt_100g / sodium_100g) as ratio FROM all_kpi WHERE sodium_100g > 0 LIMIT 1;`
* **Attendu :** Ratio proche de **2.5**.



---

## 5. BILAN GLOBAL DES ANOMALIES

* **Taux de rejet :** Environ 2% des lignes initiales (principalement dues à l'absence de code-barres ou de données nutritionnelles minimales).
* **Actions correctives :** Troncature forcée à 255 caractères pour stabiliser les noms de produits très longs.


