-- phpMyAdmin SQL Dump
-- version 4.5.2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jun 26, 2018 at 03:00 AM
-- Server version: 10.1.13-MariaDB
-- PHP Version: 5.6.23

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Claribot`
--

-- --------------------------------------------------------

--
-- Table structure for table `blacklist_channels`
--

CREATE TABLE `blacklist_channels` (
  `server_id` bigint(32) NOT NULL,
  `channel_id` bigint(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `blacklist_commands`
--

CREATE TABLE `blacklist_commands` (
  `server_id` bigint(32) NOT NULL,
  `command` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `blacklist_users`
--

CREATE TABLE `blacklist_users` (
  `server_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `bot_data`
--

CREATE TABLE `bot_data` (
  `var_name` mediumtext COLLATE utf8mb4_bin NOT NULL,
  `value` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

--
-- Dumping data for table `bot_data`
--

INSERT INTO `bot_data` (`var_name`, `value`) VALUES
('playing', 'end my life');

-- --------------------------------------------------------

--
-- Table structure for table `personality`
--

CREATE TABLE `personality` (
  `server_id` bigint(32) NOT NULL,
  `personality` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

--
-- Dumping data for table `personality`
--


-- --------------------------------------------------------

--
-- Table structure for table `points`
--

CREATE TABLE `points` (
  `server_id` bigint(32) NOT NULL,
  `user_id` bigint(32) NOT NULL,
  `points` bigint(32) NOT NULL,
  `timestamp` bigint(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

--
-- Dumping data for table `points`
--

-- --------------------------------------------------------

--
-- Table structure for table `prefix`
--

CREATE TABLE `prefix` (
  `server_id` bigint(32) NOT NULL,
  `prefix` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

--
-- Dumping data for table `prefix`
--


-- --------------------------------------------------------

--
-- Table structure for table `server_options`
--

CREATE TABLE `server_options` (
  `server_id` bigint(32) NOT NULL,
  `var` mediumtext COLLATE utf8mb4_bin NOT NULL,
  `value` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

--
-- Dumping data for table `server_options`
--


-- --------------------------------------------------------

--
-- Table structure for table `special_users`
--

CREATE TABLE `special_users` (
  `user_id` bigint(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `warnings`
--

CREATE TABLE `warnings` (
  `server_id` bigint(32) NOT NULL,
  `user_id` bigint(32) NOT NULL,
  `reason` text COLLATE utf8mb4_bin NOT NULL,
  `warner` bigint(32) NOT NULL,
  `timestamp` bigint(32) NOT NULL,
  `issue_id` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `blacklist_channels`
--
ALTER TABLE `blacklist_channels`
  ADD KEY `server_id` (`server_id`),
  ADD KEY `channel_id` (`channel_id`);

--
-- Indexes for table `blacklist_commands`
--
ALTER TABLE `blacklist_commands`
  ADD KEY `command_blacklist_serverid_index` (`server_id`);

--
-- Indexes for table `blacklist_users`
--
ALTER TABLE `blacklist_users`
  ADD KEY `server_id` (`server_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `personality`
--
ALTER TABLE `personality`
  ADD KEY `server_id` (`server_id`);

--
-- Indexes for table `points`
--
ALTER TABLE `points`
  ADD KEY `server_id` (`server_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `prefix`
--
ALTER TABLE `prefix`
  ADD KEY `server_id` (`server_id`);

--
-- Indexes for table `server_options`
--
ALTER TABLE `server_options`
  ADD KEY `server_id` (`server_id`);

--
-- Indexes for table `special_users`
--
ALTER TABLE `special_users`
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `warnings`
--
ALTER TABLE `warnings`
  ADD KEY `server_id` (`server_id`),
  ADD KEY `user_id` (`user_id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
