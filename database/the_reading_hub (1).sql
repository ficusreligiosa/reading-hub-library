-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 11, 2026 at 07:14 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `the_reading_hub`
--

-- --------------------------------------------------------

--
-- Table structure for table `all_user_data`
--

CREATE TABLE `all_user_data` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('Admin','Owner','User') NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `all_user_data`
--

INSERT INTO `all_user_data` (`id`, `username`, `password`, `role`, `created_at`) VALUES
(1, 'Palak321', 'Palak@321', 'Admin', '2025-09-28 08:12:12'),
(2, '7', 'Man2002', 'User', '2025-09-29 03:23:49'),
(3, '8', 'Man2002', 'User', '2025-09-29 03:32:00'),
(4, '9', 'Man2025', 'User', '2025-10-07 06:00:40'),
(5, '10', 'Man2025', 'User', '2025-10-07 06:21:13'),
(6, '11', 'Man2025', 'User', '2025-10-07 06:22:28'),
(7, '12', 'Man2025', 'User', '2025-10-07 06:28:36'),
(8, '13', 'Man2025', 'User', '2025-10-07 06:30:12'),
(9, '14', 'Man2025', 'User', '2025-10-07 06:31:49'),
(10, '15', 'Man2025', 'User', '2025-10-07 07:21:13'),
(11, '16', 'Yas2007', 'User', '2025-10-10 04:32:33'),
(12, '17', 'Ash2005', 'User', '2025-10-24 09:14:47'),
(13, '18', 'Ren2015', 'User', '2025-10-25 05:12:15'),
(14, '19', 'Rit2001', 'User', '2025-10-27 07:57:32'),
(15, '20', 'Vik2000', 'User', '2025-10-27 08:00:17'),
(16, '21', 'Ok2005', 'User', '2025-10-27 14:31:16'),
(17, '22', 'Hjg2002', 'User', '2025-10-27 15:30:39'),
(18, '23', 'Fhd2003', 'User', '2025-10-27 15:34:07'),
(19, '24', 'Hum2001', 'User', '2025-10-28 04:02:00'),
(20, '25', 'Raw1995', 'User', '2025-10-28 05:23:02'),
(21, '26', 'Sun2000', 'User', '2025-10-28 05:30:56'),
(22, '27', 'Sha1950', 'User', '2025-10-28 05:43:20');

-- --------------------------------------------------------

--
-- Table structure for table `books`
--

