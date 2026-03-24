import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QComboBox, QDialog, QTextEdit
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
        self.filter_status.addItem("Все", "")
        self.filter_status.addItems(["Принят", "Передан курьеру", "В пути", "Доставлен", "Отменен"])
        filter_layout.addWidget(QLabel("Статус:"))
        filter_layout.addWidget(self.filter_status)
        
        self.filter_courier = QComboBox()
        self.filter_courier.addItem("Все", None)
        filter_layout.addWidget(QLabel("Курьер:"))
        filter_layout.addWidget(self.filter_courier)
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("Дата с:"))
        filter_layout.addWidget(self.date_from)
        
        self.filter_btn = QPushButton("Фильтр")
        self.filter_btn.clicked.connect(self.load_filtered_data)
        filter_layout.addWidget(self.filter_btn)
        main_layout.addLayout(filter_layout)
        
        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton("Сохранить отчёт")
        self.export_btn.clicked.connect(lambda: save_table(self.table, parent=self))
        btn_layout.addWidget(self.export_btn)
        main_layout.addLayout(btn_layout)
        
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

    def load_filtered_data(self):
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        status = self.filter_status.currentData()
        courier_id = self.filter_courier.currentData()
        date_from = self.date_from.date().toString("YYYY-MM-DD")
        
        query = """
            SELECT o.id, o.tracking_number, o.status, c.fullname, o.created_at, o.cost 
            FROM orders o LEFT JOIN couriers c ON o.courier_id = c.id WHERE 1=1
        """
        params = []
        if status:
            query += " AND o.status = %s"
            params.append(status)
        if courier_id:
            query += " AND o.courier_id = %s"
            params.append(courier_id)
        if date_from:
            query += " AND o.created_at >= %s"
            params.append(date_from)
        
        cursor.execute(query, params)
        self.fill_table(cursor.fetchall())
        cursor.close()
        conn.close()
        QMessageBox.information(self, "Отчёт", "Данные отфильтрованы")

    def search_order(self):
        track = self.search_input.text().strip()
        if not track: return
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.tracking_number, o.status, o.created_at, c.fullname 
            FROM orders o LEFT JOIN couriers c ON o.courier_id = c.id WHERE o.tracking_number = %s
        """, (track,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        self.table.setRowCount(0)
        if row:
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