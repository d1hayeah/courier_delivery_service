import sys
import hashlib
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database.get_connection import get_connection

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.resize(300, 180)
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Логин:"))
        self.input_login = QLineEdit()
        layout.addWidget(self.input_login)
        
        layout.addWidget(QLabel("Пароль:"))
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)
        
        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.check_login)
        layout.addWidget(self.btn_login)
        
        self.btn_register = QPushButton("Регистрация")
        self.btn_register.clicked.connect(self.open_register)
        layout.addWidget(self.btn_register)
        
        self.setLayout(layout)

    def open_register(self):
        from .register_window import RegisterWindow
        self.reg_win = RegisterWindow()
        self.reg_win.show()

    def check_login(self):
        username = self.input_login.text().strip()
        password = self.input_password.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return
        
        hashed = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE username = %s AND password = %s;", (username, hashed))
        user = cursor.fetchone()
        if not user:
            cursor.execute("SELECT id, username, role FROM users WHERE username = %s AND password = %s;", (username, password))
            user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user:
            user_id, db_username, role = user
            from modules.menu_window import MenuWindow
            self.hide()
            self.menu = MenuWindow(db_username, role, user_id)
            self.menu.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

if __name__ == "__main__":
    from database.get_connection import ensure_tables
    ensure_tables()
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