CREATE TABLE `books` (
  `book_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `publication` varchar(255) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `price` int(255) NOT NULL,
  `shelf_id` int(11) DEFAULT NULL,
  `copies` int(11) DEFAULT 1,
  `staff_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `books`
--

INSERT INTO `books` (`book_id`, `title`, `author`, `publication`, `year`, `price`, `shelf_id`, `copies`, `staff_id`, `created_at`) VALUES
(1, 'Gunaahon Ka Devta', 'Dharamvir Bharati', 'Bharati Bhandar', 1948, 450, 1, 50, 1, '2025-09-28 08:56:42'),
(2, 'Chacha Chaudhary and the Diamond Thief', 'Pran Kumar Sharma', 'Diamond Comics', 2017, 0, 6, 5, 1, '2025-09-28 09:30:02'),
(4, 'Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', 'Bloomsburry', 1995, 750, 6, 8, 1, '2025-10-10 02:40:21'),
(6, 'mr', 'ok', 'ok', 2004, 1997, 3, 100, 1, '2025-10-22 09:04:55'),
(9, 'My Bio Part 3', 'Me', 'Kmn', 2004, 1500, 6, 50, 1, '2025-10-24 08:47:59'),
(10, 'Kuch', 'Bhi', 'Kar', 2002, 150, 5, 14, 1, '2025-10-25 05:02:27');

-- --------------------------------------------------------

--
-- Table structure for table `book_genres`
--

CREATE TABLE `book_genres` (
  `book_id` int(11) NOT NULL,
  `genre_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `book_genres`
--

INSERT INTO `book_genres` (`book_id`, `genre_id`) VALUES
(1, 6),
(1, 21),
(2, 5),
(2, 22),
(2, 23),
(4, 4),
(4, 9),
(4, 22),
(6, 23),
(9, 11),
(10, 23);

-- --------------------------------------------------------

--
-- Table structure for table `book_returned_data`
--

CREATE TABLE `book_returned_data` (
  `return_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `book_id` int(11) NOT NULL,
  `return_date` date NOT NULL,
  `status` enum('Returned','Lost','Damaged') DEFAULT 'Returned',
  `fine_amount` decimal(10,2) DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `book_returned_data`
--

INSERT INTO `book_returned_data` (`return_id`, `user_id`, `book_id`, `return_date`, `status`, `fine_amount`, `created_at`) VALUES
(1, 3, 1, '2025-10-15', 'Returned', 270.00, '2025-10-06 09:17:04'),
(2, 2, 1, '2025-10-07', 'Returned', 60.00, '2025-10-07 10:16:25'),
(3, 4, 1, '2025-10-22', 'Returned', 255.00, '2025-10-22 10:30:46'),
(4, 4, 2, '2025-10-24', 'Returned', 30.00, '2025-10-24 11:49:16');

-- --------------------------------------------------------

--
-- Table structure for table `borrowers`
--

CREATE TABLE `borrowers` (
  `borrow_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `book_id` int(11) NOT NULL,
  `borrow_date` date NOT NULL,
  `due_date` date NOT NULL,
  `return_date` date DEFAULT NULL,
  `status` enum('Borrowed','Returned','Overdue') DEFAULT 'Borrowed',
  `amount` decimal(10,2) DEFAULT 0.00,
  `fine_amount` decimal(10,2) DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `borrowers`
--

INSERT INTO `borrowers` (`borrow_id`, `user_id`, `book_id`, `borrow_date`, `due_date`, `return_date`, `status`, `amount`, `fine_amount`, `created_at`) VALUES
(1, 3, 1, '2025-09-28', '2025-10-01', '2025-10-15', 'Returned', 270.00, 0.00, '2025-09-28 16:51:37'),
(2, 2, 1, '2025-10-03', '2025-10-04', '2025-10-07', 'Returned', 60.00, 0.00, '2025-10-06 09:50:16'),
(4, 4, 1, '2025-10-05', '2025-10-06', '2025-10-22', 'Returned', 255.00, 0.00, '2025-10-07 04:26:21'),
(5, 6, 1, '2025-10-07', '2025-10-08', NULL, 'Overdue', 15.00, 0.00, '2025-10-07 04:54:58'),
(6, 7, 1, '2025-10-07', '2025-10-08', NULL, 'Overdue', 15.00, 0.00, '2025-10-07 04:55:21'),
(7, 4, 2, '2025-10-22', '2025-10-23', '2025-10-24', 'Returned', 30.00, 0.00, '2025-10-22 10:38:10'),
(8, 4, 4, '2025-10-22', '2025-10-23', NULL, 'Overdue', 15.00, 0.00, '2025-10-22 10:38:50'),
(9, 5, 4, '2025-10-24', '2025-10-25', NULL, 'Overdue', 15.00, 0.00, '2025-10-24 11:24:44'),
(10, 11, 2, '2025-10-25', '2025-10-26', NULL, 'Overdue', 15.00, 0.00, '2025-10-25 07:54:51'),
(11, 11, 1, '2025-10-25', '2025-10-26', NULL, 'Overdue', 15.00, 0.00, '2025-10-25 07:54:51'),
(12, 11, 4, '2025-10-25', '2025-10-26', NULL, 'Overdue', 15.00, 0.00, '2025-10-25 07:54:51'),
(13, 11, 10, '2025-10-25', '2025-10-26', NULL, 'Overdue', 15.00, 0.00, '2025-10-25 07:54:51');

-- --------------------------------------------------------

--
-- Table structure for table `expenses`
--

CREATE TABLE `expenses` (
  `expense_id` int(11) NOT NULL,
  `staff_id` int(11) NOT NULL,
  `expense_name` varchar(255) NOT NULL,
  `date` date NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `photo_path` varchar(500) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `genres`
--

CREATE TABLE `genres` (
  `genre_id` int(11) NOT NULL,
  `genre_name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `genres`
--

INSERT INTO `genres` (`genre_id`, `genre_name`, `description`, `created_at`) VALUES
(1, 'Fiction', NULL, '2025-09-28 08:40:47'),
(2, 'Non-Fiction', NULL, '2025-09-28 08:40:47'),
(3, 'Science Fiction', NULL, '2025-09-28 08:40:47'),
(4, 'Fantasy', NULL, '2025-09-28 08:40:47'),
(5, 'Mystery', NULL, '2025-09-28 08:40:47'),
(6, 'Romance', NULL, '2025-09-28 08:40:47'),
(7, 'Thriller', NULL, '2025-09-28 08:40:47'),
(8, 'Horror', NULL, '2025-09-28 08:40:47'),
(9, 'Adventure', NULL, '2025-09-28 08:40:47'),
(10, 'Drama', NULL, '2025-09-28 08:40:47'),
(11, 'Biography', NULL, '2025-09-28 08:40:47'),
(12, 'History', NULL, '2025-09-28 08:40:47'),
(13, 'Science', NULL, '2025-09-28 08:40:47'),
(14, 'Technology', NULL, '2025-09-28 08:40:47'),
(15, 'Business', NULL, '2025-09-28 08:40:47'),
(16, 'Self-Help', NULL, '2025-09-28 08:40:47'),
(17, 'Children', NULL, '2025-09-28 08:40:47'),
(18, 'Young Adult', NULL, '2025-09-28 08:40:47'),
(19, 'Poetry', NULL, '2025-09-28 08:40:47'),
(20, 'Art', NULL, '2025-09-28 08:40:47'),
(21, 'Social Fiction', NULL, '2025-09-28 08:54:55'),
(22, 'Children\'s Comic', NULL, '2025-09-28 09:28:43'),
(23, 'Action', NULL, '2025-09-28 09:28:49'),
(24, 'Comedy', NULL, '2025-10-06 08:44:31');

-- --------------------------------------------------------

--
-- Table structure for table `members`
--

CREATE TABLE `members` (
  `member_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `membership_type` enum('Student','Faculty','Staff','External') NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `photo_path` varchar(500) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `members`
--

INSERT INTO `members` (`member_id`, `name`, `phone`, `address`, `membership_type`, `email`, `date_of_birth`, `photo_path`, `created_at`) VALUES
(1, 'Manav Singh', '9336975413', '582/10, Satyalok Colony, Lucknow, Uttar Pradesh - 226023', 'External', 'manavsingh89777@gmail.com', NULL, 'static/uploads/profile.jpg', '2025-09-28 12:00:04'),
(2, 'Manav Singh', '9336975413', '582/10, Satyalok Colony, Lucknow, Uttar Pradesh - 226023', 'External', 'manavsingh89777@gmail.com', NULL, 'static/uploads/profile.jpg', '2025-09-28 12:01:11'),
(3, 'Mansi Singh', '9335451558', '582/10, Satyalok Colony, Lucknow, Uttar Pradesh - 226023', 'Student', 'bscmansi@gmail.com', NULL, 'static/uploads/beautifultundin14.jpg', '2025-09-28 12:16:01'),
(4, 'Yashmit Singh', '8081951311', '582/10, Satyalok Colony, Lucknow, Uttar Pradesh - 226023', 'Student', 'yashmitsingh89777@gmail.com', NULL, 'static/uploads/xy57q6g9cb1c1.jpg', '2025-09-28 12:24:33'),
(5, 'Manav Singh', '9336975413', '582/10, Satyalok Colony, Lucknow, Uttar Pradesh - 226023', 'Student', 'manavsingh89777@gmail.com', NULL, 'static/uploads/profile.jpg', '2025-09-28 12:29:39'),
(6, 'Manav Singh', '9336975413', '582/10, Satyalok Colony, Lucknow, Uttar Pradesh - 226023', 'Student', 'manavsingh89777@gmail.com', NULL, 'static/uploads/profile.jpg', '2025-09-28 12:31:20'),
(7, 'Mansi Singh', '9335451558', '582/10, Satyalok colony, Lucknow, Uttar Pradesh - 226023', 'Student', 'bscmansi@gmail.com', '2002-06-29', 'static/uploads/beautifultundin14.jpg', '2025-09-29 03:23:49'),
(8, 'Mansi Singh', '9335451558', '582/10, Satyalok Colony, Lucknow, Uttar Pradesh - 226023', 'Student', 'bscmansi@gmail.com', '2002-06-29', 'static/uploads/tundin.jpg', '2025-09-29 03:32:00'),
(9, 'Manav Singh', '9336975413', '582/10, Satyalok colony, Lucknow, Uttar Pradesh - 226023', 'External', 'manavsingh89777@gmail.com', '2025-10-07', 'static/uploads/Manav_profile_picture.png', '2025-10-07 06:00:40'),
(10, 'Manav Singh', '8381870608', '582/10, Satyalok colony, Lucknow, Uttar Pradesh - 226023', 'External', 'manavsingh8977@gmail.com', '2025-10-07', 'uploads/users/20251007115113_Manav_profile_picture.png', '2025-10-07 06:21:13'),
(11, 'Manav Singh', '8381870609', '582/10, Satyalok colony, Lucknow, Uttar Pradesh - 226023', 'External', 'manavsingh897@gmail.com', '2025-10-07', 'uploads/users/20251007115228_Manav_profile_picture.png', '2025-10-07 06:22:28'),
(12, 'Manav Singh', '9336975412', '582/10, Satyalok colony, Lucknow, Uttar Pradesh - 226023', 'External', 'hi@gmail.com', '2025-10-07', 'uploads/users/20251007115836_Manav_profile_picture.png', '2025-10-07 06:28:36'),
(13, 'Manav Singh', '9336975411', '582/10, Satyalok colony, Lucknow, UP - 226023', 'External', 'my@gmail.com', '2025-10-07', 'uploads/users/20251007120012_Manav_profile_picture.png', '2025-10-07 06:30:12'),
(14, 'Manav Singh', '9336975415', '582/10, Satyalok colony, Lucknow, UP - 226023', 'External', 'manavsinghh@gmail.com', '2025-10-07', 'uploads/users/20251007120148_Manav_profile_picture.png', '2025-10-07 06:31:49'),
(15, 'Manav Singh', '9336975410', '582/10, Satyalok colony, Lucknow, Uttar Pradesh - 226023', 'External', 'manavsinghu@gmail.com', '2025-10-07', 'uploads/users/20251007125113_Manav_profile_picture.png', '2025-10-07 07:21:13'),
(16, 'Yashmit singh', '8081951310', '582/10, Satyalok colony, Lucknow, Uttar Pradesh - 226023', 'Student', 'yashmit@gmail.com', '2007-09-07', 'uploads/users/20251010100233_ritikphoto.jpg', '2025-10-10 04:32:33'),
(17, 'Ash', '9698978975', '1, Pakri Pul, Lucknow, Up - 226023', 'Student', 'ash@gmail.com', '2005-12-13', 'uploads/users/20251024144447_ritikphoto.jpg', '2025-10-24 09:14:47'),
(18, 'Renu', '9656589876', '1, Local, Lucknow, Uttar Pradesh - 226023', 'Student', 'renu@gmail.com', '2015-10-18', 'uploads/users/20251025104215_sorcerer-stone-childrens-tenth-anniversary-edition.jpg', '2025-10-25 05:12:15'),
(19, 'Ritik Dwivedi', '7390022913', '1, Ashiyana, Lucknow, Uttar Pradesh - 226023', 'External', 'ritik.msi55@gmail.com', '2001-08-08', 'uploads/users/20251027132731_ritikphoto.jpg', '2025-10-27 07:57:31'),
(20, 'Vikas', '9658746321', '4, Sgf, Sf, Sf - 226023', 'External', 'a@gmail.com', '2000-02-20', 'uploads/users/20251027133017_Manav__LearnTrail_Certificate.png', '2025-10-27 08:00:17'),
(21, 'Ok', '5489785464', '1, Fd, Fgfc, Gch - 226023', 'External', 'manavsingh@gmail.com', '2005-08-26', 'uploads/users/20251027200116_Manav__LearnTrail_Certificate.png', '2025-10-27 14:31:16'),
(22, 'Hjg', '5164547897', '5, Gfd, Fgdf, Vfdfg - 226023', 'External', 'sads@gmail.com', '2002-10-15', 'uploads/20251027210039_sorcerer-stone-childrens-tenth-anniversary-edition.jpg', '2025-10-27 15:30:39'),
(23, 'Fhd', '5456487897', '55, Ghdf, Hgc, Hg - 226023', 'External', 'sda@gmail.com', '2003-02-12', 'uploads/20251027210407_sorcerer-stone-childrens-tenth-anniversary-edition.jpg', '2025-10-27 15:34:07'),
(24, 'Human', '1234567897', '5, Bndsf, Jxcbgk, Hjb - 226023', 'External', 'human@gmail.com', '2001-01-01', 'uploads/20251028093200_sorcerer-stone-childrens-tenth-anniversary-edition.jpg', '2025-10-28 04:02:00'),
(25, 'Rawal Singh', '8318608066', '5, Mahnaura, Unnao, Uttar Pradesh - 228009', 'External', 'rawal@gmail.com', '1995-08-08', 'uploads/20251028105302_1495efda-9a2b-4f49-ba18-b29845120c6f.jpeg', '2025-10-28 05:23:02'),
(26, 'Sun Wukong', '9865645465', '1, Himalaya, Himalaya, Himalaya - 111111', 'External', 'wukong@gmail.com', '2000-01-01', 'uploads/20251028110055_sunwukong.jpg', '2025-10-28 05:30:55'),
(27, 'Shadow Ranger Aka Doggie', '9878456103', '100, Unknown, Unknown, Unknown - 100100', 'External', 'ads@gmail.com', '1950-01-01', 'uploads/20251028111320_doggie.jpg', '2025-10-28 05:43:20');

-- --------------------------------------------------------

--
-- Table structure for table `shelves`
--

CREATE TABLE `shelves` (
  `shelf_id` int(11) NOT NULL,
  `shelf_code` varchar(20) NOT NULL,
  `section` varchar(50) NOT NULL,
  `description` text DEFAULT NULL,
  `floor_level` int(11) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `shelves`
--

INSERT INTO `shelves` (`shelf_id`, `shelf_code`, `section`, `description`, `floor_level`, `created_at`) VALUES
(1, 'FIC-A1', 'Fiction', 'Fiction Section - Row A, Shelf 1', 1, '2025-09-28 09:05:10'),
(2, 'FIC-A2', 'Fiction', 'Fiction Section - Row A, Shelf 2', 1, '2025-09-28 09:05:10'),
(3, 'FIC-B1', 'Fiction', 'Fiction Section - Row B, Shelf 1', 1, '2025-09-28 09:05:10'),
(4, 'SCI-A1', 'Science', 'Science Section - Row A, Shelf 1', 1, '2025-09-28 09:05:10'),
(5, 'REF-A1', 'Reference', 'Reference Section - Row A, Shelf 1', 1, '2025-09-28 09:05:10'),
(6, 'CHILD-A1', 'Children', 'Children Section - Row A, Shelf 1', 1, '2025-09-28 09:05:10');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `all_user_data`
--
ALTER TABLE `all_user_data`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `books`
--
ALTER TABLE `books`
  ADD PRIMARY KEY (`book_id`),
  ADD KEY `fk_books_staff` (`staff_id`),
  ADD KEY `idx_books_copies` (`copies`),
  ADD KEY `fk_books_shelf` (`shelf_id`);

--
-- Indexes for table `book_genres`
--
ALTER TABLE `book_genres`
  ADD PRIMARY KEY (`book_id`,`genre_id`),
  ADD KEY `genre_id` (`genre_id`);

--
-- Indexes for table `book_returned_data`
--
ALTER TABLE `book_returned_data`
  ADD PRIMARY KEY (`return_id`),
  ADD KEY `idx_return_user_id` (`user_id`),
  ADD KEY `idx_return_book_id` (`book_id`);

--
-- Indexes for table `borrowers`
--
ALTER TABLE `borrowers`
  ADD PRIMARY KEY (`borrow_id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_book_id` (`book_id`),
  ADD KEY `idx_borrowers_status` (`status`),
  ADD KEY `idx_borrowers_due_date` (`due_date`);

--
-- Indexes for table `expenses`
--
ALTER TABLE `expenses`
  ADD PRIMARY KEY (`expense_id`),
  ADD KEY `idx_staff_id` (`staff_id`);

--
-- Indexes for table `genres`
--
ALTER TABLE `genres`
  ADD PRIMARY KEY (`genre_id`),
  ADD UNIQUE KEY `genre_name` (`genre_name`);

--
-- Indexes for table `members`
--
ALTER TABLE `members`
  ADD PRIMARY KEY (`member_id`);

--
-- Indexes for table `shelves`
--
ALTER TABLE `shelves`
  ADD PRIMARY KEY (`shelf_id`),
  ADD UNIQUE KEY `shelf_code` (`shelf_code`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `all_user_data`
--
ALTER TABLE `all_user_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `books`
--
ALTER TABLE `books`
  MODIFY `book_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `book_returned_data`
--
ALTER TABLE `book_returned_data`
  MODIFY `return_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `borrowers`
--
ALTER TABLE `borrowers`
  MODIFY `borrow_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `expenses`
--
ALTER TABLE `expenses`
  MODIFY `expense_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `genres`
--
ALTER TABLE `genres`
  MODIFY `genre_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `members`
--
ALTER TABLE `members`
  MODIFY `member_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `shelves`
--
ALTER TABLE `shelves`
  MODIFY `shelf_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `books`
--
ALTER TABLE `books`
  ADD CONSTRAINT `books_ibfk_1` FOREIGN KEY (`staff_id`) REFERENCES `all_user_data` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_books_shelf` FOREIGN KEY (`shelf_id`) REFERENCES `shelves` (`shelf_id`),
  ADD CONSTRAINT `fk_books_staff` FOREIGN KEY (`staff_id`) REFERENCES `all_user_data` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `book_genres`
--
ALTER TABLE `book_genres`
  ADD CONSTRAINT `book_genres_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `book_genres_ibfk_2` FOREIGN KEY (`genre_id`) REFERENCES `genres` (`genre_id`) ON DELETE CASCADE;

--
-- Constraints for table `book_returned_data`
--
ALTER TABLE `book_returned_data`
  ADD CONSTRAINT `book_returned_data_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `members` (`member_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `book_returned_data_ibfk_2` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`) ON DELETE CASCADE;

--
-- Constraints for table `borrowers`
--
ALTER TABLE `borrowers`
  ADD CONSTRAINT `borrowers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `members` (`member_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `borrowers_ibfk_2` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`) ON DELETE CASCADE;

--
-- Constraints for table `expenses`
--
ALTER TABLE `expenses`
  ADD CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`staff_id`) REFERENCES `all_user_data` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
