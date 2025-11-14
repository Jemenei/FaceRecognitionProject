from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from auth_db import register_user, login_user

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login / Register")

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        layout.addWidget(self.password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        reg_btn = QPushButton("Register")
        reg_btn.clicked.connect(self.register)
        layout.addWidget(reg_btn)

        self.setLayout(layout)

    def login(self):
        if login_user(self.username.text(), self.password.text()):
            QMessageBox.information(self, "OK", "Login successful")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Wrong username or password")

    def register(self):
        try:
            register_user(self.username.text(), self.password.text())
            QMessageBox.information(self, "OK", "User registered")
        except:
            QMessageBox.warning(self, "Error", "Username already exists")
