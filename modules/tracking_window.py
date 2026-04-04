import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QDialog, QTextEdit
from PyQt5.QtCore import QDate
from database.get_connection import get_connection
from utils.report import save_table

class HistoryDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"История заказа #{order_id}")
        self.resize(400, 300)
        layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)
        self.setLayout(layout)
        
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT old_status, new_status, changed_at FROM order_history WHERE order_id = %s ORDER BY changed_at DESC", (order_id,))
            rows = cursor.fetchall()
            history_text = "Дата\t\t\tБыло\t\t\tСтало\n"
            for r in rows:
                history_text += f"{r[2]}\t{r[0]}\t{r[1]}\n"
            self.text.setText(history_text)
            cursor.close()
            conn.close()

class TrackingWindow(QWidget):
    def __init__(self, user_role="user"):
        super().__init__()
        self.user_role = user_role
        self.setWindowTitle(f"Отслеживание и Отчёты (Роль: {user_role})")
        self.resize(800, 600)
        main_layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Трекинг-номер:"))
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input)
        self.search_btn = QPushButton("Найти")
        self.search_btn.clicked.connect(self.search_order)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Трекинг", "Статус", "Курьер", "Дата", "Стоимость"])
        main_layout.addWidget(self.table)
        
        filter_layout = QHBoxLayout()
        self.filter_status = QComboBox()
        self.filter_status.addItem("Все", None)
        self.filter_status.addItem("Принят", "Принят")
        self.filter_status.addItem("Передан курьеру", "Передан курьеру")
        self.filter_status.addItem("В пути", "В пути")
        self.filter_status.addItem("Доставлен", "Доставлен")
        self.filter_status.addItem("Отменен", "Отменен")
        filter_layout.addWidget(QLabel("Статус:"))
        filter_layout.addWidget(self.filter_status)
        
        self.filter_courier = QComboBox()
        self.filter_courier.addItem("Все", None)
        filter_layout.addWidget(QLabel("Курьер:"))
        filter_layout.addWidget(self.filter_courier)
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-7))  # По умолчанию неделя назад
        filter_layout.addWidget(QLabel("Дата с:"))
        filter_layout.addWidget(self.date_from)
        
        self.filter_btn = QPushButton("Применить фильтры")
        self.filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.filter_btn)
        
        self.reset_btn = QPushButton("Сбросить фильтры")
        self.reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_btn)
        
        main_layout.addLayout(filter_layout)
        
        self.setLayout(main_layout)
        self.load_couriers_to_filter()
        self.load_data()

    def load_couriers_to_filter(self):
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT id, fullname FROM couriers ORDER BY fullname;")
        for r in cursor.fetchall():
            self.filter_courier.addItem(r[1], r[0])
        cursor.close()
        conn.close()

    def load_data(self):
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.tracking_number, o.status, c.fullname, o.created_at, o.cost 
            FROM orders o LEFT JOIN couriers c ON o.courier_id = c.id ORDER BY o.id DESC
        """)
        self.fill_table(cursor.fetchall())
        cursor.close()
        conn.close()

    def fill_table(self, rows):
        self.table.setRowCount(0)
        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))

    def apply_filters(self):
        status_filter = self.filter_status.currentData()
        courier_id = self.filter_courier.currentData()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        
        query = """
            SELECT o.id, o.tracking_number, o.status, c.fullname, o.created_at, o.cost 
            FROM orders o LEFT JOIN couriers c ON o.courier_id = c.id 
            WHERE 1=1
        """
        params = []
        
        if status_filter:
            query += " AND o.status = %s"
            params.append(status_filter)
        
        if courier_id:
            query += " AND o.courier_id = %s"
            params.append(courier_id)
        
        # Фильтр по дате - только если выбрана дата не равная минимальной
        if date_from and date_from != "2000-01-01":  # Минимальная дата Qt
            query += " AND DATE(o.created_at) >= %s"
            params.append(date_from)
        
        query += " ORDER BY o.id DESC"
        
        cursor.execute(query, params)
        self.fill_table(cursor.fetchall())
        cursor.close()
        conn.close()
        
        QMessageBox.information(self, "Фильтры применены", f"Найдено записей: {self.table.rowCount()}")

    def reset_filters(self):
        self.filter_status.setCurrentIndex(0)
        self.filter_courier.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.load_data()
        QMessageBox.information(self, "Фильтры сброшены", "Показаны все записи")

    def search_order(self):
        track = self.search_input.text().strip()
        if not track: return
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.tracking_number, o.status, c.fullname, o.created_at, o.cost 
            FROM orders o LEFT JOIN couriers c ON o.courier_id = c.id WHERE o.tracking_number = %s
        """, (track,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            self.table.setRowCount(0)
            self.table.insertRow(0)
            for c_idx, val in enumerate(row):
                self.table.setItem(0, c_idx, QTableWidgetItem(str(val)))
            self.show_history(row[0])
            QMessageBox.information(self, "Найдено", f"Заказ {track} найден. История открыта.")
        else:
            QMessageBox.warning(self, "Не найдено", "Заказ не найден")

    def show_history(self, order_id):
        dialog = HistoryDialog(order_id, self)
        dialog.exec_()