
USE company;

INSERT INTO DEPARTMENT
(Dnumber, Dname, mgr_ssn, mgr_start_date)
VALUES
(1, 'Research', NULL, '2024-01-01'),
(2, 'Administration', NULL, '2024-02-01'),
(3, 'IT', NULL, '2024-03-01');

INSERT INTO EMPLOYEE
(ssn, fname, lname, bdate, address, gender, salary, Dno)
VALUES
('100000001', 'Ahmed', 'Ali', '2002-05-14',
 'Alexandria, Egypt', 'M', 12000.00, 1),

('100000002', 'Mona', 'Hassan', '2001-09-22',
 'Cairo, Egypt', 'F', 13500.00, 2),

('100000003', 'Omar', 'Mahmoud', '2003-01-10',
 'Alexandria, Egypt', 'M', 11000.00, 3);

UPDATE DEPARTMENT
SET mgr_ssn = '100000001'
WHERE Dnumber = 1;

UPDATE DEPARTMENT
SET mgr_ssn = '100000002'
WHERE Dnumber = 2;

UPDATE DEPARTMENT
SET mgr_ssn = '100000003'
WHERE Dnumber = 3;

INSERT INTO PROJECT
(Pnumber, Pname, Plocation, Dno)
VALUES
(101, 'AI Research', 'Alexandria', 1),
(102, 'Office Upgrade', 'Cairo', 2),
(103, 'Network System', 'Alexandria', 3);

