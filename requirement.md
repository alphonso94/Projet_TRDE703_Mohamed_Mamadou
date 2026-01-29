
# 📄 Spécifications des Besoins (Requirements)

## 1. Objectif du Projet

L'objectif est de construire un **Datamart "OpenFoodFacts Nutrition & Qualité"** fonctionnel et reproductible. Ce système doit collecter des données massives depuis un Datalake pour alimenter un entrepôt de données relationnel structuré en étoile.

## 2. Besoins Fonctionnels (KPI métiers)

Le système doit permettre de répondre aux questions analytiques suivantes:

* 
**Analyse des Marques** : Identifier le Top 10 des marques selon la proportion de produits Nutri-Score A/B.


* 
**Qualité Nutritionnelle** : Classer les marques par "qualité nutritionnelle moyenne" via la médiane des taux de sucres et de sel.


* 
**Distribution Géographique** : Produire une Heatmap par pays et catégorie sur la moyenne du taux de sucre.


* 
**Santé Publique** : Lister les catégories de produits contenant le plus grand nombre moyen d'additifs.


* 
**Suivi de la Qualité** : Suivre l'évolution hebdomadaire de la complétude des nutriments.



## 3. Besoins Techniques (ETL Spark)

Le pipeline d'intégration doit respecter les contraintes suivantes :

* 
**Langage et Framework** : Utilisation exclusive d'Apache Spark via PySpark (Python) ou Java.


* 
**Lecture des Données** : Ingestion de fichiers JSONL ou CSV avec définition d'un **schéma explicite** (interdiction de l'inférence automatique).


* **Architecture Médaillon** :
* 
**Bronze** : Extraction brute des champs clés (code, nutriments, scores, tags).


* 
**Silver** : Normalisation des types/unités, dédoublonnage par code-barres en conservant le `last_modified_t` le plus récent, et résolution multilingue (FR prioritaire).


* 
**Gold** : Chargement dans un modèle en étoile (Fact + Dimensions).




* 
**Historisation** : Mise en œuvre du **SCD Type 2** pour la dimension produit (gestion de `effective_from`, `effective_to` et `is_current`).


* 
**Cible** : Chargement dans une base **MySQL 8** via JDBC avec des stratégies d'upsert maîtrisées.



## 4. Exigences de Qualité de Données

Chaque exécution du pipeline doit produire des métriques de qualité:

* 
**Unicité** : Un code-barres doit correspondre à un seul produit actif.


* 
**Complétude Pondérée** : Calcul d'un score basé sur la présence du nom du produit, de la marque et des nutriments clés.


* 
**Contrôle des Bornes** : Les valeurs nutritionnelles pour 100g doivent être comprises entre 0 et 100.


* 
**Harmonisation** : Conversion systématique kcal/kJ, g/mg et sel/sodium ().



## 5. Livrables Attendus

* 
**Dépôt Git** structuré contenant les répertoires `/etl`, `/sql`, `/docs`, `/tests` et `/conf`.


* 
**Note d'Architecture** justifiant les choix techniques et les schémas.


* 
**Cahier de Qualité** recensant les règles, le coverage et le log des anomalies.


* 
**Jeu de requêtes SQL** analytiques prêtes à l'emploi.



---

