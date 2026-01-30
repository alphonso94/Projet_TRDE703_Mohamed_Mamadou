-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost:8889
-- Généré le : ven. 30 jan. 2026 à 20:36
-- Version du serveur : 8.0.40
-- Version de PHP : 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `openfoodfacts_datamart`
--

-- --------------------------------------------------------

--
-- Structure de la table `etl_metrics_logs`
--

CREATE TABLE `etl_metrics_logs` (
  `log_id` int NOT NULL,
  `job_name` varchar(100) DEFAULT NULL,
  `step_name` varchar(100) DEFAULT NULL,
  `input_count` int DEFAULT NULL,
  `output_count` int DEFAULT NULL,
  `rejected_count` int DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `etl_metrics_logs`
--

INSERT INTO `etl_metrics_logs` (`log_id`, `job_name`, `step_name`, `input_count`, `output_count`, `rejected_count`, `timestamp`) VALUES
(1, 'OFF_StarSchema_Final_Production', '1_SILVER_CLEANING', 1000, 999, 1, '2026-01-29 22:26:25'),
(2, 'OFF_StarSchema_Prod', '1_SILVER_CLEANING', 1000, 999, 1, '2026-01-29 22:50:33'),
(3, 'OFF_StarSchema_Prod', '2_DIM_TIME', 999, 249, 750, '2026-01-29 22:50:35'),
(4, 'OFF_StarSchema_Prod', '3_DIM_BRAND', 999, 414, 585, '2026-01-29 22:50:36'),
(5, 'OFF_StarSchema_Prod', '4_DIM_CATEGORY', 999, 202, 797, '2026-01-29 22:50:38'),
(6, 'OFF_StarSchema_Prod', '5_DIM_COUNTRY', 999, 98, 901, '2026-01-29 22:50:39'),
(7, 'OFF_StarSchema_Prod', '6_DIM_PRODUCT', 999, 999, 0, '2026-01-29 22:50:42'),
(8, 'OFF_StarSchema_Prod', '7_FACT_NUTRITION', 999, 999, 0, '2026-01-29 22:50:45'),
(9, 'OFF_StarSchema_Prod', '1_SILVER_CLEANING', 1000, 999, 1, '2026-01-29 23:55:08'),
(10, 'OFF_StarSchema_Prod', '2_DIM_TIME', 999, 249, 750, '2026-01-29 23:55:10'),
(11, 'OFF_StarSchema_Prod', '3_DIM_BRAND', 999, 414, 585, '2026-01-29 23:55:11'),
(12, 'OFF_StarSchema_Prod', '4_DIM_CATEGORY', 999, 202, 797, '2026-01-29 23:55:12'),
(13, 'OFF_StarSchema_Prod', '5_DIM_COUNTRY', 999, 98, 901, '2026-01-29 23:55:13'),
(14, 'OFF_StarSchema_Prod', '6_DIM_PRODUCT', 999, 999, 0, '2026-01-29 23:55:16'),
(15, 'OFF_StarSchema_Prod', '7_FACT_NUTRITION', 999, 999, 0, '2026-01-29 23:55:19'),
(16, 'OFF_StarSchema_Prod', '1_SILVER_CLEANING', 4192502, 4186676, 5826, '2026-01-30 00:04:38'),
(17, 'OFF_StarSchema_Prod', '2_DIM_TIME', 4186676, 3726, 4182950, '2026-01-30 00:05:24'),
(18, 'OFF_StarSchema_Prod', '1_SILVER_CLEANING', 4192502, 4186676, 5826, '2026-01-30 10:00:51'),
(19, 'OFF_StarSchema_Prod', '2_DIM_TIME', 4186676, 3726, 4182950, '2026-01-30 10:02:01'),
(20, 'OFF_StarSchema_Prod', '1_SILVER_CLEANING', 4192502, 4186676, 5826, '2026-01-30 10:10:49'),
(21, 'OFF_StarSchema_Prod', '3_DIM_BRAND', 4186676, 358725, 3827951, '2026-01-30 10:47:12'),
(22, 'OFF_StarSchema_Prod', '1_SILVER_CLEANING', 10000, 9999, 1, '2026-01-30 14:42:12'),
(23, 'OFF_StarSchema_Prod', '1_SILVER_CLEANING', 4192502, 499992, 3692510, '2026-01-30 14:49:40'),
(24, 'OFF_StarSchema_Prod', '1_SILVER_CLEANING', 4192502, 499992, 3692510, '2026-01-30 14:59:33'),
(25, 'OFF_StarSchema_Prod', '5_DIM_COUNTRY', 499992, 839, 499153, '2026-01-30 14:59:56');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `etl_metrics_logs`
--
ALTER TABLE `etl_metrics_logs`
  ADD PRIMARY KEY (`log_id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `etl_metrics_logs`
--
ALTER TABLE `etl_metrics_logs`
  MODIFY `log_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
