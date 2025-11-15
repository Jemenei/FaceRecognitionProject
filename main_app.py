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
        self.setWindowTitle("Авторизация в системе")
        self.setFixedSize(450, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                padding: 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("🔐 СИСТЕМА КОНТРОЛЯ ДОСТУПА")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2196F3; padding: 20px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Авторизация администратора")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Поля ввода
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        
        # Кнопка входа
        login_btn = QPushButton("🚀 ВОЙТИ В СИСТЕМУ")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)
        
        # Подсказка
        hint = QLabel("По умолчанию: admin / admin123")
        hint.setStyleSheet("color: #999; font-size: 11px; font-style: italic; margin-top: 10px;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
        
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
            QMessageBox.warning(self, "❌ Ошибка доступа", 
                              "Неверный логин или пароль!\n\nПопробуйте снова.")
            self.password_input.clear()
            self.username_input.setFocus()


class MainWindow(QMainWindow):
    """Главное окно приложения с выбором режимов"""
    
    def __init__(self, admin_name):
        super().__init__()
        self.admin_name = admin_name
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🎓 Система контроля доступа университета")
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        # Заголовок с именем админа
        header_layout = QHBoxLayout()
        
        header = QLabel("🎓 ПАНЕЛЬ УПРАВЛЕНИЯ")
        header.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(20)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("padding: 20px; background-color: #2196F3; color: white;")
        
        admin_label = QLabel(f"👤 {self.admin_name}")
        admin_label.setAlignment(Qt.AlignRight)
        admin_label_font = QFont()
        admin_label_font.setPointSize(12)
        admin_label.setFont(admin_label_font)
        admin_label.setStyleSheet("padding: 20px; background-color: #2196F3; color: white;")
        
        header_layout.addWidget(header, 3)
        header_layout.addWidget(admin_label, 1)
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)
        
        # Описание
        description = QLabel("Выберите режим работы системы:")
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("font-size: 14px; padding: 15px; background-color: #e3f2fd;")
        main_layout.addWidget(description)
        
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
        layout = QVBoxLayout()
        
        layout.addStretch()
        
        # Кнопка FULL DATABASE
        db_btn = QPushButton("📋 FULL DATABASE\n\nПросмотр всех зарегистрированных\nстудентов и сотрудников")
        db_btn.setMinimumHeight(120)
        db_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        db_btn.clicked.connect(lambda: self.switch_mode(1))
        layout.addWidget(db_btn)
        
        # Кнопка LOGIN/LOGOUT DATABASE
        logs_btn = QPushButton("🕐 LOGIN/LOGOUT DATABASE\n\nЖурнал входов и выходов\n(Live мониторинг)")
        logs_btn.setMinimumHeight(120)
        logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        logs_btn.clicked.connect(lambda: self.switch_mode(1))
        layout.addWidget(logs_btn)
        
        # Кнопка FACE RECOGNITION
        face_btn = QPushButton("🎥 FACE RECOGNITION\n\nАктивировать систему\nраспознавания лиц")
        face_btn.setMinimumHeight(120)
        face_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        face_btn.clicked.connect(lambda: self.switch_mode(2))
        layout.addWidget(face_btn)
        
        layout.addStretch()
        
        # Кнопка назад (скрыта на главном экране)
        self.back_btn = QPushButton("◀ Назад в меню")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        self.back_btn.clicked.connect(lambda: self.switch_mode(0))
        self.back_btn.hide()
        layout.addWidget(self.back_btn)
        
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
            self.back_btn.raise_()
        
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