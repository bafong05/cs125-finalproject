CREATE TABLE Student (
    studentID INT,
    firstName VARCHAR(30) NOT NULL,
    lastName VARCHAR(30) NOT NULL,
    age INT NOT NULL,
    phoneNumber INT,
    email VARCHAR(60),
    guardian1ID INT NOT NULL,
    guardian2ID INT,
    groupID INT NOT NULL,
    PRIMARY KEY (studentID),
    FOREIGN KEY (guardian1ID) REFERENCES Relationship (guardianID),
    FOREIGN KEY (guardian2ID) REFERENCES Relationship (guardianID),
    FOREIGN KEY (groupID) REFERENCES SmallGroup (groupID)
)
CREATE TABLE Relationship (
    studentID INT NOT NULL,
    guardianID INT NOT NULL,
)
CREATE TABLE Guardian (
    guardianID INT,
    firstName VARCHAR(30) NOT NULL,
    lastName VARCHAR(30) NOT NULL,
    phoneNumber INT,
    email VARCHAR(60),
    PRIMARY KEY (guardianID)
)
CREATE TABLE Registration (
    studentID INT,
    eventID INT NOT NULL,
    PRIMARY KEY (studentID)
)
CREATE TABLE Attendance (
    studentID INT NOT NULL,
    eventID INT NOT NULL,
    checkInTime TIME NOT NULL,
    checkOutTime TIME NOT NULL,
    CHECK ((Registration.studentID AND Registration.eventID)
        == (Attendance.studentID AND Attendance.eventID))
)
CREATE TABLE SmallGroup (
    groupID INT,
    name VARCHAR(30),
    PRIMARY KEY (groupID)
)
CREATE TABLE Session (
    sessionID INT,
    groupID INT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR(60) NOT NULL,
    notes VARCHAR(1023),
    PRIMARY KEY (sessionID)
)
CREATE TABLE Event (
    eventID INT,
    name VARCHAR(60),
    location VARCHAR(60) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    PRIMARY KEY (eventID)
)
CREATE TABLE Leader (
    leaderID INT NOT NULL,
    firstName VARCHAR(30) NOT NULL,
    lastName VARCHAR(30) NOT NULL,
    phoneNumber INT,
    email VARCHAR(60),
    groupID INT NOT NULL,
)
CREATE TABLE EventStaff (
    eventID INT NOT NULL,
    volunteerID INT NOT NULL,
)
CREATE TABLE Volunteer (
    volunteerID INT,
    firstName VARCHAR(30) NOT NULL,
    lastName VARCHAR(30) NOT NULL,
    phoneNumber INT,
    email VARCHAR(60),
    eventID INT NOT NULL,
    PRIMARY KEY (volunteerID)
)
