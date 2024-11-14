	CREATE DATABASE dance ;
	USE dance;
	DROP DATABASE dance;
	CREATE TABLE Student (
		StudentID VARCHAR(10) NOT NULL,
		First_Name VARCHAR(100) Default NULL,
		Last_Name VARCHAR(100) DEFAULT NULL,
		Email VARCHAR(100),
		Phone BIGINT,
		Password VARCHAR(20),
		PRIMARY KEY (StudentID)
	);


	CREATE TABLE Student_EmergencyContact (
		StudentID VARCHAR(10) NOT NULL,
		Emergency_Contact BIGINT,
		PRIMARY KEY (StudentID , Emergency_Contact)
	);

	CREATE TABLE Instructor (
		InstructorID VARCHAR(10) NOT NULL,
		First_Name VARCHAR(100) DEFAULT NULL,
		Last_Name VARCHAR(100) DEFAULT NULL,
		Email VARCHAR(100),
		Password Varchar(20),
		PRIMARY KEY (InstructorID)
	);

	CREATE TABLE Instructor_ContactNumber (
		InstructorID VARCHAR(10) NOT NULL,
		Contact_number BIGINT,
		PRIMARY KEY (InstructorID , Contact_number)
	);

	CREATE TABLE Administrator (
		AdminID VARCHAR(10) NOT NULL,
		First_Name VARCHAR(100) DEFAULT NULL ,
		Last_Name VARCHAR(100) DEFAULT NULL ,
		Email VARCHAR(100),
		Password VARCHAR(50),
		PRIMARY KEY (AdminID) 
	);

	CREATE TABLE Class (
		ClassID VARCHAR(10) PRIMARY KEY NOT NULL,
		RoomNumber INT,
		Start_Time Time,
		End_Time Time,
		StudentCapacity INT,
		Enrollment_Status VARCHAR(50),
        Fee DECIMAL(10, 2),
		InstructorID VARCHAR(10) ,
		PrereqID VARCHAR(10) ,
		FOREIGN KEY (PrereqID) REFERENCES Class(ClassID),
		FOREIGN KEY (InstructorID) REFERENCES Instructor(InstructorID)
	);
    ALTER TABLE Class DROP FOREIGN KEY class_ibfk_2;

    ALTER TABLE Class MODIFY COLUMN InstructorID VARCHAR(10) NULL;
    ALTER TABLE Class
