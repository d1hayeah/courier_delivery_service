import sys
import hashlib
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database.get_connection import get_connection

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.resize(300, 200)
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Логин:"))
        self.input_login = QLineEdit()
        layout.addWidget(self.input_login)
        
        layout.addWidget(QLabel("Пароль:"))
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)
        
        self.btn_register = QPushButton("Зарегистрироваться")
        self.btn_register.clicked.connect(self.register_user)
        layout.addWidget(self.btn_register)
        self.setLayout(layout)

    def register_user(self):
        username = self.input_login.text().strip()
        password = self.input_password.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return
        
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет связи с БД")
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE username = %s;", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь уже существует!")
                return
            
            hashed = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s);", (username, hashed, 'user'))
            conn.commit()
            QMessageBox.information(self, "Успех", "Регистрация успешна!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()