import sys
import sqlite3

from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QStackedWidget, QMessageBox,
    QDialog, QFormLayout, QDateEdit, QTextEdit, QHeaderView,
    QFrame, QDoubleSpinBox, QGraphicsOpacityEffect,
    QAbstractItemView, QScrollArea
)

import logic
import database


# -------------------- APPLICATION DESIGN --------------------

STYLE = """
* {
    font-family: 'Segoe UI';
}

QMainWindow, QWidget {
    background: #0B1020;
    color: #F4F6FF;
    font-size: 13px;
}

QFrame#Sidebar {
    background: #111A30;
    border-right: 1px solid #263653;
}

QLabel#Brand {
    color: #A78BFA;
    font-size: 23px;
    font-weight: 900;
}

QLabel#PageTitle {
    color: white;
    font-size: 27px;
    font-weight: 800;
}

QLabel#Muted {
    color: #9AA9C4;
}

QFrame#StatCard {
    background: #17233D;
    border: 1px solid #2A3A5B;
    border-radius: 16px;
}

QFrame#Panel {
    background: #121D34;
    border: 1px solid #263653;
    border-radius: 16px;
}

QPushButton {
    background: #7657E8;
    color: white;
    border: 0;
    border-radius: 9px;
    padding: 10px 14px;
    font-weight: bold;
}

QPushButton:hover {
    background: #947BFF;
}

QPushButton:pressed {
    background: #5D43C7;
}

QPushButton#NavButton {
    text-align: left;
    background: transparent;
    color: #C5CEE2;
    padding: 13px;
}

QPushButton#NavButton:hover {
    background: #263653;
    color: white;
}

QPushButton#Secondary {
    background: #263653;
    color: #E6EBF8;
}

QPushButton#Secondary:hover {
    background: #35496F;
}

QPushButton#Danger {
    background: #C7435B;
}

QPushButton#Danger:hover {
    background: #E65B72;
}

QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QTextEdit {
    background: #0D172B;
    color: white;
    border: 1px solid #344565;
    border-radius: 8px;
    padding: 9px;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
QTextEdit:focus {
    border: 1px solid #9A82FF;
}

QTableWidget {
    background: #111B30;
    alternate-background-color: #17233D;
    color: white;
    border: 1px solid #263653;
    border-radius: 12px;
    gridline-color: #263653;
    selection-background-color: #463A80;
}

QHeaderView::section {
    background: #263653;
    color: white;
    padding: 11px;
    border: none;
    font-weight: bold;
}

QMessageBox {
    background: #121D34;
}

QMessageBox QLabel {
    color: white;
}
"""


# -------------------- STUDENT REGISTRATION FORM --------------------

class StudentDialog(QDialog):

    def __init__(self, parent=None, student=None):
        super().__init__(parent)

        self.setWindowTitle("Student Profile")
        self.setMinimumWidth(440)
        self.setStyleSheet(STYLE)

        self.original_student_id = None

        layout = QVBoxLayout(self)

        title = QLabel("✦ Student Information")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setVerticalSpacing(12)

        self.student_id = QLineEdit()
        self.student_id.setPlaceholderText("Enter Student ID")

        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter full name")

        self.gender = QComboBox()
        self.gender.addItems(["Male", "Female", "Other"])

        self.class_name = QComboBox()
        self.class_name.addItems([
            "Class 7", "Class 8", "Class 9",
            "Class 10", "Class 11", "Class 12"
        ])

        self.section = QComboBox()
        self.section.addItems(["A", "B", "C"])

        self.dob = QDateEdit()
        self.dob.setCalendarPopup(True)
        self.dob.setDisplayFormat("dd MMM yyyy")
        self.dob.setDate(QDate.currentDate())

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Digits only")

        self.email = QLineEdit()
        self.email.setPlaceholderText("example@email.com")

        self.address = QTextEdit()
        self.address.setFixedHeight(65)

        form.addRow("Student ID:", self.student_id)
        form.addRow("Full Name:", self.name)
        form.addRow("Gender:", self.gender)
        form.addRow("Class:", self.class_name)
        form.addRow("Section:", self.section)
        form.addRow("Date of Birth:", self.dob)
        form.addRow("Phone:", self.phone)
        form.addRow("Email:", self.email)
        form.addRow("Address:", self.address)

        layout.addLayout(form)

        buttons = QHBoxLayout()

        cancel = QPushButton("Cancel")
        cancel.setObjectName("Secondary")
        cancel.clicked.connect(self.reject)

        save = QPushButton("Save Student ✓")
        save.clicked.connect(self.validate_student)

        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

        if student:

            self.original_student_id = str(student[0])
            self.student_id.setText(str(student[0]))
            self.name.setText(str(student[1]))
            self.gender.setCurrentText(str(student[2]))
            self.class_name.setCurrentText(str(student[3]))
            self.section.setCurrentText(str(student[4]))

            if student[5]:
                date = QDate.fromString(
                    str(student[5]), "yyyy-MM-dd"
                )

                if date.isValid():
                    self.dob.setDate(date)

            self.phone.setText(str(student[6] or ""))
            self.email.setText(str(student[7] or ""))
            self.address.setPlainText(str(student[8] or ""))

    def get_original_student_id(self):
        return self.original_student_id

    def validate_student(self):

        data = self.get_data()

        if not data[0]:
            QMessageBox.warning(
                self, "Missing Student ID",
                "Please enter Student ID."
            )
            return

        if not data[0].isdigit():
            QMessageBox.warning(
                self, "Invalid Student ID",
                "Student ID must contain numbers only."
            )
            return

        if not data[1]:
            QMessageBox.warning(
                self, "Missing Name",
                "Please enter Student Name."
            )
            return

        if not all(
            character.isalpha() or character.isspace()
            for character in data[1]
        ):
            QMessageBox.warning(
                self, "Invalid Name",
                "Name must contain alphabets only."
            )
            return

        if data[6] and not data[6].isdigit():
            QMessageBox.warning(
                self, "Invalid Phone",
                "Phone number must contain digits only."
            )
            return

        if data[7] and "@" not in data[7]:
            QMessageBox.warning(
                self, "Invalid Email",
                "Please enter a valid email address."
            )
            return

        self.accept()

    def get_data(self):

        return (
            self.student_id.text().strip(),
            self.name.text().strip(),
            self.gender.currentText(),
            self.class_name.currentText(),
            self.section.currentText(),
            self.dob.date().toString("yyyy-MM-dd"),
            self.phone.text().strip(),
            self.email.text().strip(),
            self.address.toPlainText().strip()
        )
    # -------------------- MARKS REGISTRATION FORM --------------------

