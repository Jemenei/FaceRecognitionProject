from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QHeaderView, QTabWidget)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from database import get_all_users, delete_user, get_recent_logs


class AdminPanel(QWidget):
    """Панель администратора для просмотра баз данных"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Таймер для автообновления логов каждые 5 секунд
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_logs)
        self.timer.start(5000)
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("📊 Панель администратора")
        
        layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel("📊 ПАНЕЛЬ УПРАВЛЕНИЯ БАЗАМИ ДАННЫХ")
        header.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("padding: 15px; background-color: #2196F3; color: white;")
        layout.addWidget(header)
        
        # Создаем вкладки
        tabs = QTabWidget()
        tabs.addTab(self.create_users_tab(), "📋 FULL DATABASE")
        tabs.addTab(self.create_logs_tab(), "🕐 LOGIN/LOGOUT DATABASE")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Загружаем данные
        self.load_users()
        self.load_logs()
    
    def create_users_tab(self):
        """Создание вкладки с полной базой пользователей"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Информация
        info_label = QLabel("📋 Все зарегистрированные студенты и сотрудники")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; background-color: #e3f2fd;")
        layout.addWidget(info_label)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; font-weight: bold;")
        refresh_btn.clicked.connect(self.load_users)
        
        delete_btn = QPushButton("🗑️ Удалить выбранного")
        delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px; font-weight: bold;")
        delete_btn.clicked.connect(self.delete_user)
        
        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "ID Студента", "Имя", "Фамилия", "Факультет", "Дата регистрации"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
        """)
        
        layout.addWidget(self.users_table)
        tab.setLayout(layout)
        return tab
    
    def create_logs_tab(self):
        """Создание вкладки с логами входов/выходов"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Информационная панель
        info_layout = QHBoxLayout()
        info_label = QLabel("🔴 Live мониторинг | Автообновление каждые 5 секунд")
        info_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 14px; padding: 10px;")
        
        refresh_btn = QPushButton("🔄 Обновить сейчас")
        refresh_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; font-weight: bold;")
        refresh_btn.clicked.connect(self.load_logs)
        
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        info_layout.addWidget(refresh_btn)
        
        layout.addLayout(info_layout)
        
        # Таблица логов
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(6)
        self.logs_table.setHorizontalHeaderLabels([
            "ID", "ID Студента", "ФИО", "Действие", "Локация", "Время"
        ])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.setAlternatingRowColors(True)
        self.logs_table.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
        """)
        
        layout.addWidget(self.logs_table)
        tab.setLayout(layout)
        return tab
    
    def load_users(self):
        """Загрузка пользователей в таблицу"""
        users = get_all_users()
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            for col, value in enumerate(user):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Только чтение
                self.users_table.setItem(row, col, item)
    
    def load_logs(self):
        """Загрузка логов в таблицу"""
        logs = get_recent_logs(100)
        self.logs_table.setRowCount(len(logs))
        
        for row, log in enumerate(logs):
            for col, value in enumerate(log):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                
                # Цветовая маркировка действий
                if col == 3:  # Колонка "Действие"
                    if value == "Вход":
                        item.setBackground(Qt.green)
                    elif value == "Выход":
                        item.setBackground(Qt.yellow)
                
                self.logs_table.setItem(row, col, item)
    
    def refresh_logs(self):
        """Автоматическое обновление логов"""
        self.load_logs()
    
    def delete_user(self):
        """Удаление выбранного пользователя"""
        selected = self.users_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления!")
            return
        
        user_id = int(self.users_table.item(selected, 0).text())
        student_id = self.users_table.item(selected, 1).text()
        
        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Удалить пользователя {student_id}?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            delete_user(user_id)
            QMessageBox.information(self, "Успех", "Пользователь удален!")
            self.load_users()
    
    def closeEvent(self, event):
        """Остановка таймера при закрытии"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        super().closeEvent(event)