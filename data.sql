USE youth_group;

-- ============================
-- GUARDIANS
-- ============================
INSERT INTO Guardian (firstName, lastName, phoneNumber, email)
VALUES 
 ('Laura', 'Mitchell', '555-1111', 'laura.mitchell@example.com'),
 ('James', 'Mitchell', '555-2222', 'james.mitchell@example.com'),
 ('Sophie', 'Young', '555-3333', 'sophie.young@example.com'),
 ('Daniel', 'Young', '555-4444', 'daniel.young@example.com'),
 ('Karen', 'Lopez', '555-5555', 'karen.lopez@example.com'),
 ('Tina', 'Johnson', '555-6666', 'tina.johnson@example.com'),
 ('Marcus', 'Johnson', '555-7777', 'marcus.johnson@example.com'),
 ('Amy', 'Wong', '555-8881', 'amy.wong@example.com'),
 ('Robert', 'Wong', '555-8882', 'robert.wong@example.com'),
 ('Linda', 'Chavez', '555-9081', 'linda.chavez@example.com'),
 ('Carlos', 'Chavez', '555-9082', 'carlos.chavez@example.com'),
 ('Helen', 'Smith', '555-9090', 'helen.smith@example.com'),
 ('George', 'Smith', '555-9091', 'george.smith@example.com'),
 ('Olivia', 'Reed', '555-7575', 'olivia.reed@example.com'),
 ('Paul', 'Reed', '555-7576', 'paul.reed@example.com');

-- ============================
-- SMALL GROUPS
-- ============================
INSERT INTO SmallGroup (name)
VALUES 
 ('Middle School'),
 ('High School');

-- Capture IDs
SET @Group101 = 1;
SET @Group102 = 2;

-- ============================
-- EVENTS (auto IDs)
-- ============================
INSERT INTO Event (name, location, date, time)
VALUES 
 ('Winter Retreat', 'Camp Redwood', '2026-01-14', '09:00:00'),
 ('Youth Service Day', 'Community Center', '2026-02-20', '10:00:00'),
 ('Spring Picnic', 'Lakeside Park', '2026-03-12', '12:00:00'),
 ('Fundraising Gala', 'Church Hall', '2026-04-18', '18:00:00'),
 ('Summer Kickoff', 'Beachside', '2026-06-10', '11:00:00'),
 ('Holiday Giving Event', 'Food Bank', '2026-12-05', '09:30:00');

-- Save eventIDs
SET @E1 = 1;
SET @E2 = 2;
SET @E3 = 3;
SET @E4 = 4;
SET @E5 = 5;
SET @E6 = 6;

-- ============================
-- STUDENTS
-- ============================
INSERT INTO Student (firstName, lastName, age, phoneNumber, email, 
                     guardian1ID, guardian2ID, groupID)
VALUES
 ('Emily', 'Mitchell', 13, '555-1234', 'emily.m@example.com', 1, 2, @Group101),
 ('Brian', 'Young', 15, '555-5678', 'brian.y@example.com', 3, 4, @Group101),
 ('Lily', 'Lopez', 14, '555-9999', 'lily.l@example.com', 5, NULL, @Group102),
 ('Jason', 'Johnson', 12, '555-2399', 'jason.j@example.com', 6, 7, @Group101),
 ('Chloe', 'Wong', 13, '555-7812', 'chloe.w@example.com', 8, 9, @Group101),
 ('Sofia', 'Chavez', 14, '555-4521', 'sofia.c@example.com', 10, 11, @Group102),
 ('Evan', 'Smith', 15, '555-2390', 'evan.s@example.com', 12, 13, @Group102),
 ('Noah', 'Reed', 16, '555-4492', 'noah.r@example.com', 14, 15, @Group102),
 ('Maya', 'Mitchell', 11, '555-1313', 'maya.m@example.com', 1, 2, @Group101),
 ('Aiden', 'Young', 12, '555-5656', 'aiden.y@example.com', 3, 4, @Group101),
 ('Bella', 'Lopez', 15, '555-9333', 'bella.l@example.com', 5, NULL, @Group102),
 ('Ethan', 'Johnson', 14, '555-6611', 'ethan.j@example.com', 6, 7, @Group101),
 ('Zoe', 'Wong', 13, '555-8891', 'zoe.w@example.com', 8, 9, @Group101),
 ('Lucas', 'Chavez', 16, '555-9033', 'lucas.c@example.com', 10, 11, @Group102),
 ('Grace', 'Smith', 15, '555-9060', 'grace.s@example.com', 12, 13, @Group102),
 ('Oliver', 'Reed', 14, '555-7481', 'oliver.r@example.com', 14, 15, @Group102),
 ('Natalie', 'Mitchell', 12, '555-1119', 'natalie.m@example.com', 1, 2, @Group101),
 ('Ryan', 'Young', 13, '555-6767', 'ryan.y@example.com', 3, 4, @Group101),
 ('Ella', 'Lopez', 14, '555-9099', 'ella.l@example.com', 5, NULL, @Group102),
 ('Jacob', 'Smith', 15, '555-9500', 'jacob.s@example.com', 12, 13, @Group102);

