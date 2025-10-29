CREATE TABLE venues(name varchar(50) PRIMARY KEY, isHall boolean);
CREATE TABLE CCs(name varchar(50) PRIMARY KEY, password varchar(20));
CREATE TABLE Bookings ( Booking_ID INT PRIMARY KEY, Venue VARCHAR(100), Start_Time TIME, Start_Date DATE, End_Time TIME, End_Date DATE, Name VARCHAR(100), Status VARCHAR(50), Event_Name VARCHAR(100));
