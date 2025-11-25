DROP DATABASE IF EXISTS youth_group;
CREATE DATABASE youth_group;
USE youth_group;

CREATE TABLE Guardian
(
    guardianID  INT,
    firstName   VARCHAR(30) NOT NULL,
    lastName    VARCHAR(30) NOT NULL,
    phoneNumber VARCHAR(20),
    email       VARCHAR(60),
    PRIMARY KEY (guardianID)
);

CREATE TABLE SmallGroup
(
    groupID INT,
    name    VARCHAR(30),
    PRIMARY KEY (groupID)
);
CREATE TABLE Event
(
    eventID  INT,
    name     VARCHAR(60),
    location VARCHAR(60) NOT NULL,
    date     DATE        NOT NULL,
    time     TIME        NOT NULL,
    PRIMARY KEY (eventID)
);
CREATE TABLE Volunteer
(
    volunteerID INT,
    firstName   VARCHAR(30) NOT NULL,
    lastName    VARCHAR(30) NOT NULL,
    phoneNumber VARCHAR(20),
    email       VARCHAR(60),
    eventID     INT         NOT NULL,
    PRIMARY KEY (volunteerID),
    FOREIGN KEY (eventID) REFERENCES Event (eventID)
);
CREATE TABLE Relationship
(
    studentID  INT NOT NULL,
    guardianID INT NOT NULL,
    PRIMARY KEY (studentID, guardianID),
    FOREIGN KEY (guardianID) REFERENCES Guardian (guardianID)
);
CREATE TABLE Student
(
    studentID   INT,
    firstName   VARCHAR(30) NOT NULL,
    lastName    VARCHAR(30) NOT NULL,
    age         INT         NOT NULL,
    phoneNumber VARCHAR(20),
    email       VARCHAR(60),
    guardian1ID INT         NOT NULL,
    guardian2ID INT,
    groupID     INT         NOT NULL,
    PRIMARY KEY (studentID),
    FOREIGN KEY (guardian1ID) REFERENCES Guardian (guardianID),
    FOREIGN KEY (guardian2ID) REFERENCES Guardian (guardianID),
    FOREIGN KEY (groupID) REFERENCES SmallGroup (groupID)
);
ALTER TABLE Relationship
    ADD FOREIGN KEY (studentID) REFERENCES Student (studentID)
;
CREATE TABLE Leader
(
    leaderID    INT         NOT NULL,
    firstName   VARCHAR(30) NOT NULL,
    lastName    VARCHAR(30) NOT NULL,
    phoneNumber VARCHAR(20),
    email       VARCHAR(60),
    groupID     INT UNIQUE  NOT NULL,
    PRIMARY KEY (leaderID),
    FOREIGN KEY (groupID) REFERENCES SmallGroup (groupID)
);
CREATE TABLE Session
(
    sessionID INT,
    groupID   INT         NOT NULL,
    date      DATE        NOT NULL,
    time      TIME        NOT NULL,
    location  VARCHAR(60) NOT NULL,
    notes     VARCHAR(1023),
    PRIMARY KEY (sessionID),
    FOREIGN KEY (groupID) REFERENCES SmallGroup (groupID)
);
CREATE TABLE Registration
(
    studentID INT NOT NULL,
    eventID   INT NOT NULL,
    PRIMARY KEY (studentID, eventID),
    FOREIGN KEY (studentID) REFERENCES Student (studentID),
    FOREIGN KEY (eventID) REFERENCES Event (eventID)
);
CREATE TABLE Attendance
(
    studentID    INT  NOT NULL,
    eventID      INT  NOT NULL,
    checkInTime  TIME NOT NULL,
    checkOutTime TIME,
    PRIMARY KEY (studentID, eventID),
    FOREIGN KEY (studentID, eventID) REFERENCES Registration (studentID, eventID)
);
CREATE TABLE EventStaff
(
    eventID     INT NOT NULL,
    volunteerID INT NOT NULL,
    PRIMARY KEY (eventID, volunteerID),
    FOREIGN KEY (eventID) REFERENCES Event (eventID),
    FOREIGN KEY (volunteerID) REFERENCES Volunteer (volunteerID)
);
