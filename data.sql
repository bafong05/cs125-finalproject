USE youth_group;

-- GUARDIANS (15)
INSERT INTO Guardian VALUES
(1, 'Laura', 'Mitchell', '555-1111', 'laura.mitchell@example.com'),
(2, 'James', 'Mitchell', '555-2222', 'james.mitchell@example.com'),
(3, 'Sophie', 'Young', '555-3333', 'sophie.young@example.com'),
(4, 'Daniel', 'Young', '555-4444', 'daniel.young@example.com'),
(5, 'Karen', 'Lopez', '555-5555', 'karen.lopez@example.com'),
(6, 'Tina', 'Johnson', '555-6666', 'tina.johnson@example.com'),
(7, 'Marcus', 'Johnson', '555-7777', 'marcus.johnson@example.com'),
(8, 'Amy', 'Wong', '555-8881', 'amy.wong@example.com'),
(9, 'Robert', 'Wong', '555-8882', 'robert.wong@example.com'),
(10, 'Linda', 'Chavez', '555-9081', 'linda.chavez@example.com'),
(11, 'Carlos', 'Chavez', '555-9082', 'carlos.chavez@example.com'),
(12, 'Helen', 'Smith', '555-9090', 'helen.smith@example.com'),
(13, 'George', 'Smith', '555-9091', 'george.smith@example.com'),
(14, 'Olivia', 'Reed', '555-7575', 'olivia.reed@example.com'),
(15, 'Paul', 'Reed', '555-7576', 'paul.reed@example.com');

-- SMALL GROUPS (2)
INSERT INTO SmallGroup VALUES
(101, 'Middle School A'),
(102, 'High School A');

-- EVENTS (6)
INSERT INTO Event VALUES
(1001, 'Winter Retreat', 'Camp Redwood', '2025-01-14', '09:00:00'),
(1002, 'Youth Service Day', 'Community Center', '2025-02-20', '10:00:00'),
(1003, 'Spring Picnic', 'Lakeside Park', '2025-03-12', '12:00:00'),
(1004, 'Fundraising Gala', 'Church Hall', '2025-04-18', '18:00:00'),
(1005, 'Summer Kickoff', 'Beachside', '2025-06:10', '11:00:00'),
(1006, 'Holiday Giving Event', 'Food Bank', '2025-12-05', '09:30:00');

-- VOLUNTEERS (10)
INSERT INTO Volunteer VALUES
(501, 'Amanda', 'Chen', '555-8765', 'amanda.chen@example.com', 1001),
(502, 'Michael', 'Tran', '555-3234', 'michael.tran@example.com', 1002),
(503, 'Rachel', 'Price', '555-4721', 'rachel.price@example.com', 1001),
(504, 'Jonathan', 'Lee', '555-4983', 'jon.lee@example.com', 1003),
(505, 'Mia', 'Patel', '555-2229', 'mia.patel@example.com', 1004),
(506, 'Eric', 'Diaz', '555-1742', 'eric.diaz@example.com', 1005),
(507, 'Hannah', 'Rogers', '555-7412', 'hannah.rogers@example.com', 1005),
(508, 'Peter', 'Nguyen', '555-6422', 'peter.nguyen@example.com', 1006),
(509, 'Nina', 'Morales', '555-9012', 'nina.morales@example.com', 1004),
(510, 'Leo', 'Kim', '555-1029', 'leo.kim@example.com', 1002);

-- STUDENTS (20)
INSERT INTO Student VALUES
(201, 'Emily', 'Mitchell', 13, '555-1234', 'emily.m@example.com', 1, 2, 101),
(202, 'Brian', 'Young', 15, '555-5678', 'brian.y@example.com', 3, 4, 101),
(203, 'Lily', 'Lopez', 14, '555-9999', 'lily.l@example.com', 5, NULL, 102),
(204, 'Jason', 'Johnson', 12, '555-2399', 'jason.j@example.com', 6, 7, 101),
(205, 'Chloe', 'Wong', 13, '555-7812', 'chloe.w@example.com', 8, 9, 101),
(206, 'Sofia', 'Chavez', 14, '555-4521', 'sofia.c@example.com', 10, 11, 102),
(207, 'Evan', 'Smith', 15, '555-2390', 'evan.s@example.com', 12, 13, 102),
(208, 'Noah', 'Reed', 16, '555-4492', 'noah.r@example.com', 14, 15, 102),
(209, 'Maya', 'Mitchell', 11, '555-1313', 'maya.m@example.com', 1, 2, 101),
(210, 'Aiden', 'Young', 12, '555-5656', 'aiden.y@example.com', 3, 4, 101),
(211, 'Bella', 'Lopez', 15, '555-9333', 'bella.l@example.com', 5, NULL, 102),
(212, 'Ethan', 'Johnson', 14, '555-6611', 'ethan.j@example.com', 6, 7, 101),
(213, 'Zoe', 'Wong', 13, '555-8891', 'zoe.w@example.com', 8, 9, 101),
(214, 'Lucas', 'Chavez', 16, '555-9033', 'lucas.c@example.com', 10, 11, 102),
(215, 'Grace', 'Smith', 15, '555-9060', 'grace.s@example.com', 12, 13, 102),
(216, 'Oliver', 'Reed', 14, '555-7481', 'oliver.r@example.com', 14, 15, 102),
(217, 'Natalie', 'Mitchell', 12, '555-1119', 'natalie.m@example.com', 1, 2, 101),
(218, 'Ryan', 'Young', 13, '555-6767', 'ryan.y@example.com', 3, 4, 101),
(219, 'Ella', 'Lopez', 14, '555-9099', 'ella.l@example.com', 5, NULL, 102),
(220, 'Jacob', 'Smith', 15, '555-9500', 'jacob.s@example.com', 12, 13, 102);

