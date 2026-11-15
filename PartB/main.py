import sys

from PyQt6.QtWidgets import QApplication
from database import create_tables
from ui import StudentManagementWindow


if __name__ == "__main__":

    # Create database tables
    create_tables()

    # Start the application
    app = QApplication(sys.argv)

    window = StudentManagementWindow()
    window.show()

    sys.exit(app.exec())
