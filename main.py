import sys
from PyQt5.QtWidgets import QApplication
from database.get_connection import ensure_tables
from auth.login_window import LoginWindow

if __name__ == "__main__":
    ensure_tables()
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())