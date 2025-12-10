DROP DATABASE IF EXISTS youth_group;
CREATE DATABASE youth_group;
USE youth_group;

CREATE TABLE Guardian
(
    guardianID  INT AUTO_INCREMENT,
    firstName   VARCHAR(30) NOT NULL,
    lastName    VARCHAR(30) NOT NULL,
    phoneNumber VARCHAR(20),
    email       VARCHAR(60),
    PRIMARY KEY (guardianID)
);

CREATE TABLE SmallGroup
(
    groupID INT AUTO_INCREMENT,
    name    VARCHAR(30) NOT NULL,
    PRIMARY KEY (groupID)
);
CREATE TABLE Event
(
    eventID  INT AUTO_INCREMENT,
    name     VARCHAR(60) NOT NULL,
    location VARCHAR(60) NOT NULL,
    date     DATE        NOT NULL,
    time     TIME        NOT NULL,
    PRIMARY KEY (eventID)
);
CREATE TABLE Relationship
(
    studentID  INT NOT NULL,
    guardianID INT NOT NULL,
    PRIMARY KEY (studentID, guardianID),
    FOREIGN KEY (guardianID) REFERENCES Guardian (guardianID) ON DELETE CASCADE
);
CREATE TABLE Student
(
    studentID   INT AUTO_INCREMENT,
    firstName   VARCHAR(30) NOT NULL,
    lastName    VARCHAR(30) NOT NULL,
    age         INT         NOT NULL,
    phoneNumber VARCHAR(20),
    email       VARCHAR(60),
    guardian1ID INT         NOT NULL,
    guardian2ID INT,
    groupID     INT         NOT NULL,
    PRIMARY KEY (studentID),
    FOREIGN KEY (guardian1ID) REFERENCES Guardian (guardianID) ON DELETE CASCADE,
    FOREIGN KEY (guardian2ID) REFERENCES Guardian (guardianID) ON DELETE SET NULL,
    FOREIGN KEY (groupID) REFERENCES SmallGroup (groupID) ON DELETE CASCADE
);
ALTER TABLE Relationship
    ADD FOREIGN KEY (studentID) REFERENCES Student (studentID) ON DELETE CASCADE
;
CREATE TABLE Leader
(
    leaderID    INT    AUTO_INCREMENT,
    firstName   VARCHAR(30) NOT NULL,
    lastName    VARCHAR(30) NOT NULL,
    phoneNumber VARCHAR(20),
    email       VARCHAR(60),
    groupID     INT         NOT NULL,
    PRIMARY KEY (leaderID),
    FOREIGN KEY (groupID) REFERENCES SmallGroup (groupID) ON DELETE CASCADE
);
CREATE TABLE Session
(
    sessionID INT AUTO_INCREMENT,
    groupID   INT         NOT NULL,
    date      DATE        NOT NULL,
    time      TIME        NOT NULL,
    location  VARCHAR(60) NOT NULL,
    notes     VARCHAR(1023),
    PRIMARY KEY (sessionID),
    FOREIGN KEY (groupID) REFERENCES SmallGroup (groupID) ON DELETE CASCADE
);
CREATE TABLE Registration
(
    studentID INT NOT NULL,
    eventID   INT NOT NULL,
    PRIMARY KEY (studentID, eventID),
    FOREIGN KEY (studentID) REFERENCES Student (studentID) ON DELETE CASCADE,
    FOREIGN KEY (eventID) REFERENCES Event (eventID) ON DELETE CASCADE
);
CREATE TABLE Attendance
(
    attendanceID INT AUTO_INCREMENT,
    studentID    INT  NOT NULL,
    eventID      INT  NOT NULL,
    checkInTime  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checkOutTime DATETIME,
    PRIMARY KEY (attendanceID),
    FOREIGN KEY (studentID) REFERENCES Student(studentID) ON DELETE CASCADE,
    FOREIGN KEY (eventID)   REFERENCES Event(eventID) ON DELETE CASCADE
);
