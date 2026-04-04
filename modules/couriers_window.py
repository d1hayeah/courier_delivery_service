import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox
from database.get_connection import get_connection
from utils.report import save_table

class CouriersApp(QWidget):
    def __init__(self, user_role="user"):
        super().__init__()
        self.user_role = user_role
        self.setWindowTitle(f"Курьеры (Роль: {user_role})")
        self.resize(600, 450)
        self.selected_id = None
        main_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон", "Статус"])
        self.table.cellClicked.connect(self.select_row)
        main_layout.addWidget(self.table)
        
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("ФИО:"))
        self.name_input = QLineEdit()
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(QLabel("Телефон:"))
        self.phone_input = QLineEdit()
        form_layout.addWidget(self.phone_input)
        form_layout.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Свободен", "На маршруте"])
        form_layout.addWidget(self.status_combo)
        main_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Дoбавить")
        self.add_btn.clicked.connect(self.add_courier)
        btn_layout.addWidget(self.add_btn)
        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_courier)
        btn_layout.addWidget(self.update_btn)
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_courier)
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
            self.status_combo.setEnabled(False)
            self.name_input.setReadOnly(True)
            self.phone_input.setReadOnly(True)
        self.load_data()

    def load_data(self):
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT id, fullname, phone, status FROM couriers ORDER BY id;")
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
        self.name_input.setText(self.table.item(row, 1).text())
        self.phone_input.setText(self.table.item(row, 2).text())
        status = self.table.item(row, 3).text()
        idx = self.status_combo.findText(status)
        if idx >= 0: self.status_combo.setCurrentIndex(idx)

    def clear_form(self):
        self.name_input.clear()
        self.phone_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.selected_id = None
        QMessageBox.information(self, "Успех", "Форма очищена")

    def add_courier(self):
        if self.user_role != "admin": return
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        status = self.status_combo.currentText()
        if not name or not phone:
            QMessageBox.warning(self, "Ошибка", "Введите ФИО и телефон!")
            return
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO couriers (fullname, phone, status) VALUES (%s, %s, %s);", (name, phone, status))
            conn.commit()
            QMessageBox.information(self, "Успех", "Курьер добавлен")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_courier(self):
        if self.user_role != "admin": return
        if not self.selected_id: return
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        status = self.status_combo.currentText()
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE couriers SET fullname = %s, phone = %s, status = %s WHERE id = %s;", (name, phone, status, self.selected_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Данные обновлены")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_courier(self):
        if self.user_role != "admin": return
        if not self.selected_id: return
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM couriers WHERE id = %s;", (self.selected_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "Курьер удален")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()