ADD CONSTRAINT class_ibfk_2 FOREIGN KEY (InstructorID) REFERENCES Instructor(InstructorID) ON DELETE SET NULL;

	CREATE TABLE ClassPrereq (
		ClassID VARCHAR(10) NOT NULL,
		PrereqID VARCHAR(10) NOT NULL ,
		PRIMARY KEY (ClassID , PrereqID),
		FOREIGN KEY (ClassID) REFERENCES Class(ClassID) ,
		FOREIGN KEY (PrereqID) REFERENCES Class(ClassID)
	);
		
	CREATE TABLE Enrolls_In_R (
		StudentID VARCHAR(10),
		ClassID VARCHAR(10),
		Enrollment_date DATE,
		PRIMARY KEY (StudentID, ClassID),  
		FOREIGN KEY (StudentID) REFERENCES Student(StudentID),  
		FOREIGN KEY (ClassID) REFERENCES Class(ClassID)      
	);

	CREATE TABLE Payment (
	PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    PaymentDate DATE,
    Amount DECIMAL(10, 2),
    StudentID VARCHAR(10),
    ClassID VARCHAR(10),
    FOREIGN KEY (ClassID) REFERENCES Class(ClassID),
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID) ON DELETE CASCADE
);


	INSERT INTO Student (StudentID, First_Name, Last_Name, Email, Phone ,Password) VALUES
	('S001', 'Rajesh', 'Sharma', 'rajesh.sharma@gmail.com', 9876543210, 'raj@esh'),
	('S002', 'Priya', 'Iyer', 'priya.iyer@gmail.com', 9876543211, 'priya123'),
	('S003', 'Sanjay', 'Verma', 'sanjay.verma@gmail.com', 9876543212,'hello@123'),
	('S004', 'Anjali', 'Deshmukh', 'anjali.deshmukh@gmail.com', 9876543213,'anj@ali'),
	('S005', 'Amit', 'Kumar', 'amit.kumar@gmail.com', 9876543214, 'amit_kumar@123'),
	('S006', 'Ritu', 'Patel', 'ritu.patel@gmail.com', 9876543215,'ritup'),
	('S007', 'Akash', 'Mehra', 'akash.mehra@gmail.com', 9876543216,'ak@sh'),
	('S008', 'Sneha', 'Pandey', 'sneha.pandey@gmail.com', 9876543217,'sne@123ha'),
	('S009', 'Vikram', 'Sethi', 'vikram.sethi@gmail.com', 9876543218,'vik@1309'),
	('S0010', 'Kavita', 'Singh', 'kavita.singh@gmail.com', 9876543219,'kavs&12');

	INSERT INTO Instructor (InstructorID, First_Name, Last_Name, Email, Password) VALUES
	('I001', 'Arvind', 'Nair', 'arvind.nair@gmail.com','arv@123'),
	('I002', 'Shweta', 'Gupta', 'shweta.gupta@gmail.com','Shweta12'),
	('I003', 'Rohan', 'Mishra', 'rohan.mishra@gmail.com','roh@mishra');

	INSERT INTO Class (ClassID, RoomNumber, Start_Time, End_Time, StudentCapacity, Enrollment_Status, Fee, InstructorID, PrereqID) VALUES
	('C101', 201, '09:00:00', '10:30:00', 30, 'Open', 1500, 'I001', NULL),
	('C102', 202, '11:00:00', '12:30:00', 25, 'Open', 2000, 'I002', 'C101'),
	('C103', 203, '14:00:00', '15:30:00', 20, 'Open', 2500, 'I003', 'C102');

	INSERT INTO ClassPrereq (ClassID, PrereqID) VALUES
	('C102', 'C101'),
	('C103', 'C102');

	INSERT INTO Enrolls_In_R (StudentID, ClassID, Enrollment_date) VALUES
	('S001', 'C101', '2024-10-01'),
	('S002', 'C101', '2024-10-01'),
	('S003', 'C102', '2024-10-02'),
	('S004', 'C102', '2024-10-02'),
	('S005', 'C103', '2024-10-03'),
	('S006', 'C103', '2024-10-03'),
	('S007', 'C101', '2024-10-04'),
	('S008', 'C102', '2024-10-05'),
	('S009', 'C103', '2024-10-05'),
	('S0010', 'C101', '2024-10-06');

	INSERT INTO Payment (PaymentID, PaymentDate, Amount, StudentID, ClassID) VALUES
	(1, '2024-10-02', 1500.00, 'S001', 'C101'),
	(2, '2024-10-02', 1500.00, 'S002', 'C101'),
	(3, '2024-10-03', 2000.00, 'S003', 'C102'),
	(4, '2024-10-03', 2000.00, 'S004', 'C102'),
	(5, '2024-10-04', 2500.00, 'S005', 'C103'),
	(6, '2024-10-04', 2500.00, 'S006', 'C103'),
	(7, '2024-10-05', 1500.00, 'S007', 'C101'),
	(8, '2024-10-06', 2000.00, 'S008', 'C102'),
	(9, '2024-10-06', 2500.00, 'S009', 'C103'),
	(10, '2024-10-07', 1500.00, 'S0010', 'C101');

	INSERT INTO Student_EmergencyContact (StudentID, Emergency_Contact) VALUES
	('S001', 9123456780),
	('S001', 9123456790),  -- Second contact for student 1
	('S002', 9123456781),
	('S002', 9123456791),  -- Second contact for student 2
	('S003', 9123456782), 
	('S004', 9123456783), 
	('S005', 9123456784), 
	('S006', 9123456785), 
	('S007', 9123456786), 
	('S008', 9123456787), 
	('S009', 9123456788),
	('S009', 9123456792),  -- Second contact for student 9
	('S0010', 9123456789);

	INSERT INTO Instructor_ContactNumber (InstructorID, Contact_number) VALUES
	('I001', 9987654321),
	('I001', 9987654324),  -- Second contact for Instructor 1
	('I002', 9987654322),
	('I002', 9987654325),  -- Second contact for Instructor 2
	('I003', 9987654323),
	('I003', 9987654326);  -- Second contact for Instructor 3

	INSERT INTO Administrator (AdminID, First_Name, Last_Name, Email, Password) VALUES
	('A001', 'Neha', 'Kapoor', 'neha.kapoor@gmail.com', 'admin123'),
	('A002', 'Arun', 'Patel', 'arun.patel@gmail.com', 'admin456'),
	('A003', 'Sonia', 'Reddy', 'sonia.reddy@gmail.com', 'admin789'),
	('A004', 'Vikas', 'Shah', 'vikas.shah@gmail.com', 'admin101');

