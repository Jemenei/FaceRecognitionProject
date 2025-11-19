import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QDialog, 
                             QLineEdit, QMessageBox, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from auth_db import login_user
from admin_panel import AdminPanel
from face_recognition_window import FaceRecognitionWindow


class LoginWindow(QDialog):
    """Окно авторизации администратора"""
    
    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.admin_name = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Авторизация")
        self.setFixedSize(400, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                padding: 14px 15px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1px;
                background-color: #f8f9fa;
                color: #1a1a1a;
                min-height: 45px;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background-color: #ffffff;
            }
            QPushButton {
                padding: 12px;
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2868A8;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок
        title = QLabel("🔐 Вход в систему")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(22)
        title.setFont(title_font)
        title.setStyleSheet("color: #1a1a1a; margin-bottom: 10px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Система контроля доступа")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666666; font-size: 13px; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Логин
        login_label = QLabel("Логин")
        login_label.setStyleSheet("color: #666; font-size: 13px; margin-bottom: -8px;")
        layout.addWidget(login_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.username_input)

        # Пароль
        password_label = QLabel("Пароль")
        password_label.setStyleSheet("color: #666; font-size: 13px; margin-bottom: -8px; margin-top: 5px;")
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        # Кнопка входа
        login_btn = QPushButton("Войти")
        login_btn.setMinimumHeight(50)
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn, 0, Qt.AlignTop)
        
        layout.addSpacing(10)


        # Подсказка
        hint = QLabel("По умолчанию: admin / admin123")
        hint.setStyleSheet("color: #999; font-size: 11px; font-style: italic;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
        

        layout.addStretch()
        
        self.setLayout(layout)
        
        self.password_input.returnPressed.connect(self.login)
        self.username_input.setFocus()
    
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        admin_name = login_user(username, password)
        if admin_name:
            self.authenticated = True
            self.admin_name = admin_name
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", 
                              "Неверный логин или пароль")
            self.password_input.clear()
            self.username_input.setFocus()


class MainWindow(QMainWindow):
    """Главное окно приложения с выбором режимов"""
    
    def __init__(self, admin_name):
        super().__init__()
        self.admin_name = admin_name
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Система контроля доступа")
        self.setGeometry(100, 100, 1100, 750)
        self.setStyleSheet("background-color: #f5f7fa;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок с именем админа
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #e0e0e0;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        header = QLabel("Панель управления")
        header_font = QFont()
        header_font.setPointSize(20)
        header.setFont(header_font)
        header.setStyleSheet("color: #1a1a1a;")
        
        admin_label = QLabel(f"👤 {self.admin_name}")
        admin_label.setStyleSheet("color: #666666; font-size: 14px;")
        
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(admin_label)
        
        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)
        
        # Стек виджетов для разных режимов
        self.stacked_widget = QStackedWidget()
        
        # Режимы
        self.menu_widget = self.create_menu_widget()
        self.admin_panel = AdminPanel()
        self.face_recognition = FaceRecognitionWindow()
        
        self.stacked_widget.addWidget(self.menu_widget)
        self.stacked_widget.addWidget(self.admin_panel)
        self.stacked_widget.addWidget(self.face_recognition)
        
        main_layout.addWidget(self.stacked_widget)
        
        central_widget.setLayout(main_layout)
    
    def create_menu_widget(self):
        """Создание виджета с меню выбора режимов"""
        widget = QWidget()
        widget.setStyleSheet("background-color: #f5f7fa;")
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)
        
        # Описание
        description = QLabel("Выберите режим работы")
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #666666; font-size: 15px; margin-bottom: 20px;")
        layout.addWidget(description)
        
        # Кнопка FULL DATABASE
        db_btn = QPushButton("📋  База данных пользователей\nПросмотр всех студентов и сотрудников")
        db_btn.setMinimumHeight(100)
        db_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1a1a1a;
                padding: 25px;
                font-size: 15px;
                font-weight: 500;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4A90E2;
                color: white;
                border: 1px solid #4A90E2;
            }
        """)
        db_btn.clicked.connect(lambda: self.switch_mode(1))
        layout.addWidget(db_btn)
        
        # Кнопка LOGIN/LOGOUT DATABASE
        logs_btn = QPushButton("🕐  Журнал доступа\nИстория входов и выходов (Live)")
        logs_btn.setMinimumHeight(100)
        logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1a1a1a;
                padding: 25px;
                font-size: 15px;
                font-weight: 500;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4A90E2;
                color: white;
                border: 1px solid #4A90E2;
            }
        """)
        logs_btn.clicked.connect(lambda: self.switch_mode(1))
        layout.addWidget(logs_btn)
        
        # Кнопка FACE RECOGNITION
        face_btn = QPushButton("🎥  Распознавание лиц\nАктивировать систему сканирования")
        face_btn.setMinimumHeight(100)
        face_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1a1a1a;
                padding: 25px;
                font-size: 15px;
                font-weight: 500;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4A90E2;
                color: white;
                border: 1px solid #4A90E2;
            }
        """)
        face_btn.clicked.connect(lambda: self.switch_mode(2))
        layout.addWidget(face_btn)
        
        layout.addStretch()
        
        # Кнопка назад (скрыта на главном экране)
        self.back_btn = QPushButton("← Назад")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e9ecef;
                color: #495057;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #dee2e6;
            }
        """)
        self.back_btn.clicked.connect(lambda: self.switch_mode(0))
        self.back_btn.hide()
        layout.addWidget(self.back_btn, 0, Qt.AlignLeft)
        
        widget.setLayout(layout)
        return widget
    
    def switch_mode(self, index):
        """Переключение между режимами"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Показываем/скрываем кнопку назад
        if index == 0:
            self.back_btn.hide()
        else:
            self.back_btn.show()
        
        # Управление камерой для режима распознавания
        if index == 2:
            if hasattr(self.face_recognition, 'timer'):
                self.face_recognition.timer.start()
        else:
            if hasattr(self.face_recognition, 'timer'):
                self.face_recognition.timer.stop()


def main():
    app = QApplication(sys.argv)
    
    # Окно авторизации
    login = LoginWindow()
    if login.exec_() != QDialog.Accepted:
        sys.exit(0)
    
    # Главное окно
    window = MainWindow(login.admin_name)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()