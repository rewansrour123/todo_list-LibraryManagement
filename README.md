# Lab 3: Foreign Keys and Simple SQL

A web application built using Flask and MySQL, combining a **Login & To-Do Management System** with a **Library Management System** for books and authors.

This project extends Lab 2 by keeping the existing user authentication and personal task management features while adding library database operations for Lab 3.

---

## 👥 1. Team Members

| Name | Student ID | Responsibilities |
| Rewan Mahmoud Mohamed | 2304098 | Database Design, Flask Backend, Authentication, To-Do List, and Library Management |

---

## 🛠️ 2. Technologies & Tools

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL
- **Database Connector:** PyMySQL
- **Password Security:** bcrypt
- **Session Management:** Flask Sessions
- **Environment Variables:** python-dotenv

---

## ✨ 3. Website Features

### A. Login & To-Do Management — Lab 2

- User registration and login.
- Duplicate email handling.
- Secure password hashing using bcrypt.
- Session-based authentication.
- Private task lists for each user.
- Add new tasks.
- Edit existing task titles.
- Mark tasks as completed or incomplete.
- Delete tasks with confirmation.
- Client-side and server-side input validation.
- Maximum task title length of 200 characters.
- Parameterized SQL queries.
- Responsive user interface.
- Dark Mode and Light Mode.

### B. Library Management — Lab 3

- Display all books in a table, including their `author_id`.
- Display all authors in a separate table.
- Add new books and authors.
- Edit existing books and authors.
- Delete individual books.
- Delete authors and automatically delete their associated books using `ON DELETE CASCADE`.
- Store and manage library records using MySQL.

### C. Security and Database Integrity

- Primary keys to uniquely identify records.
- Foreign keys to establish relationships between tables.
- Referential integrity constraints.
- Parameterized SQL queries to help prevent SQL injection.
- Input validation for database operations.

---

## 🗄️ 4. Database Design

### Problem 1 — COMPANY Database

The first part implements the COMPANY database using three tables:

- `EMPLOYEE`
- `DEPARTMENT`
- `PROJECT`

Foreign key relationships:

- `EMPLOYEE.Dno` references `DEPARTMENT.Dnumber`.
- `PROJECT.Dno` references `DEPARTMENT.Dnumber`.
- `DEPARTMENT.mgr_ssn` references `EMPLOYEE.ssn`.

Files:

- `problem1_DDL.sql` — Database and table creation.
- `problem1_DML.sql` — Sample data insertion.
- `problem1_Answers.txt` — SQL statements and outputs for Q1.1–Q1.3.

### Problem 2 — Library Database

The second part adds two related tables:

**AUTHOR**

- `author_id` — Primary key.
- `name` — Author name.
- `country` — Author's country.

**BOOK**

- `book_id` — Primary key.
- `title` — Book title.
- `price` — Book price.
- `author_id` — Foreign key referencing `AUTHOR.author_id`.

The relationship uses `ON DELETE CASCADE`, so deleting an author also deletes the books associated with that author.

Files:

- `problem2_DDL.sql` — Library database and table creation.
- `problem2_DML.sql` — Seed data containing at least three authors and six books.

---

## 🚀 5. Installation & Setup

### Step 1 — Install Requirements

Make sure Python and MySQL are installed.

Navigate to the website directory and run:

```bash
pip install -r requirements.txt
```

### Step 2 — Set Up the Databases

From the project root directory, execute the SQL scripts:

```bash
mysql -u root -p < problem1_DDL.sql
mysql -u root -p < problem1_DML.sql
mysql -u root -p < problem2_DDL.sql
mysql -u root -p < problem2_DML.sql
```

Enter your MySQL password when prompted.

### Step 3 — Configure Environment Variables

Copy `.env.example` to `.env` and configure the required database credentials and Flask secret key.

Do not upload `.env` or expose sensitive credentials on GitHub.

### Step 4 — Run the Website

Navigate to the website directory:

```bash
cd website
python app.py
```

### Step 5 — Open the Website

Open the application in your browser:

[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

Use the registration and login pages to access the application. From the website, you can manage your personal to-do list and access the library pages for managing books and authors.

*Note: The database scripts must match the database names and configuration used by the Flask application.*

---

## 📸 6. Screenshots

Add screenshots of the actual implemented pages.

### Login & To-Do Application

- Registration page.
- Login page.
- To-do list management.

### Library Management

- Books table.
- Authors table.
- Add and edit book/author forms.
- Delete book/author operations.

---

## ✅ 7. Conclusion

This project extends the Lab 2 Login & To-Do application by integrating the Library Management functionality required for Lab 3.

It demonstrates user authentication, personal task management, relational database design, SQL CRUD operations, foreign key constraints, and referential integrity using Flask and MySQL.

---

## 📚 Course Information

- **University:** Alexandria National University
- **Faculty:** Faculty of Engineering
- **Course:** Introduction to Database Systems
- **Lab:** Lab 3 — Foreign Keys and Simple SQL
- **Semester:** Fall 2026
- **Submission Deadline:** October 26, 2026, at 11:59 PM
