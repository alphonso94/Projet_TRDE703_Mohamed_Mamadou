https://github.com/alphonso94/Projet_TRDE703_Mohamed_Mamadou.git

# Projet Open Food Facts - Datamart ETL

## 📌 Présentation

Ce projet réalise un pipeline **ETL** (Extract, Transform, Load) complet utilisant **PySpark** pour traiter les données mondiales d'Open Food Facts. L'objectif est de transformer des données CSV brutes en un **Star Schema** (schéma en étoile) optimisé pour le reporting décisionnel dans **MySQL** et la visualisation dans **Tableau**.

## 🛠️ Stack Technique

* **Traitement :** Apache Spark (Engine local)
* **Langage :** Python 3.14
* **Stockage :** MySQL 8.x
* **Connectivité :** JDBC MySQL Connector J 8.3.0

## 📂 Structure du Projet

* `/etl` : Script `main.py` contenant toute la logique de nettoyage et de chargement.
* `/sql` : Scripts DDL pour la création des tables et DML pour la vue analytique `reporting_kpi`.
* `/docs` : Dictionnaire des données et Note d'architecture.
* `/tests` : Cahier de recette et logs de qualité.

## 🚀 Guide de Démarrage Rapide

### 1. Préparation de la Base de Données

Exécutez le script `/sql/DDL.sql` dans votre instance MySQL pour initialiser le schéma. Cela créera les tables de dimensions, la table de faits, ainsi que la vue de reporting.

### 2. Configuration de l'ETL

Modifiez les variables `MYSQL_URL` et `DB_PROPERTIES` dans le fichier `etl/main.py` pour correspondre à vos identifiants locaux (par défaut : `root/root` sur le port `8889`).

### 3. Exécution du Pipeline

```bash
python etl/main.py

```

Le script gère automatiquement :

* Le nettoyage des doublons par code-barres.
* La normalisation des pays et marques (casse, accents) pour éviter les erreurs d'intégrité.
* Le calcul du score de complétude des données.
* L'optimisation de la mémoire pour l'ingestion massive.

## 📈 Analyse et KPI

La vue **`reporting_kpi`** centralise les 24 indicateurs clés. Vous pouvez la connecter directement à Tableau pour visualiser :

* Le Top 20 des produits par marque et par pays 
* L'évolution hebdomadaire de la complétude des données.
* La répartition géographique des anomalies nutritionnelles...

## 📝 Choix d'Architecture 

* **Robustesse :** Désactivation temporaire des `UNIQUE_CHECKS` pour absorber les caractères spéciaux internationaux.
* **SCD Type 1 :** Mise à jour des produits avec le drapeau `is_current` pour assurer l'unicité dans le reporting.
* **Performance :** Utilisation de `batchsize` réduit (500) pour respecter les contraintes d'espace disque (OS errno 28).




