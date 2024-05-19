-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: May 19, 2024 at 03:05 PM
-- Server version: 10.6.16-MariaDB-cll-lve
-- PHP Version: 8.1.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fleet_db`
--
CREATE DATABASE IF NOT EXISTS `fleet_db` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `fleet_db`;

-- --------------------------------------------------------

--
-- Table structure for table `entry`
--

CREATE TABLE `entry` (
  `id` int(11) NOT NULL,
  `van` varchar(2) NOT NULL,
  `body` varchar(200) NOT NULL,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `entry`
--

INSERT INTO `entry` (`id`, `van`, `body`, `timestamp`) VALUES
(814, '28', '@Crash Champions - Accident ', '2024-01-17 13:17:04'),
(1006, '21', 'G21 Rear view back up camera is off and on. Dash camera half screen is black/broken. Sliding door weather strip', '2024-04-20 03:06:18'),
(1065, '1', 'Driver door fix at Eli soon. ', '2024-04-22 12:43:53'),
(1070, '6', 'G6 is starting to stall when starting after each stop. Advised to leave it running for the day. ', '2024-04-23 18:30:39'),
(1079, '4', 'G4 - Ignition cylinder @ Castle Naperville Dealership', '2024-04-26 21:29:10'),
(1086, '9', 'G9 - Rear bumper is loose not the rear step.', '2024-04-30 20:51:00'),
(1087, '17', 'G17 - Check engine light, transmission @ Castle Naperville Dealership', '2024-05-01 21:24:11'),
(1092, '1', 'left tail light is out', '2024-05-06 01:05:35'),
(1098, '19', 'G19 - Check engine light on, vibrations in axle and window will not go up @ Castle Naperville Dealership', '2024-05-10 19:59:35'),
(1099, '3', 'G3 driver side hazard lights do not work @ Castle Naperville Dealership', '2024-05-15 13:23:00'),
(1101, '23', 'G23 side step loose', '2024-05-10 16:06:14'),
(1104, '16', 'G16 was having trouble starting. Driver left it running for the last 40 stops. AC is not working.', '2024-05-11 23:44:48'),
(1105, '11', 'G11 steering wheel shakes past 60. The ABS & ESC lights are on.', '2024-05-12 00:18:17'),
(1106, '22', 'G22 AC is not working.', '2024-05-13 01:02:22'),
(1107, '56', 'G56 shows a triangle symbol with an exclamation point in it lit up and says ESC is off.', '2024-05-13 01:07:36'),
(1108, '20', 'Dr window wont go down', '2024-05-13 15:41:07'),
(1111, '54', 'maintenance lights check. Front passenger tire needs air.', '2024-05-16 01:37:15'),
(1112, '5', 'G5 - Van kept stalling today per Daniel T. ', '2024-05-15 18:47:12'),
(1113, '5', 'G5 - Driver side turn signal is out.', '2024-05-15 18:47:32'),
(1114, '54', 'G54 -Front passenger tire is low 38psi. ', '2024-05-15 20:52:22'),
(1115, '52', 'Pump gas into 52 and 58', '2024-05-16 20:15:48'),
(1118, '20', 'check engine light is on. another light that looks like a lightening bolt in between )( is on. at some points the van would not exceed 20 mph. @ Castle Naperville Dealership', '2024-05-17 19:46:53'),
(1119, '5', 'G5 - Driver side seatbelt sticks and is hard to unlock.', '2024-05-17 19:46:23');

-- --------------------------------------------------------

--
-- Table structure for table `note`
--

CREATE TABLE `note` (
  `id` int(11) NOT NULL,
  `body` varchar(200) NOT NULL,
  `timestamp` datetime NOT NULL,
  `color` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `note`
--

INSERT INTO `note` (`id`, `body`, `timestamp`, `color`) VALUES
(10, 'Testing', '2024-04-03 00:49:40', 'white');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `entry`
--
ALTER TABLE `entry`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `note`
--
ALTER TABLE `note`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `entry`
--
ALTER TABLE `entry`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1120;

--
-- AUTO_INCREMENT for table `note`
--
ALTER TABLE `note`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