class MarksDialog(QDialog):

    def __init__(self, parent=None, mark_record=None):
        super().__init__(parent)

        self.mark_record = mark_record
        self.editing = mark_record is not None

        if self.editing:
            self.setWindowTitle("Edit Student Marks")
        else:
            self.setWindowTitle("Add Student Marks")

        self.setMinimumWidth(390)
        self.setStyleSheet(STYLE)

        layout = QVBoxLayout(self)

        title = QLabel("✦ Examination Marks")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        form = QFormLayout()

        self.student = QComboBox()

        for student in logic.get_students():
            self.student.addItem(
                f"{student[0]} - {student[1]}",
                student[0]
            )

        self.subject = QLineEdit()
        self.subject.setPlaceholderText("Example: ICT")

        self.term = QComboBox()
        self.term.addItems([
            "Mid-Term", "Annual", "Class Test", "Other"
        ])

        self.marks = QDoubleSpinBox()
        self.marks.setRange(0, 1000)
        self.marks.setDecimals(2)

        self.total = QDoubleSpinBox()
        self.total.setRange(1, 1000)
        self.total.setDecimals(2)
        self.total.setValue(100)

        form.addRow("Student:", self.student)
        form.addRow("Subject:", self.subject)
        form.addRow("Term:", self.term)
        form.addRow("Marks Obtained:", self.marks)
        form.addRow("Total Marks:", self.total)

        layout.addLayout(form)

        buttons = QHBoxLayout()

        cancel = QPushButton("Cancel")
        cancel.setObjectName("Secondary")
        cancel.clicked.connect(self.reject)

        if self.editing:
            save = QPushButton("Update Marks ✓")
        else:
            save = QPushButton("Save Marks ✓")

        save.clicked.connect(self.validate_marks)

        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

        if self.editing:
            self.load_existing_marks()

    def load_existing_marks(self):

        mark_id, student_id, subject, marks, total, term = self.mark_record

        student_index = self.student.findData(student_id)

        if student_index >= 0:
            self.student.setCurrentIndex(student_index)

        self.subject.setText(str(subject))
        self.marks.setValue(float(marks))
        self.total.setValue(float(total))

        term_index = self.term.findText(str(term))

        if term_index >= 0:
            self.term.setCurrentIndex(term_index)
        else:
            self.term.addItem(str(term))
            self.term.setCurrentText(str(term))

    def validate_marks(self):

        if self.student.count() == 0:
            QMessageBox.warning(
                self, "No Students",
                "Please add a student first."
            )
            return

        if not self.subject.text().strip():
            QMessageBox.warning(
                self, "Missing Subject",
                "Please enter the subject."
            )
            return

        if self.marks.value() > self.total.value():
            QMessageBox.warning(
                self, "Invalid Marks",
                "Marks cannot exceed total marks."
            )
            return

        self.accept()

    def get_data(self):

        return (
            self.student.currentData(),
            self.subject.text().strip(),
            self.marks.value(),
            self.total.value(),
            self.term.currentText()
        )


# -------------------- STUDENT PROFILE WINDOW --------------------

