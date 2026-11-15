import sqlite3
from pathlib import Path


# Database file location
DB_NAME = Path(__file__).parent / "students.db"


# Connect to database
def connect_db():
    connection = sqlite3.connect(DB_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# Create database tables
def create_tables():

    with connect_db() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                class_name TEXT NOT NULL,
                section TEXT NOT NULL,
                dob TEXT,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                marks REAL NOT NULL,
                total REAL NOT NULL,
                term TEXT NOT NULL,
                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE,
                UNIQUE(student_id, subject, term)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                attendance_date TEXT NOT NULL,
                status TEXT NOT NULL
                    CHECK(status IN ('Present', 'Absent', 'Late')),
                FOREIGN KEY (student_id)
                    REFERENCES students(student_id)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE,
                UNIQUE(student_id, attendance_date)
            )
        """)


# -------------------- STUDENT FUNCTIONS --------------------

# Get all student records
def get_all_students():

    with connect_db() as connection:

        students = connection.execute("""
            SELECT * FROM students
            ORDER BY student_id
        """).fetchall()

    return students


# Add new student
def add_student(student):

    with connect_db() as connection:

        connection.execute("""
            INSERT INTO students (
                student_id, name, gender, class_name,
                section, dob, phone, email, address
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, student)


# Update student information
def update_student(student, original_student_id):

    with connect_db() as connection:

        cursor = connection.execute("""
            UPDATE students
            SET student_id = ?,
                name = ?,
                gender = ?,
                class_name = ?,
                section = ?,
                dob = ?,
                phone = ?,
                email = ?,
                address = ?
            WHERE student_id = ?
        """, (*student, str(original_student_id)))

        if cursor.rowcount == 0:
            raise ValueError("Student record was not found.")


# Delete student
def delete_student(student_id):

    with connect_db() as connection:

        cursor = connection.execute("""
            DELETE FROM students
            WHERE student_id = ?
        """, (str(student_id),))

        if cursor.rowcount == 0:
            raise ValueError("Student record was not found.")


# Search students by ID or name
def search_students(keyword):

    with connect_db() as connection:

        students = connection.execute("""
            SELECT * FROM students
            WHERE student_id LIKE ?
               OR name LIKE ?
            ORDER BY student_id
        """, (f"%{keyword}%", f"%{keyword}%")).fetchall()

    return students


# -------------------- MARKS FUNCTIONS --------------------

# Get all academic records
def get_all_marks():

    with connect_db() as connection:

        records = connection.execute("""
            SELECT marks.id,
                   marks.student_id,
                   students.name,
                   marks.subject,
                   marks.marks,
                   marks.total,
                   marks.term
            FROM marks
            INNER JOIN students
                ON marks.student_id = students.student_id
            ORDER BY students.student_id,
                     marks.term,
                     marks.subject
        """).fetchall()

    return records


# Add marks for a student
def add_marks(student_id, subject, marks, total, term):

    with connect_db() as connection:

        connection.execute("""
            INSERT INTO marks (
                student_id, subject, marks, total, term
            )
            VALUES (?, ?, ?, ?, ?)
        """, (str(student_id), subject, marks, total, term))


# Update existing marks
def update_marks(mark_id, student_id, subject, marks, total, term):

    with connect_db() as connection:

        cursor = connection.execute("""
            UPDATE marks
            SET student_id = ?,
                subject = ?,
                marks = ?,
                total = ?,
                term = ?
            WHERE id = ?
        """, (
            str(student_id),
            subject,
            marks,
            total,
            term,
            mark_id
        ))

        if cursor.rowcount == 0:
            raise ValueError("Academic record was not found.")


# Delete an academic record
def delete_marks(mark_id):

    with connect_db() as connection:

        cursor = connection.execute("""
            DELETE FROM marks
            WHERE id = ?
        """, (mark_id,))

        if cursor.rowcount == 0:
            raise ValueError("Academic record was not found.")


# -------------------- ATTENDANCE FUNCTIONS --------------------

# Save or update a student's attendance
def save_attendance(student_id, attendance_date, status):

    if status not in ("Present", "Absent", "Late"):
        raise ValueError("Invalid attendance status.")

    with connect_db() as connection:

        connection.execute("""
            INSERT INTO attendance (
                student_id, attendance_date, status
            )
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, attendance_date)
            DO UPDATE SET status = excluded.status
        """, (str(student_id), attendance_date, status))


# Get attendance for a selected date
def get_attendance_by_date(attendance_date):

    with connect_db() as connection:

        records = connection.execute("""
            SELECT students.student_id,
                   students.name,
                   students.class_name,
                   students.section,
                   attendance.status
            FROM students
            LEFT JOIN attendance
                ON students.student_id = attendance.student_id
                AND attendance.attendance_date = ?
            ORDER BY students.class_name,
                     students.section,
                     students.name
        """, (attendance_date,)).fetchall()

    return records


# Get attendance history for one student
def get_student_attendance(student_id):

    with connect_db() as connection:

        records = connection.execute("""
            SELECT attendance_date, status
            FROM attendance
            WHERE student_id = ?
            ORDER BY attendance_date DESC
        """, (str(student_id),)).fetchall()

    return records


# Get attendance totals for dashboard
def get_attendance_summary():

    with connect_db() as connection:

        result = connection.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END)
            FROM attendance
        """).fetchone()

    return tuple(value or 0 for value in result)


# Run database setup
if __name__ == "__main__":

    create_tables()

    print("Database and tables created successfully!")
