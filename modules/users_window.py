import sys
import hashlib
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox
from database.get_connection import get_connection
from utils.report import save_table

class UsersWindow(QWidget):
    def __init__(self, user_role="user"):
        super().__init__()
        self.user_role = user_role
        self.setWindowTitle("Управление пользователями")
        self.resize(600, 450)
        self.selected_id = None
        
        main_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Логин", "Роль"])
        self.table.cellClicked.connect(self.select_row)
        main_layout.addWidget(self.table)
        
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        form_layout.addWidget(self.login_input)
        form_layout.addWidget(QLabel("Роль:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        form_layout.addWidget(self.role_combo)
        main_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_user)
        btn_layout.addWidget(self.add_btn)
        
        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_user)
        btn_layout.addWidget(self.update_btn)
        
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_user)
        btn_layout.addWidget(self.delete_btn)
        
        self.clear_btn = QPushButton("Очистить форму")
        self.clear_btn.clicked.connect(self.clear_form)
        btn_layout.addWidget(self.clear_btn)
        
        self.export_btn = QPushButton("Отчёт")
        self.export_btn.clicked.connect(lambda: save_table(self.table, parent=self))
        btn_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        
        if self.user_role != "admin":
            self.add_btn.setEnabled(False)
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.login_input.setReadOnly(True)
        self.load_data()

    def load_data(self):
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users ORDER BY id;")
        rows = cursor.fetchall()
        self.table.setRowCount(0)
        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
        cursor.close()
        conn.close()

    def select_row(self, row, column):
        self.selected_id = self.table.item(row, 0).text()
        self.login_input.setText(self.table.item(row, 1).text())
        role = self.table.item(row, 2).text()
        idx = self.role_combo.findText(role)
        if idx >= 0: self.role_combo.setCurrentIndex(idx)

    def clear_form(self):
        self.login_input.clear()
        self.role_combo.setCurrentIndex(0)
        self.selected_id = None
        QMessageBox.information(self, "Успех", "Форма очищена")

    def add_user(self):
        if self.user_role != "admin": return
        login = self.login_input.text().strip()
        role = self.role_combo.currentText()
        if not login:
            QMessageBox.warning(self, "Ошибкa", "Введите логин!")
            return
        hashed = hashlib.sha256("1234".encode()).hexdigest()
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s);", (login, hashed, role))
            conn.commit()
            QMessageBox.information(self, "Успех", "Пользователь добавлен (пароль: 1234)")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_user(self):
        if self.user_role != "admin": return
        if not self.selected_id: return
        role = self.role_combo.currentText()
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET role = %s WHERE id = %s;", (role, self.selected_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Роль обновлена")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_user(self):
        if self.user_role != "admin": return
        if not self.selected_id: return
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = %s;", (self.selected_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "Пользователь удален")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()