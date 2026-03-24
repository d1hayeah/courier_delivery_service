import sys
import random
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDoubleSpinBox
from database.get_connection import get_connection
from utils.report import save_table

class OrdersWindow(QWidget):
    def __init__(self, user_role="user"):
        super().__init__()
        self.user_role = user_role
        self.setWindowTitle(f"Заказы (Роль: {user_role})")
        self.resize(800, 600)
        self.selected_id = None
        main_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Трекинг", "Отправитель", "Получатель", "Статус"])
        self.table.cellClicked.connect(self.select_row)
        main_layout.addWidget(self.table)
        
        form_layout = QVBoxLayout()
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Отправитель:"))
        self.sender_name = QLineEdit()
        h1.addWidget(self.sender_name)
        h1.addWidget(QLabel("Телефон:"))
        self.sender_phone = QLineEdit()
        h1.addWidget(self.sender_phone)
        form_layout.addLayout(h1)
        
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Адрес отправителя:"))
        self.sender_addr = QLineEdit()
        h2.addWidget(self.sender_addr)
        form_layout.addLayout(h2)
        
        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Получатель:"))
        self.receiver_name = QLineEdit()
        h3.addWidget(self.receiver_name)
        h3.addWidget(QLabel("Телефон:"))
        self.receiver_phone = QLineEdit()
        h3.addWidget(self.receiver_phone)
        form_layout.addLayout(h3)
        
        h4 = QHBoxLayout()
        h4.addWidget(QLabel("Адрес получателя:"))
        self.receiver_addr = QLineEdit()
        h4.addWidget(self.receiver_addr)
        form_layout.addLayout(h4)
        
        h5 = QHBoxLayout()
        h5.addWidget(QLabel("Вес (кг):"))
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0.1, 1000)
        h5.addWidget(self.weight_input)
        h5.addWidget(QLabel("Габариты:"))
        self.dim_input = QLineEdit()
        h5.addWidget(self.dim_input)
        h5.addWidget(QLabel("Ценность:"))
        self.value_input = QDoubleSpinBox()
        h5.addWidget(self.value_input)
        form_layout.addLayout(h5)
        
        h6 = QHBoxLayout()
        h6.addWidget(QLabel("Стоимость:"))
        self.cost_input = QLineEdit()
        self.cost_input.setReadOnly(True)
        h6.addWidget(self.cost_input)
        btn_calc = QPushButton("Расчет")
        btn_calc.clicked.connect(self.calc_cost)
        h6.addWidget(btn_calc)
        h6.addWidget(QLabel("Курьер:"))
        self.courier_combo = QComboBox()
        h6.addWidget(self.courier_combo)
        form_layout.addLayout(h6)
        
        h7 = QHBoxLayout()
        h7.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Принят", "Передан курьеру", "В пути", "Доставлен", "Отменен"])
        h7.addWidget(self.status_combo)
        form_layout.addLayout(h7)
        
        main_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Создать")
        self.add_btn.clicked.connect(self.add_order)
        btn_layout.addWidget(self.add_btn)
        self.update_btn = QPushButton("Изменить")
        self.update_btn.clicked.connect(self.update_order)
        btn_layout.addWidget(self.update_btn)
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_order)
        btn_layout.addWidget(self.delete_btn)
        self.export_btn = QPushButton("Отчёт")
        self.export_btn.clicked.connect(lambda: save_table(self.table, parent=self))
        btn_layout.addWidget(self.export_btn)
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
        if self.user_role != "admin":
            self.add_btn.setEnabled(False)
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.courier_combo.setEnabled(False)
            self.status_combo.setEnabled(False)
        self.load_couriers()
        self.load_data()

    def load_couriers(self):
        self.courier_combo.clear()
        self.courier_combo.addItem("Не назначен", None)
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT id, fullname FROM couriers WHERE status = 'Свободен';")
        for r in cursor.fetchall():
            self.courier_combo.addItem(r[1], r[0])
        cursor.close()
        conn.close()

    def calc_cost(self):
        weight = self.weight_input.value()
        value = self.value_input.value()
        cost = weight * 150 + value * 0.02
        self.cost_input.setText(f"{cost:.2f}")

    def load_data(self):
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT id, tracking_number, sender_name, receiver_name, status FROM orders ORDER BY id DESC;")
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
        QMessageBox.information(self, "Инфо", f"Выбран заказ ID: {self.selected_id}")

    def add_order(self):
        if self.user_role != "admin": return
        tracking = f"TRK-{random.randint(10000,99999)}"
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO orders (tracking_number, sender_name, sender_address, sender_phone, 
                receiver_name, receiver_address, receiver_phone, weight, dimensions, declared_value, cost, status, courier_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                tracking, self.sender_name.text(), self.sender_addr.text(), self.sender_phone.text(),
                self.receiver_name.text(), self.receiver_addr.text(), self.receiver_phone.text(),
                self.weight_input.value(), self.dim_input.text(), self.value_input.value(), 
                self.cost_input.text(), self.status_combo.currentText(), self.courier_combo.currentData()
            ))
            conn.commit()
            QMessageBox.information(self, "Успех", "Заказ создан")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_order(self):
        if self.user_role != "admin": return
        if not self.selected_id: return
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT status FROM orders WHERE id = %s;", (self.selected_id,))
            old_status = cursor.fetchone()[0]
            new_status = self.status_combo.currentText()
            
            cursor.execute("""
                UPDATE orders SET sender_name=%s, sender_address=%s, sender_phone=%s,
                receiver_name=%s, receiver_address=%s, receiver_phone=%s, weight=%s,
                dimensions=%s, declared_value=%s, cost=%s, status=%s, courier_id=%s
                WHERE id=%s
            """, (
                self.sender_name.text(), self.sender_addr.text(), self.sender_phone.text(),
                self.receiver_name.text(), self.receiver_addr.text(), self.receiver_phone.text(),
                self.weight_input.value(), self.dim_input.text(), self.value_input.value(),
                self.cost_input.text(), new_status, self.courier_combo.currentData(), self.selected_id
            ))
            
            if old_status != new_status:
                cursor.execute("INSERT INTO order_history (order_id, old_status, new_status) VALUES (%s, %s, %s);",
                               (self.selected_id, old_status, new_status))
            
            conn.commit()
            QMessageBox.information(self, "Успех", "Заказ обновлен")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_order(self):
        if self.user_role != "admin": return
        if not self.selected_id: return
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM orders WHERE id = %s;", (self.selected_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "Заказ удален")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()