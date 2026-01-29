Voici une proposition de **README** structurée et professionnelle pour votre projet, rédigée selon les exigences de rigueur du niveau M1.

---

# OFF Nutrition & Quality - ETL Pipeline (PySpark)

## 📌 Présentation du Projet

Ce projet consiste en la mise en place d'une chaîne d'intégration de données de bout en bout à partir des données **OpenFoodFacts (OFF)**. L'objectif est de transformer des données massives brutes (Datalake) en un **Datamart MySQL** modélisé en étoile pour répondre à des problématiques métier sur la qualité nutritionnelle.

## 🏗️ Architecture Technique

Le pipeline suit une architecture de données en couches (Medallion Architecture):

* 
**Bronze (Ingestion)** : Lecture des données brutes JSON/CSV avec schéma explicite (pas d'inférence).


* 
**Silver (Conformation)** : Normalisation des types, dédoublonnage par code-barres (conservation du plus récent via `last_modified_t`) et nettoyage des unités (sel/sodium, kcal/kj).


* 
**Gold (Modélisation)** : Structuration en schéma en étoile avec gestion de l'historisation **SCD Type 2** pour les produits.



## 📊 Modèle de Données (Datamart)

Le datamart est composé des tables suivantes:

* 
**Faits** : `fact_nutrition_snapshot` (mesures pour 100g, scores, indices de complétude).


* **Dimensions** :
* 
`dim_product` (SCD2 : `effective_from`, `is_current`).


* 
`dim_brand` (Marques).


* 
`dim_category` (Hiérarchie des catégories).


* 
`dim_time` (Granularité temporelle : ISO week, mois, année).





## 🛡️ Règles de Qualité & Métriques

Le pipeline intègre des contrôles rigoureux:

* 
**Unicité** : Un seul produit courant (`is_current = 1`) par code-barres.


* 
**Complétude pondérée** : Score calculé sur la présence du nom, de la marque, et des nutriments clés.


* 
**Contrôle des bornes** : Validation des valeurs nutritionnelles (ex: 0 ≤ sucre ≤ 100).


* 
**Reporting** : Export d'un fichier JSON de métriques après chaque run (nb produits filtrés, taux d'anomalies).



## 🚀 Installation et Utilisation

### Prérequis

* 
**Apache Spark** (PySpark).


* 
**MySQL 8**.


* 
**Connector JDBC MySQL** (`mysql-connector-j-8.x.jar`).



### Lancement de l'ETL

```bash
spark-submit --jars path/to/mysql-connector-j.jar main.py

```

### Génération des KPIs

Une fois le chargement terminé, la table `all_kpi` permet d'exécuter les requêtes analytiques:

* Top 10 marques par Nutri-Score A/B.


* Évolution hebdomadaire de la complétude.


* Heatmap des sucres par catégorie.



## 📁 Structure du Repository

* 
`/etl` : Code PySpark (Ingestion, Transformation, Ingestion JDBC).


* 
`/sql` : Scripts DDL de création des tables et requêtes analytiques.


* 
`/docs` : Dictionnaire des données et schémas d'architecture.


* 
`/conf` : Paramètres de connexion base de données.
Voici la **Note d'Architecture** détaillée pour votre projet, structurée pour répondre aux exigences académiques du niveau M1.

---

## Note d’Architecture : Pipeline OFF Nutrition & Qualité

### 1. Choix Technologiques

* 
**Moteur d'exécution :** **Apache Spark (PySpark)** a été choisi pour sa capacité à traiter des données massives (Big Data) de manière distribuée, répondant ainsi à la spécificité de l'exercice.


* 
**Stockage Cible :** **MySQL 8** via le connecteur **JDBC**, structuré en Datamart pour optimiser les performances des requêtes analytiques SQL.


* 
**Langage :** **Python** pour la flexibilité de ses bibliothèques de manipulation de données et sa compatibilité native avec Spark.



### 2. Stratégie d'Architecture (Médaillon)

L'intégration suit une progression de données en trois étapes pour garantir la traçabilité et la qualité:

* 
**Couche Bronze (Ingestion) :** Lecture du fichier source (CSV/JSON) avec un **schéma explicite** pour garantir la robustesse du pipeline en production.


* 
**Couche Silver (Conformation) :** * Nettoyage des données : suppression des doublons par code-barres en conservant l'enregistrement le plus récent via `last_modified_t`.


* Normalisation : harmonisation des unités (sel/sodium) et filtrage des valeurs aberrantes (0 ≤ nutriments ≤ 100).




* 
**Couche Gold (Modélisation) :** Passage d'un format plat à un **schéma en étoile** pour l'analyse décisionnelle.



### 3. Modélisation du Datamart

Le modèle repose sur une table de faits centrale et plusieurs dimensions descriptives:

* 
**Table de Faits (`fact_nutrition_snapshot`) :** Contient les métriques nutritionnelles (énergies, sucres, graisses) et le score de complétude calculé.


* **Dimensions :**
* 
**dim_product :** Implémentation du **SCD Type 2** (Slowly Changing Dimension) pour historiser les changements de produits (hash des attributs, `effective_from`, `is_current`).


* 
**dim_time :** Permet une analyse temporelle à la semaine (ISO week) et au jour.


* 
**dim_brand & dim_category :** Normalisation des référentiels pour faciliter les classements par marque ou catégorie.





### 4. Gestion de la Qualité (Data Quality)

La qualité est mesurée à chaque run et exportée sous format JSON:

* 
**Complétude pondérée :** Calcul d'un score basé sur la présence des champs critiques (Nom, Nutriments, Catégorie, Marque).


* 
**Détection d'anomalies :** Identification automatique des valeurs hors bornes (ex: sel > 25g) stockées dans le champ `quality_issues_json`.



### 5. Stratégie de Chargement (Upsert)

Pour garantir l'**idempotence** (capacité à rejouer le script sans créer de doublons), nous utilisons la stratégie suivante:

* **Dimensions :** Mode `append` avec gestion des clés naturelles uniques.
* **Faits :** Chargement par snapshot quotidien utilisant des `time_sk` pour éviter les recouvrements.

---