class ProfileDialog(QDialog):

    def __init__(self, parent, student):
        super().__init__(parent)

        self.setWindowTitle("Student Profile")
        self.resize(850, 750)
        self.setMinimumSize(650, 550)
        self.setStyleSheet(STYLE)

        main_layout = QVBoxLayout(self)

        title = QLabel("✦ STUDENT PROFILE")
        title.setObjectName("PageTitle")
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Student information
        details_title = QLabel("STUDENT INFORMATION")
        details_title.setStyleSheet(
            "font-size:16px;font-weight:bold;color:#C4B5FD;"
        )
        layout.addWidget(details_title)

        details = (
            f"Student ID: {student[0]}\n"
            f"Full Name: {student[1]}\n"
            f"Gender: {student[2]}\n"
            f"Class: {student[3]} - {student[4]}\n"
            f"Date of Birth: {student[5] or 'Not provided'}\n"
            f"Phone: {student[6] or 'Not provided'}\n"
            f"Email: {student[7] or 'Not provided'}\n"
            f"Address: {student[8] or 'Not provided'}"
        )

        details_label = QLabel(details)
        details_label.setWordWrap(True)
        details_label.setStyleSheet(
            "font-size:14px;padding:15px;"
            "background:#17233D;border-radius:12px;"
        )
        layout.addWidget(details_label)

        # Academic records
        academic_title = QLabel("ACADEMIC RECORDS")
        academic_title.setStyleSheet(
            "font-size:16px;font-weight:bold;color:#C4B5FD;"
        )
        layout.addWidget(academic_title)

        with database.connect_db() as connection:
            academic_records = connection.execute("""
                SELECT subject, term, marks, total
                FROM marks
                WHERE student_id = ?
                ORDER BY term, subject
            """, (student[0],)).fetchall()

        if academic_records:

            total_marks = sum(
                float(record[2]) for record in academic_records
            )

            total_possible = sum(
                float(record[3]) for record in academic_records
            )

            overall_percentage = (
                total_marks / total_possible * 100
                if total_possible else 0
            )

            summary = QLabel(
                f"Recorded Subject Entries: {len(academic_records)}\n"
                f"Total Marks Obtained: {total_marks:g}\n"
                f"Total Possible Marks: {total_possible:g}\n"
                f"Overall Percentage: {overall_percentage:.1f}%"
            )

            summary.setStyleSheet(
                "font-size:14px;padding:12px;"
                "background:#17233D;border-radius:10px;"
            )
            layout.addWidget(summary)

            self.academic_table = QTableWidget(
                len(academic_records), 5
            )

            self.academic_table.setHorizontalHeaderLabels([
                "SUBJECT", "TERM", "MARKS",
                "TOTAL", "PERCENTAGE"
            ])

            self.prepare_profile_table(self.academic_table)

            for row, record in enumerate(academic_records):

                subject, term, marks, total = record

                percentage = (
                    float(marks) / float(total) * 100
                    if total else 0
                )

                values = [
                    subject,
                    term,
                    marks,
                    total,
                    f"{percentage:.1f}%"
                ]

                for column, value in enumerate(values):

                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                    self.academic_table.setItem(
                        row, column, item
                    )

            self.academic_table.setMinimumHeight(
                min(350, 45 * (len(academic_records) + 1))
            )

            layout.addWidget(self.academic_table)

        else:

            no_marks = QLabel(
                "No academic marks recorded for this student yet."
            )
            no_marks.setStyleSheet(
                "font-size:14px;padding:12px;color:#9AA9C4;"
            )
            layout.addWidget(no_marks)

        # Attendance history
        attendance_title = QLabel("ATTENDANCE HISTORY")
        attendance_title.setStyleSheet(
            "font-size:16px;font-weight:bold;color:#C4B5FD;"
        )
        layout.addWidget(attendance_title)

        history = database.get_student_attendance(student[0])

        if history:

            present = sum(
                1 for item in history
                if str(item[1]).strip().lower() == "present"
            )

            absent = sum(
                1 for item in history
                if str(item[1]).strip().lower() == "absent"
            )

            late = sum(
                1 for item in history
                if str(item[1]).strip().lower() == "late"
            )

            total_days = len(history)

            attendance_percentage = (
                present / total_days * 100
                if total_days else 0
            )

            attendance_summary = QLabel(
                f"Total Recorded Days: {total_days}\n"
                f"Present: {present}\n"
                f"Absent: {absent}\n"
                f"Late: {late}\n"
                f"Attendance Percentage: "
                f"{attendance_percentage:.1f}%"
            )

            attendance_summary.setStyleSheet(
                "font-size:14px;padding:12px;"
                "background:#17233D;border-radius:10px;"
            )

            layout.addWidget(attendance_summary)

            self.attendance_history_table = QTableWidget(
                len(history), 2
            )

            self.attendance_history_table.setHorizontalHeaderLabels([
                "DATE", "ATTENDANCE STATUS"
            ])

            self.prepare_profile_table(
                self.attendance_history_table
            )

            for row, record in enumerate(history):

                date, status = record

                date_item = QTableWidgetItem(str(date))
                status_item = QTableWidgetItem(str(status))

                date_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                status_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.attendance_history_table.setItem(
                    row, 0, date_item
                )

                self.attendance_history_table.setItem(
                    row, 1, status_item
                )

            self.attendance_history_table.setMinimumHeight(
                min(350, 45 * (len(history) + 1))
            )

            layout.addWidget(self.attendance_history_table)

            absent_title = QLabel("ABSENT DATES")
            absent_title.setStyleSheet(
                "font-size:15px;font-weight:bold;color:#F07878;"
            )
            layout.addWidget(absent_title)

            absent_dates = [
                str(item[0]) for item in history
                if str(item[1]).strip().lower() == "absent"
            ]

            if absent_dates:
                absent_label = QLabel("\n".join(absent_dates))
            else:
                absent_label = QLabel("No absent days recorded.")

            absent_label.setWordWrap(True)
            absent_label.setStyleSheet(
                "font-size:14px;padding:12px;"
                "background:#17233D;border-radius:10px;"
            )

            layout.addWidget(absent_label)

        else:

            no_attendance = QLabel(
                "No attendance records available for this student."
            )

            no_attendance.setStyleSheet(
                "font-size:14px;padding:12px;color:#9AA9C4;"
            )

            layout.addWidget(no_attendance)

        layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)

    def prepare_profile_table(self, table):

        table.setAlternatingRowColors(True)

        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        table.verticalHeader().setVisible(False)
        # -------------------- MAIN APPLICATION --------------------

class StudentManagementWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Student Hub | Student Management System"
        )

        self.resize(1280, 790)
        self.setMinimumSize(1050, 650)
        self.setStyleSheet(STYLE)

        self.build_interface()
        self.refresh_all()
        self.fade_in()

    # Opening animation
    def fade_in(self):

        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)

        self.animation = QPropertyAnimation(
            self.opacity, b"opacity", self
        )

        self.animation.setDuration(850)
        self.animation.setStartValue(0.15)
        self.animation.setEndValue(1.0)

        self.animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self.animation.start()

    # Build main interface
    def build_interface(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(235)

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(18, 26, 18, 22)

        brand = QLabel("✦ STUDENT HUB")
        brand.setObjectName("Brand")
        side_layout.addWidget(brand)

        subtitle = QLabel(
            "SMART RECORDS • SIMPLE MANAGEMENT"
        )
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        side_layout.addWidget(subtitle)

        side_layout.addSpacing(25)

        self.pages = QStackedWidget()

        navigation = [
            ("▦  Dashboard", 0),
            ("♙  Student Records", 1),
            ("▤  Academic Records", 2),
            ("◷  Student Attendance", 3),
            ("ⓘ  About Project", 4)
        ]

        for text, index in navigation:

            button = QPushButton(text)
            button.setObjectName("NavButton")

            button.clicked.connect(
                lambda checked=False, i=index:
                self.change_page(i)
            )

            side_layout.addWidget(button)

        side_layout.addStretch()

        developer = QLabel(
            "DEVELOPED BY\n"
            "Nima Tashi\n"
            "Roll No: 08230159"
        )

        developer.setStyleSheet("color:#B7C4DE;")
        side_layout.addWidget(developer)

        self.dashboard = self.create_dashboard()
        self.records = self.create_records()
        self.marks_page = self.create_marks()
        self.attendance_page = self.create_attendance()
        self.about = self.create_about()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.records)
        self.pages.addWidget(self.marks_page)
        self.pages.addWidget(self.attendance_page)
        self.pages.addWidget(self.about)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(25, 22, 25, 22)

        topbar = QFrame()
        topbar.setObjectName("Panel")

        top_layout = QHBoxLayout(topbar)

        welcome = QLabel("Students Management Records ✨")
        welcome.setStyleSheet(
            "font-size:17px;font-weight:800;color:#E9E5FF;"
        )

        top_layout.addWidget(welcome)
        top_layout.addStretch()

        status = QLabel("STUDENT ADMINISTRATION")
        status.setObjectName("Muted")
        top_layout.addWidget(status)

        content_layout.addWidget(topbar)
        content_layout.addSpacing(16)
        content_layout.addWidget(self.pages)

        content = QWidget()
        content.setLayout(content_layout)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

    # Page heading
    def page_heading(self, title, subtitle):

        layout = QVBoxLayout()

        heading = QLabel(title)
        heading.setObjectName("PageTitle")

        description = QLabel(subtitle)
        description.setObjectName("Muted")

        layout.addWidget(heading)
        layout.addWidget(description)

        return layout

    # Dashboard card
    def create_card(self, title, accent):

        card = QFrame()
        card.setObjectName("StatCard")

        layout = QVBoxLayout(card)

        label = QLabel(title.upper())
        label.setObjectName("Muted")

        value = QLabel("0")
        value.setStyleSheet(
            f"color:{accent};font-size:27px;font-weight:900;"
        )

        layout.addWidget(label)
        layout.addWidget(value)

        return card, value

    # Dashboard page
    def create_dashboard(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 12, 10, 10)

        layout.addLayout(
            self.page_heading(
                "Dashboard Overview",
                "A quick look at your student records, academic data and attendance."
            )
        )

        layout.addSpacing(18)

        grid = QGridLayout()
        grid.setSpacing(12)

        self.total_card = self.create_card(
            "Total Students", "#A78BFA"
        )

        self.boys_card = self.create_card(
            "Male Students", "#42D6E8"
        )

        self.girls_card = self.create_card(
            "Female Students", "#F08CC8"
        )

        self.average_card = self.create_card(
            "Average Percentage", "#F6C66A"
        )

        self.present_card = self.create_card(
            "Present Records", "#5CE0A0"
        )

        self.absent_card = self.create_card(
            "Absent Records", "#F07878"
        )

        cards = [
            self.total_card,
            self.boys_card,
            self.girls_card,
            self.average_card,
            self.present_card,
            self.absent_card
        ]

        for index, card in enumerate(cards):
            grid.addWidget(card[0], index // 3, index % 3)

        layout.addLayout(grid)
        layout.addSpacing(18)

        panel = QFrame()
        panel.setObjectName("Panel")

        panel_layout = QVBoxLayout(panel)

        title = QLabel("YOUR CONTROL CENTRE")
        title.setStyleSheet(
            "font-size:17px;font-weight:800;color:#C4B5FD;"
        )

        panel_layout.addWidget(title)

        description = QLabel(
            "Manage student profiles, examination results and "
            "daily attendance from one place."
        )

        description.setObjectName("Muted")
        description.setWordWrap(True)
        panel_layout.addWidget(description)

        buttons = QHBoxLayout()

        add_button = QPushButton("＋ Register New Student")
        add_button.clicked.connect(self.add_student)

        view_button = QPushButton("View Student Records →")
        view_button.setObjectName("Secondary")
        view_button.clicked.connect(
            lambda: self.change_page(1)
        )

        attendance_button = QPushButton("Take Attendance")
        attendance_button.setObjectName("Secondary")
        attendance_button.clicked.connect(
            lambda: self.change_page(3)
        )

        buttons.addWidget(add_button)
        buttons.addWidget(view_button)
        buttons.addWidget(attendance_button)

        panel_layout.addLayout(buttons)
        layout.addWidget(panel)
        layout.addStretch()

        return page

    # Student records page
    def create_records(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 12, 10, 10)

        layout.addLayout(
            self.page_heading(
                "Student Records",
                "Register, search, update and manage student profiles."
            )
        )

        layout.addSpacing(15)

        toolbar = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "⌕ Search by Student ID or name..."
        )

        self.search.textChanged.connect(self.search_records)
        toolbar.addWidget(self.search, 2)

        add_button = QPushButton("＋ Add Student")
        add_button.clicked.connect(self.add_student)

        edit_button = QPushButton("✎ Edit")
        edit_button.setObjectName("Secondary")
        edit_button.clicked.connect(self.edit_student)

        delete_button = QPushButton("✕ Delete")
        delete_button.setObjectName("Danger")
        delete_button.clicked.connect(self.delete_student)

        details_button = QPushButton("View Profile")
        details_button.setObjectName("Secondary")
        details_button.clicked.connect(self.view_details)

        toolbar.addWidget(add_button)
        toolbar.addWidget(edit_button)
        toolbar.addWidget(delete_button)
        toolbar.addWidget(details_button)

        layout.addLayout(toolbar)

        self.student_table = QTableWidget(0, 5)

        self.student_table.setHorizontalHeaderLabels([
            "STUDENT ID", "FULL NAME", "GENDER",
            "CLASS", "SECTION"
        ])

        self.prepare_table(self.student_table)
        layout.addWidget(self.student_table)

        return page

    # Academic records page
    def create_marks(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 12, 10, 10)

        layout.addLayout(
            self.page_heading(
                "Academic Records",
                "Review examination marks and student academic performance."
            )
        )

        layout.addSpacing(15)

        toolbar = QHBoxLayout()

        self.academic_filter = QComboBox()
        self.academic_filter.addItem("All Students", None)
        self.academic_filter.currentIndexChanged.connect(
            self.load_marks
        )

        toolbar.addWidget(QLabel("Filter Student:"))
        toolbar.addWidget(self.academic_filter)

        add_button = QPushButton("＋ Add Marks")
        add_button.clicked.connect(self.add_marks)

        edit_button = QPushButton("✎ Edit Marks")
        edit_button.setObjectName("Secondary")
        edit_button.clicked.connect(self.edit_marks)

        delete_button = QPushButton("✕ Delete Marks")
        delete_button.setObjectName("Danger")
        delete_button.clicked.connect(self.delete_marks)

        refresh_button = QPushButton("↻ Refresh")
        refresh_button.setObjectName("Secondary")
        refresh_button.clicked.connect(self.load_marks)

        toolbar.addWidget(add_button)
        toolbar.addWidget(edit_button)
        toolbar.addWidget(delete_button)
        toolbar.addWidget(refresh_button)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        self.academic_average_label = QLabel(
            "Overall Average: Select a student"
        )

        self.academic_average_label.setStyleSheet(
            "font-size:17px;"
            "font-weight:bold;"
            "color:#F6C66A;"
            "padding:10px;"
        )

        layout.addWidget(self.academic_average_label)

        self.marks_table = QTableWidget(0, 7)

        self.marks_table.setHorizontalHeaderLabels([
            "STUDENT ID", "STUDENT NAME", "SUBJECT",
            "MARKS", "TOTAL", "PERCENTAGE", "TERM"
        ])

        self.prepare_table(self.marks_table)
        layout.addWidget(self.marks_table)

        return page

    # Attendance page
    def create_attendance(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 12, 10, 10)

        layout.addLayout(
            self.page_heading(
                "Student Attendance",
                "Record and review daily student attendance."
            )
        )

        layout.addSpacing(15)

        toolbar = QHBoxLayout()

        toolbar.addWidget(QLabel("Attendance Date:"))

        self.attendance_date = QDateEdit()
        self.attendance_date.setCalendarPopup(True)
        self.attendance_date.setDisplayFormat("dd MMM yyyy")
        self.attendance_date.setDate(QDate.currentDate())

        self.attendance_date.dateChanged.connect(
            self.load_attendance
        )

        toolbar.addWidget(self.attendance_date)

        refresh_button = QPushButton("↻ Load Students")
        refresh_button.setObjectName("Secondary")
        refresh_button.clicked.connect(self.load_attendance)

        toolbar.addWidget(refresh_button)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        self.attendance_table = QTableWidget(0, 6)

        self.attendance_table.setHorizontalHeaderLabels([
            "STUDENT ID", "STUDENT NAME", "DATE",
            "CLASS", "SECTION", "ATTENDANCE STATUS"
        ])

        self.prepare_table(self.attendance_table)
        layout.addWidget(self.attendance_table)

        status_layout = QHBoxLayout()

        status_layout.addWidget(QLabel("Select Status:"))

        self.attendance_status = QComboBox()
        self.attendance_status.addItems([
            "Present", "Absent", "Late"
        ])

        status_layout.addWidget(self.attendance_status)

        save_button = QPushButton("Save Attendance ✓")
        save_button.clicked.connect(self.save_selected_attendance)

        status_layout.addWidget(save_button)

        present_button = QPushButton("Mark Present")
        present_button.setObjectName("Secondary")
        present_button.clicked.connect(
            lambda: self.mark_selected("Present")
        )

        absent_button = QPushButton("Mark Absent")
        absent_button.setObjectName("Danger")
        absent_button.clicked.connect(
            lambda: self.mark_selected("Absent")
        )

        late_button = QPushButton("Mark Late")
        late_button.setObjectName("Secondary")
        late_button.clicked.connect(
            lambda: self.mark_selected("Late")
        )

        status_layout.addWidget(present_button)
        status_layout.addWidget(absent_button)
        status_layout.addWidget(late_button)

        layout.addLayout(status_layout)

        note = QLabel(
            "Select a student from the table, then choose or click an attendance status."
        )
        note.setObjectName("Muted")
        layout.addWidget(note)

        return page

    # About page
    def create_about(self):

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 12, 10, 10)

        layout.addLayout(
            self.page_heading(
                "About This Project",
                "Project information and developer details."
            )
        )

        layout.addSpacing(18)

        panel = QFrame()
        panel.setObjectName("Panel")

        panel_layout = QVBoxLayout(panel)

        details = [
            "✦ STUDENT MANAGEMENT RECORDS SYSTEM",
            "Developer: Nima Tashi",
            "Roll Number: 08230159",
            "Programme: B.Ed. IT",
            "Framework: PyQt6",
            "Database: SQLite",
            "Instructor: Mr. Anup Gurung",
            "Purpose: To manage student profiles, academic marks and attendance."
        ]

        for detail in details:

            label = QLabel(detail)
            label.setStyleSheet(
                "font-size:16px;padding:7px;color:#E6EAF7;"
            )

            panel_layout.addWidget(label)

        layout.addWidget(panel)
        layout.addStretch()

        return page

    # Table formatting
    def prepare_table(self, table):

        table.setAlternatingRowColors(True)

        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        table.verticalHeader().setVisible(False)

    # Page navigation
    def change_page(self, index):

        self.pages.setCurrentIndex(index)

        if index == 1:
            self.load_students()

        elif index == 2:
            self.refresh_academic_filter()
            self.load_marks()

        elif index == 3:
            self.load_attendance()

        elif index == 0:
            self.update_dashboard()

    # Refresh all information
    def refresh_all(self):

        self.load_students()
        self.refresh_academic_filter()
        self.load_marks()
        self.load_attendance()
        self.update_dashboard()

    # Load student records
    def load_students(self):

        self.show_students(logic.get_students())

    def show_students(self, students):

        self.student_table.setRowCount(len(students))

        for row, student in enumerate(students):

            for column in range(5):

                item = QTableWidgetItem(str(student[column]))

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.student_table.setItem(
                    row, column, item
                )

    # Search students
    def search_records(self):

        results = logic.search_student(
            self.search.text().strip()
        )

        self.show_students(results)

    # Get selected student
    def selected_student(self):

        row = self.student_table.currentRow()

        if row < 0:

            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a student record first."
            )

            return None

        student_id = self.student_table.item(row, 0).text()

        return next(
            (
                student for student in logic.get_students()
                if str(student[0]) == str(student_id)
            ),
            None
        )

    # Add student
    def add_student(self):

        dialog = StudentDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:

            success, message = logic.add_student(
                dialog.get_data()
            )

            if success:

                QMessageBox.information(
                    self, "Registration Successful",
                    "✓ " + message
                )

                self.refresh_all()

            else:

                QMessageBox.warning(
                    self, "Unable to Save Record", message
                )

    # Edit student
    def edit_student(self):

        student = self.selected_student()

        if student is None:
            return

        dialog = StudentDialog(self, student)

        if dialog.exec() == QDialog.DialogCode.Accepted:

            success, message = logic.update_student(
                dialog.get_data(),
                dialog.get_original_student_id()
            )

            if success:

                QMessageBox.information(
                    self, "Update Successful", message
                )

                self.refresh_all()

            else:

                QMessageBox.warning(
                    self, "Update Failed", message
                )

    # Delete student
    def delete_student(self):

        student = self.selected_student()

        if student is None:
            return

        answer = QMessageBox.question(
            self,
            "Confirm Student Deletion",
            f"Are you sure you want to delete {student[1]}?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer == QMessageBox.StandardButton.Yes:

            success, message = logic.delete_student(student[0])

            if success:

                QMessageBox.information(
                    self, "Record Deleted", message
                )

                self.refresh_all()

            else:

                QMessageBox.critical(
                    self, "Delete Failed", message
                )

    # View complete student profile
    def view_details(self):

        student = self.selected_student()

        if student is None:
            return

        dialog = ProfileDialog(self, student)
        dialog.exec()

    # Add marks
    def add_marks(self):

        dialog = MarksDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        student_id, subject, marks, total, term = dialog.get_data()

        try:

            success, message = logic.add_marks(
                student_id, subject, marks, total, term
            )

            if success:

                QMessageBox.information(
                    self,
                    "Marks Saved",
                    message
                )

                self.refresh_all()

            else:

                QMessageBox.warning(
                    self, "Unable to Save Marks", message
                )

        except Exception as error:

            QMessageBox.critical(
                self, "Database Error", str(error)
            )

    # Get selected marks record
    def selected_mark(self):

        row = self.marks_table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a subject record first."
            )
            return None

        item = self.marks_table.item(row, 0)

        if item is None:
            return None

        mark_id = item.data(Qt.ItemDataRole.UserRole)

        if mark_id is None:
            QMessageBox.warning(
                self,
                "Invalid Selection",
                "Please select a subject row, not a student heading."
            )
            return None

        try:

            with database.connect_db() as connection:

                record = connection.execute("""
                    SELECT id, student_id, subject,
                           marks, total, term
                    FROM marks
                    WHERE id = ?
                """, (mark_id,)).fetchone()

            if record is None:
                QMessageBox.warning(
                    self,
                    "Record Not Found",
                    "This marks record no longer exists. Please refresh."
                )
                self.load_marks()
                return None

            return record

        except Exception as error:

            QMessageBox.critical(
                self, "Database Error", str(error)
            )
            return None

    # Edit existing marks
    def edit_marks(self):

        record = self.selected_mark()

        if record is None:
            return

        dialog = MarksDialog(self, record)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        student_id, subject, marks, total, term = dialog.get_data()

        try:

            success, message = logic.update_marks(
                record[0],
                student_id,
                subject,
                marks,
                total,
                term
            )

            if success:

                QMessageBox.information(
                    self,
                    "Marks Updated",
                    message
                )

                self.refresh_all()

            else:

                QMessageBox.warning(
                    self,
                    "Update Failed",
                    message
                )

        except Exception as error:

            QMessageBox.critical(
                self, "Database Error", str(error)
            )

    # Delete existing marks
    def delete_marks(self):

        record = self.selected_mark()

        if record is None:
            return

        answer = QMessageBox.question(
            self,
            "Confirm Marks Deletion",
            f"Delete {record[2]} marks for Student {record[1]}?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:

            success, message = logic.delete_marks(record[0])

            if success:

                QMessageBox.information(
                    self,
                    "Marks Deleted",
                    message
                )

                self.refresh_all()

            else:

                QMessageBox.warning(
                    self,
                    "Delete Failed",
                    message
                )

        except Exception as error:

            QMessageBox.critical(
                self, "Database Error", str(error)
            )

    # Update academic filter
    def refresh_academic_filter(self):

        if not hasattr(self, "academic_filter"):
            return

        current_id = self.academic_filter.currentData()

        self.academic_filter.blockSignals(True)
        self.academic_filter.clear()
        self.academic_filter.addItem("All Students", None)

        for student in logic.get_students():

            self.academic_filter.addItem(
                f"{student[0]} - {student[1]}",
                student[0]
            )

        index = self.academic_filter.findData(current_id)

        if index >= 0:
            self.academic_filter.setCurrentIndex(index)

        self.academic_filter.blockSignals(False)

    # Display academic records student by student
    def load_marks(self):

        if not hasattr(self, "marks_table"):
            return

        try:

            selected_id = self.academic_filter.currentData()

            with database.connect_db() as connection:

                if selected_id is None:

                    rows = connection.execute("""
                        SELECT marks.id,
                               marks.student_id,
                               students.name,
                               marks.subject,
                               marks.marks,
                               marks.total,
                               marks.term
                        FROM marks
                        JOIN students
                            ON students.student_id = marks.student_id
                        ORDER BY students.name, marks.term, marks.subject
                    """).fetchall()

                else:

                    rows = connection.execute("""
                        SELECT marks.id,
                               marks.student_id,
                               students.name,
                               marks.subject,
                               marks.marks,
                               marks.total,
                               marks.term
                        FROM marks
                        JOIN students
                            ON students.student_id = marks.student_id
                        WHERE marks.student_id = ?
                        ORDER BY marks.term, marks.subject
                    """, (selected_id,)).fetchall()

            student_records = {}

            for record in rows:

                mark_id, student_id, name, subject, marks, total, term = record

                if student_id not in student_records:
                    student_records[student_id] = {
                        "name": name,
                        "records": [],
                        "marks": 0,
                        "total": 0
                    }

                student_records[student_id]["records"].append(record)
                student_records[student_id]["marks"] += marks
                student_records[student_id]["total"] += total

            table_row_count = sum(
                1 + len(student_data["records"])
                for student_data in student_records.values()
            )

            self.marks_table.clearSpans()
            self.marks_table.setRowCount(0)
            self.marks_table.setRowCount(table_row_count)

            overall_marks = 0
            overall_total = 0
            current_row = 0

            for student_id, student_data in student_records.items():

                name = student_data["name"]
                records = student_data["records"]

                student_marks = student_data["marks"]
                student_total = student_data["total"]

                student_average = (
                    student_marks / student_total * 100
                    if student_total else 0
                )

                overall_marks += student_marks
                overall_total += student_total

                heading_item = QTableWidgetItem(
                    f"STUDENT: {student_id} - {name}     "
                    f"OVERALL AVERAGE: {student_average:.1f}%"
                )

                heading_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft |
                    Qt.AlignmentFlag.AlignVCenter
                )

                heading_item.setBackground(Qt.GlobalColor.darkBlue)
                heading_item.setForeground(Qt.GlobalColor.white)

                self.marks_table.setItem(
                    current_row, 0, heading_item
                )

                self.marks_table.setSpan(
                    current_row, 0, 1, 7
                )

                current_row += 1

                for record in records:

                    mark_id, student_id, name, subject, marks, total, term = record

                    percentage = (
                        marks / total * 100 if total else 0
                    )

                    values = [
                        student_id,
                        name,
                        subject,
                        marks,
                        total,
                        f"{percentage:.1f}%",
                        term
                    ]

                    for column, value in enumerate(values):

                        item = QTableWidgetItem(str(value))

                        item.setTextAlignment(
                            Qt.AlignmentFlag.AlignCenter
                        )

                        if column == 0:
                            item.setData(
                                Qt.ItemDataRole.UserRole,
                                mark_id
                            )

                        self.marks_table.setItem(
                            current_row, column, item
                        )

                    current_row += 1

            if overall_total > 0:

                overall_average = (
                    overall_marks / overall_total
                ) * 100

                if selected_id is not None:

                    student_name = (
                        next(iter(student_records.values()))["name"]
                        if student_records else ""
                    )

                    self.academic_average_label.setText(
                        f"{student_name} - Overall Average: "
                        f"{overall_average:.1f}% "
                        f"({len(rows)} subject records)"
                    )

                else:

                    self.academic_average_label.setText(
                        f"All Students - Overall Average: "
                        f"{overall_average:.1f}%"
                    )

            else:

                if selected_id is not None:

                    self.academic_average_label.setText(
                        "No academic marks recorded for this student."
                    )

                else:

                    self.academic_average_label.setText(
                        "No academic marks recorded yet."
                    )

        except Exception as error:

            QMessageBox.warning(
                self, "Database Error", str(error)
            )

            self.marks_table.clearSpans()
            self.marks_table.setRowCount(0)
                # Load attendance records for selected date
    def load_attendance(self):

        if not hasattr(self, "attendance_table"):
            return

        selected_date = self.attendance_date.date().toString(
            "yyyy-MM-dd"
        )

        display_date = self.attendance_date.date().toString(
            "dd MMM yyyy"
        )

        try:

            records = database.get_attendance_by_date(
                selected_date
            )

            self.attendance_table.setRowCount(len(records))

            for row, record in enumerate(records):

                student_id, name, class_name, section, status = record

                values = [
                    student_id,
                    name,
                    display_date,
                    class_name,
                    section,
                    status if status else "Not Marked"
                ]

                for column, value in enumerate(values):

                    item = QTableWidgetItem(str(value))

                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                    self.attendance_table.setItem(
                        row, column, item
                    )

        except Exception as error:

            QMessageBox.warning(
                self, "Attendance Error", str(error)
            )

    # Save attendance for selected student
    def save_selected_attendance(self):

        row = self.attendance_table.currentRow()

        if row < 0:

            QMessageBox.warning(
                self, "No Selection",
                "Please select a student first."
            )
            return

        student_id = self.attendance_table.item(row, 0).text()

        selected_date = self.attendance_date.date().toString(
            "yyyy-MM-dd"
        )

        status = self.attendance_status.currentText()

        try:

            database.save_attendance(
                student_id, selected_date, status
            )

            QMessageBox.information(
                self,
                "Attendance Saved",
                f"{student_id}: marked as {status}."
            )

            self.load_attendance()
            self.update_dashboard()

        except Exception as error:

            QMessageBox.critical(
                self, "Attendance Error", str(error)
            )

    # Quick attendance buttons
    def mark_selected(self, status):

        self.attendance_status.setCurrentText(status)
        self.save_selected_attendance()

    # Update dashboard figures
    def update_dashboard(self):

        students = logic.get_students()

        self.total_card[1].setText(str(len(students)))

        boys = sum(
            1 for student in students
            if student[2] == "Male"
        )

        girls = sum(
            1 for student in students
            if student[2] == "Female"
        )

        self.boys_card[1].setText(str(boys))
        self.girls_card[1].setText(str(girls))

        try:

            with database.connect_db() as connection:

                result = connection.execute(
                    "SELECT SUM(marks), SUM(total) FROM marks"
                ).fetchone()

            if result and result[1]:

                average = (result[0] / result[1]) * 100

                self.average_card[1].setText(
                    f"{average:.1f}%"
                )

            else:

                self.average_card[1].setText("N/A")

        except Exception:

            self.average_card[1].setText("N/A")

        try:

            summary = database.get_attendance_summary()

            total_records, present, absent, late = summary

            self.present_card[1].setText(str(present))
            self.absent_card[1].setText(str(absent))

        except Exception:

            self.present_card[1].setText("0")
            self.absent_card[1].setText("0")


# -------------------- RUN APPLICATION --------------------

if __name__ == "__main__":

    database.create_tables()

    app = QApplication(sys.argv)

    window = StudentManagementWindow()
    window.show()

    sys.exit(app.exec())