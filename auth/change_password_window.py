import sys
import hashlib
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database.get_connection import get_connection

class ChangePasswordWindow(QWidget):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.setWindowTitle(f"Смена пароля ({username})")
        self.resize(300, 200)
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Старый пароль:"))
        self.old_pass = QLineEdit()
        self.old_pass.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_pass)
        
        layout.addWidget(QLabel("Новый пароль:"))
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_pass)
        
        layout.addWidget(QLabel("Повторите пароль:"))
        self.confirm_pass = QLineEdit()
        self.confirm_pass.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_pass)
        
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self.change_password)
        layout.addWidget(self.btn_save)
        self.setLayout(layout)

    def change_password(self):
        old_p = self.old_pass.text().strip()
        new_p = self.new_pass.text().strip()
        conf_p = self.confirm_pass.text().strip()
        
        if not old_p or not new_p or not conf_p:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        if new_p != conf_p:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return
            
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            hashed_old = hashlib.sha256(old_p.encode()).hexdigest()
            cursor.execute("SELECT id FROM users WHERE id = %s AND password = %s;", (self.user_id, hashed_old))
            if not cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Неверный старый пароль!")
                return
            
            hashed_new = hashlib.sha256(new_p.encode()).hexdigest()
            cursor.execute("UPDATE users SET password = %s WHERE id = %s;", (hashed_new, self.user_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Пароль изменен!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()