-- ============================
-- RELATIONSHIPS (studentID, guardianID)
-- ============================
INSERT INTO Relationship (studentID, guardianID)
VALUES 
 (1,1),(1,2),(2,3),(2,4),(3,5),(4,6),(4,7),(5,8),(5,9),
 (6,10),(6,11),(7,12),(7,13),(8,14),(8,15),
 (9,1),(9,2),(10,3),(10,4),(11,5),(12,6),(12,7),
 (13,8),(13,9),(14,10),(14,11),(15,12),(15,13),
 (16,14),(16,15),(17,1),(17,2),(18,3),(18,4),
 (19,5),(20,12),(20,13);

-- ============================
-- LEADERS
-- ============================
INSERT INTO Leader (firstName, lastName, phoneNumber, email, groupID)
VALUES 
 ('Sarah', 'Kim', '555-7777', 'sarah.kim@example.com', @Group101),
 ('David', 'Reyes', '555-8888', 'david.reyes@example.com', @Group102),
 ('Jenna', 'Park', '555-3838', 'jenna.park@example.com', @Group101),
 ('Marcus', 'Diaz', '555-2220', 'marcus.diaz@example.com', @Group102),
 ('Elise', 'Turner', '555-4949', 'elise.turner@example.com', @Group101),
 ('Tyler', 'Gibson', '555-8181', 'tyler.gibson@example.com', @Group102);

-- ============================
-- SESSIONS
-- ============================
INSERT INTO Session (groupID, date, time, location, notes)
VALUES
 (@Group101, '2026-01-10', '17:00:00', 'Youth Room', 'Introduction'),
 (@Group101, '2026-01-17', '17:00:00', 'Youth Room', 'Discussion Night'),
 (@Group101, '2026-01-24', '17:00:00', 'Youth Room', 'Service Project Planning'),
 (@Group102, '2026-01-12', '18:00:00', 'Main Hall', 'Kickoff Meeting'),
 (@Group102, '2026-01-19', '18:00:00', 'Main Hall', 'Guest Speaker'),
 (@Group102, '2026-01-26', '18:00:00', 'Main Hall', 'Community Outreach Prep'),
 (@Group101, '2026-02-01', '17:00:00', 'Youth Room', 'Games Night'),
 (@Group102, '2026-02-02', '18:00:00', 'Main Hall', 'Worship Session'),
 (@Group101, '2026-02-08', '17:00:00', 'Youth Room', 'Bible Study'),
 (@Group102, '2026-02-09', '18:00:00', 'Main Hall', 'Leadership Training'),
 (@Group101, '2026-02-15', '17:00:00', 'Youth Room', 'Team Building'),
 (@Group102, '2026-02-16', '18:00:00', 'Main Hall', 'Debate Night'),
 (@Group101, '2026-02-22', '17:00:00', 'Youth Room', 'Movie Night'),
 (@Group102, '2026-02-23', '18:00:00', 'Main Hall', 'Service Review'),
 (@Group101, '2026-03-01', '17:00:00', 'Youth Room', 'Mentorship Lab'),
 (@Group102, '2026-03-02', '18:00:00', 'Main Hall', 'Music Night'),
 (@Group101, '2026-03-08', '17:00:00', 'Youth Room', 'Quiet Reflection'),
 (@Group102, '2026-03-09', '18:00:00', 'Main Hall', 'Advanced Study');

-- ============================
-- REGISTRATIONS (studentID, eventID)
-- ============================
INSERT INTO Registration (studentID, eventID)
VALUES
 (1,@E1), (1,@E3), (1,@E4),
 (2,@E1), (2,@E2), (2,@E5),
 (3,@E2), (3,@E6),
 (4,@E3), (4,@E5),
 (5,@E1), (5,@E4),
 (6,@E6), (6,@E3),
 (7,@E2), (7,@E4),
 (8,@E1), (8,@E5), (8,@E6),
 (9,@E4), (9,@E5),
 (10,@E3), (10,@E6),
 (11,@E6), (11,@E1),
 (12,@E2), (12,@E4),
 (13,@E1), (13,@E3),
 (14,@E5), (14,@E6),
 (15,@E4), (15,@E3),
 (16,@E2), (16,@E6),
 (17,@E1), (17,@E5),
 (18,@E3), (18,@E4),
 (19,@E6),
 (20,@E2), (20,@E3);