DELIMITER //

CREATE TRIGGER check_class_capacity
BEFORE INSERT ON Enrolls_In_R
FOR EACH ROW
BEGIN
    DECLARE current_capacity INT;
    DECLARE max_capacity INT;

    -- Get the current number of enrolled students
    SET current_capacity = (
        SELECT COUNT(*) FROM Enrolls_In_R WHERE ClassID = NEW.ClassID
    );

    -- Get the maximum capacity for the class
    SET max_capacity = (
        SELECT StudentCapacity FROM Class WHERE ClassID = NEW.ClassID
    );

    -- Check if adding the student would exceed capacity
    IF current_capacity >= max_capacity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Class capacity exceeded!';
    END IF;
END;
//

DELIMITER ;

DELIMITER //

CREATE PROCEDURE EnrollStudent(IN p_StudentID VARCHAR(10), IN p_ClassID VARCHAR(10), IN p_EnrollmentDate DATE)
BEGIN
    DECLARE prereq_count INT;
    DECLARE fulfilled_prereqs INT;

    -- Count the number of prerequisites for the class
    SET prereq_count = (
        SELECT COUNT(*) FROM ClassPrereq WHERE ClassID = p_ClassID
    );

    -- Count the number of prerequisites the student has completed
    SET fulfilled_prereqs = (
        SELECT COUNT(*) FROM Enrolls_In_R e
        JOIN ClassPrereq cp ON e.ClassID = cp.PrereqID
        WHERE e.StudentID = p_StudentID AND cp.ClassID = p_ClassID
    );

    -- Check if all prerequisites are met
    IF fulfilled_prereqs < prereq_count THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Prerequisites not fulfilled for this class!';
    ELSE
        -- If prerequisites are met, enroll the student
        INSERT INTO Enrolls_In_R (StudentID, ClassID, Enrollment_date)
        VALUES (p_StudentID, p_ClassID, p_EnrollmentDate);
    END IF;
END;

//

DELIMITER ;

DELIMITER //


CREATE FUNCTION GetTotalPayments(p_StudentID VARCHAR(10))
RETURNS DECIMAL(10, 2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_amount DECIMAL(10, 2);

    -- Calculate total payment amount for the student
    SET total_amount = (
        SELECT COALESCE(SUM(Amount), 0) FROM Payment WHERE StudentID = p_StudentID
    );

    RETURN total_amount;
END;
//

DELIMITER ;
-- CHECK TRIGGER 
INSERT INTO ClassPrereq (ClassID, PrereqID) VALUES
	('C104', 'C102');
    
INSERT INTO Class (ClassID, RoomNumber, Start_Time, End_Time, StudentCapacity, Enrollment_Status, Fee, InstructorID, PrereqID) VALUES
	('C104', 204, '16:00:00', '17:30:00', 2, 'Open', 1000, 'I001', 'C102');
    
INSERT INTO Enrolls_In_R (StudentID, ClassID, Enrollment_date) VALUES
	('S0011', 'C104', '2024-10-01'),
	('S0012', 'C104', '2024-10-01');

INSERT INTO Student (StudentID, First_Name, Last_Name, Email, Phone ,Password) VALUES
	('S0011', 'Luke', 'Jordan', 'luke.jord@gmail.com', 9876556778, 'luk@jor'),
	('S0012', 'Meethi', 'Mishra', 'meethimishra@gmail.com', 9876443445, 'meethi04'),
	('S0013', 'Akash', 'Patil', 'akash.patil@gmail.com', 9654778665,'akash@123');

INSERT INTO Student (StudentID, First_Name, Last_Name, Email, Phone ,Password) VALUES
	('S0020', 'Mia', 'George', 'mia.grg@gmail.com', 9876112334, 'mia');
INSERT INTO Enrolls_In_R (StudentID, ClassID, Enrollment_date) VALUES
	('S0020', 'C104', '2024-11-12');
    
select * from Payment;
select * from Enrolls_In_R; 	
select * from Class;
select * from Student;
Select * from Administrator;
Select * from Instructor;


DROP TABLE ENROLLMENT;

