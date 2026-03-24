import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from couriers_window import CouriersApp
from orders_window import OrdersWindow
from tracking_window import TrackingWindow
from users_window import UsersWindow
from auth.change_password_window import ChangePasswordWindow

class MenuWindow(QWidget):
    def __init__(self, username, role, user_id):
        super().__init__()
        self.username = username
        self.role = role
        self.user_id = user_id
        self.setWindowTitle(f"Меню Службы Доставки (Роль: {role})")
        self.resize(400, 300)
        layout = QVBoxLayout()
        
        self.label_info = QLabel(f"Пользователь: {username}\nРоль: {role}")
        layout.addWidget(self.label_info)
        
        btn_pass = QPushButton("Смена пароля")
        btn_pass.clicked.connect(self.open_password)
        layout.addWidget(btn_pass)
        
        btn_orders = QPushButton("Управление заказами")
        btn_orders.clicked.connect(self.open_orders)
        layout.addWidget(btn_orders)
        
        btn_couriers = QPushButton("Управление курьерами")
        btn_couriers.clicked.connect(self.open_couriers)
        layout.addWidget(btn_couriers)
        
        btn_tracking = QPushButton("Отслеживание и Отчёты")
        btn_tracking.clicked.connect(self.open_tracking)
        layout.addWidget(btn_tracking)
        
        btn_users = QPushButton("Пользователи")
        btn_users.clicked.connect(self.open_users)
        layout.addWidget(btn_users)
        
        if self.role != "admin":
            btn_orders.setEnabled(False)
            btn_couriers.setEnabled(False)
            btn_users.setEnabled(False)
            btn_users.setToolTip("Доступно только администраторам")
            
        self.setLayout(layout)

    def open_password(self):
        self.win = ChangePasswordWindow(self.user_id, self.username)
        self.win.show()

    def open_orders(self):
        self.win = OrdersWindow(self.role)
        self.win.show()

    def open_couriers(self):
        self.win = CouriersApp(self.role)
        self.win.show()

    def open_tracking(self):
        self.win = TrackingWindow(self.role)
        self.win.show()

    def open_users(self):
        self.win = UsersWindow(self.role)
        self.win.show()