
import database


# -------------------- STUDENT VALIDATION --------------------

# Validate student information
def validate_student(student):

    # Check Student ID
    if not student[0].strip():
        return False, "Please enter Student ID."

    # Check Student Name
    if not student[1].strip():
        return False, "Please enter Student Name."

    # Check Gender
    if not student[2]:
        return False, "Please select Gender."

    # Check Class
    if not student[3]:
        return False, "Please select Class."

    # Check Section
    if not student[4]:
        return False, "Please select Section."

    # Check Phone Number
    if student[6] and not student[6].isdigit():
        return False, "Phone number must contain digits only."

    # Check Email
    if student[7] and "@" not in student[7]:
        return False, "Please enter a valid email address."

    return True, "Valid student information."


# -------------------- STUDENT FUNCTIONS --------------------

# Add student
def add_student(student):

    valid, message = validate_student(student)

    if not valid:
        return False, message

    try:
        database.add_student(student)

        return True, "Student added successfully!"

    except Exception as error:

        if "UNIQUE constraint failed" in str(error):
            return False, "Student ID already exists."

        return False, f"Unable to add student: {error}"


# Update student
def update_student(student, original_student_id):

    valid, message = validate_student(student)

    if not valid:
        return False, message

    try:
        database.update_student(
            student,
            original_student_id
        )

        return True, "Student updated successfully!"

    except Exception as error:

        if "UNIQUE constraint failed" in str(error):
            return False, "This Student ID already exists."

        return False, f"Unable to update student: {error}"


# Delete student
def delete_student(student_id):

    if student_id is None or not str(student_id).strip():
        return False, "Please select a student first."

    try:
        database.delete_student(student_id)

        return True, "Student deleted successfully!"

    except Exception as error:

        return False, f"Unable to delete student: {error}"


# Get all student records
def get_students():

    return database.get_all_students()


# Search student records
def search_student(keyword):

    return database.search_students(keyword)


# -------------------- ACADEMIC RECORD FUNCTIONS --------------------

# Get all academic records
def get_marks():

    return database.get_all_marks()


# Add marks
def add_marks(student_id, subject, marks, total, term):

    try:
        if not subject.strip():
            return False, "Please enter Subject."

        if not term.strip():
            return False, "Please select Term."

        if total <= 0:
            return False, "Total marks must be greater than zero."

        if marks < 0 or marks > total:
            return False, "Marks must be between 0 and Total Marks."

        database.add_marks(
            student_id,
            subject,
            marks,
            total,
            term
        )

        return True, "Marks added successfully!"

    except Exception as error:

        if "UNIQUE constraint failed" in str(error):
            return False, "This subject's marks already exist for this student and term."

        return False, f"Unable to add marks: {error}"


# Update existing marks
def update_marks(mark_id, student_id, subject, marks, total, term):

    try:
        if not subject.strip():
            return False, "Please enter Subject."

        if not term.strip():
            return False, "Please select Term."

        if total <= 0:
            return False, "Total marks must be greater than zero."

        if marks < 0 or marks > total:
            return False, "Marks must be between 0 and Total Marks."

        database.update_marks(
            mark_id,
            student_id,
            subject,
            marks,
            total,
            term
        )

        return True, "Marks updated successfully!"

    except Exception as error:

        if "UNIQUE constraint failed" in str(error):
            return False, "This subject's marks already exist for this student and term."

        return False, f"Unable to update marks: {error}"


# Delete academic record
def delete_marks(mark_id):

    try:
        database.delete_marks(mark_id)

        return True, "Academic record deleted successfully!"

    except Exception as error:

        return False, f"Unable to delete academic record: {error}"