-- RELATIONSHIPS (Student ↔ Guardian)
INSERT INTO Relationship VALUES
(201, 1), (201, 2),
(202, 3), (202, 4),
(203, 5),
(204, 6), (204, 7),
(205, 8), (205, 9),
(206, 10), (206, 11),
(207, 12), (207, 13),
(208, 14), (208, 15),
(209, 1), (209, 2),
(210, 3), (210, 4),
(211, 5),
(212, 6), (212, 7),
(213, 8), (213, 9),
(214, 10), (214, 11),
(215, 12), (215, 13),
(216, 14), (216, 15),
(217, 1), (217, 2),
(218, 3), (218, 4),
(219, 5),
(220, 12), (220, 13);

-- LEADERS (6)
INSERT INTO Leader VALUES
(301, 'Sarah', 'Kim', '555-7777', 'sarah.kim@example.com', 101),
(302, 'David', 'Reyes', '555-8888', 'david.reyes@example.com', 102),
(303, 'Jenna', 'Park', '555-3838', 'jenna.park@example.com', 101),
(304, 'Marcus', 'Diaz', '555-2220', 'marcus.diaz@example.com', 102),
(305, 'Elise', 'Turner', '555-4949', 'elise.turner@example.com', 101),
(306, 'Tyler', 'Gibson', '555-8181', 'tyler.gibson@example.com', 102);

-- SESSIONS (18)
INSERT INTO Session VALUES
(4001, 101, '2025-01-10', '17:00:00', 'Youth Room', 'Introduction'),
(4002, 101, '2025-01-17', '17:00:00', 'Youth Room', 'Discussion Night'),
(4003, 101, '2025-01-24', '17:00:00', 'Youth Room', 'Service Project Planning'),
(4004, 102, '2025-01-12', '18:00:00', 'Main Hall', 'Kickoff Meeting'),
(4005, 102, '2025-01-19', '18:00:00', 'Main Hall', 'Guest Speaker'),
(4006, 102, '2025-01-26', '18:00:00', 'Main Hall', 'Community Outreach Prep'),
(4007, 101, '2025-02-01', '17:00:00', 'Youth Room', 'Games Night'),
(4008, 102, '2025-02-02', '18:00:00', 'Main Hall', 'Worship Session'),
(4009, 101, '2025-02-08', '17:00:00', 'Youth Room', 'Bible Study'),
(4010, 102, '2025-02-09', '18:00:00', 'Main Hall', 'Leadership Training'),
(4011, 101, '2025-02-15', '17:00:00', 'Youth Room', 'Team Building'),
(4012, 102, '2025-02-16', '18:00:00', 'Main Hall', 'Debate Night'),
(4013, 101, '2025-02-22', '17:00:00', 'Youth Room', 'Movie Night'),
(4014, 102, '2025-02-23', '18:00:00', 'Main Hall', 'Service Review'),
(4015, 101, '2025-03-01', '17:00:00', 'Youth Room', 'Mentorship Lab'),
(4016, 102, '2025-03-02', '18:00:00', 'Main Hall', 'Music Night'),
(4017, 101, '2025-03-08', '17:00:00', 'Youth Room', 'Quiet Reflection'),
(4018, 102, '2025-03-09', '18:00:00', 'Main Hall', 'Advanced Study');

-- REGISTRATIONS (40)
INSERT INTO Registration VALUES
(201,1001),(201,1003),(201,1004),
(202,1001),(202,1002),(202,1005),
(203,1002),(203,1006),
(204,1003),(204,1005),
(205,1001),(205,1004),
(206,1006),(206,1003),
(207,1002),(207,1004),
(208,1001),(208,1005),(208,1006),
(209,1004),(209,1005),
(210,1003),(210,1006),
(211,1006),(211,1001),
(212,1002),(212,1004),
(213,1001),(213,1003),
(214,1005),(214,1006),
(215,1004),(215,1003),
(216,1002),(216,1006),
(217,1001),(217,1005),
(218,1003),(218,1004),
(219,1006),
(220,1002),(220,1003);

-- ATTENDANCE (35)
INSERT INTO Attendance VALUES
(201,1001,'09:05','16:00'),
(201,1003,'12:10','15:00'),
(202,1001,'09:20','16:10'),
(202,1005,'11:05','14:45'),
(203,1002,'10:15',NULL),
(204,1003,'12:30','14:00'),
(205,1004,'18:05','21:00'),
(206,1003,'12:15','15:10'),
(207,1004,'18:20','20:50'),
(208,1001,'09:12','16:30'),
(208,1005,'11:10','14:30'),
(209,1004,'18:00','20:00'),
(210,1003,'12:00','14:30'),
(211,1006,'09:40','11:50'),
(212,1002,'10:20','13:00'),
(213,1001,'09:05','15:30'),
(214,1005,'11:00','14:20'),
(214,1006,'09:50','12:00'),
(215,1004,'18:10','20:30'),
(216,1002,'10:05','12:40'),
(217,1001,'09:00','15:50'),
(218,1003,'12:15','14:45'),
(219,1006,'09:35','12:15'),
(220,1002,'10:00','13:20');

-- EVENT STAFF (20)
INSERT INTO EventStaff VALUES
(1001,501),(1001,503),(1001,507),
(1002,502),(1002,510),
(1003,504),(1003,501),
(1004,505),(1004,509),
(1005,506),(1005,507),
(1006,508),(1006,509),(1006,505),
(1001,510),(1003,503),
(1004,501),(1005,508),
(1002,506),(1006,510);
