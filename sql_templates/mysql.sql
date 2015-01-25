-- phpMyAdmin SQL Dump
-- version 4.2.10
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 25, 2015 at 03:31 PM
-- Server version: 5.6.19-0ubuntu0.14.04.1
-- PHP Version: 5.5.9-1ubuntu4.5

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `popm`
--

-- --------------------------------------------------------

--
-- Table structure for table `exemptions`
--

CREATE TABLE IF NOT EXISTS `exemptions` (
`ID` int(11) NOT NULL,
  `ip` text NOT NULL,
  `whenadded` int(11) NOT NULL,
  `whoadded` text NOT NULL,
  `lastmodified` int(11) NOT NULL,
  `expires` int(11) NOT NULL,
  `wholast` text NOT NULL,
  `perma` tinyint(1) NOT NULL,
  `reason` text NOT NULL,
  `active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `settings`
--

CREATE TABLE IF NOT EXISTS `settings` (
  `enable_dnsbl` tinyint(1) NOT NULL,
  `enable_http` tinyint(1) NOT NULL,
  `enable_socks` tinyint(1) NOT NULL,
  `access_die` int(11) NOT NULL,
  `access_set` int(11) NOT NULL,
  `access_say` int(11) NOT NULL,
  `access_emote` int(11) NOT NULL,
  `access_joinpart` int(11) NOT NULL,
  `view_exempts` int(11) NOT NULL,
  `modify_exempts` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `settings`
--

INSERT INTO `settings` (`enable_dnsbl`, `enable_http`, `enable_socks`, `access_die`, `access_set`, `access_say`, `access_emote`, `access_joinpart`, `view_exempts`, `modify_exempts`) VALUES
(1, 1, 1, 1000, 1000, 1000, 1000, 1000, 1000, 1000);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
`ID` int(11) NOT NULL,
  `admin` text NOT NULL,
  `added` int(11) NOT NULL,
  `access` int(11) NOT NULL,
  `bywho` text NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`ID`, `admin`, `added`, `access`, `bywho`) VALUES
(1, 'your_username_here', 0, 1000, 'any_username');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `exemptions`
--
ALTER TABLE `exemptions`
 ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
 ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `exemptions`
--
ALTER TABLE `exemptions`
MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=2;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
