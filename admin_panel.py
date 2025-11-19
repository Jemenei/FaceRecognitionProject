from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QHeaderView, QTabWidget)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor
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
        self.setStyleSheet("background-color: #f5f7fa;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Создаем вкладки
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                color: #666666;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #4A90E2;
                border-bottom: 2px solid #4A90E2;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
        tabs.addTab(self.create_users_tab(), "📋 База пользователей")
        tabs.addTab(self.create_logs_tab(), "🕐 Журнал доступа")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Загружаем данные
        self.load_users()
        self.load_logs()
    
    def create_users_tab(self):
        """Создание вкладки с полной базой пользователей"""
        tab = QWidget()
        tab.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Информация и кнопки
        top_layout = QHBoxLayout()
        
        info_label = QLabel("Все зарегистрированные пользователи")
        info_label.setStyleSheet("font-size: 15px; font-weight: 500; color: #1a1a1a;")
        top_layout.addWidget(info_label)
        
        top_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        refresh_btn.clicked.connect(self.load_users)
        
        delete_btn = QPushButton("🗑 Удалить")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        delete_btn.clicked.connect(self.delete_user)
        
        top_layout.addWidget(refresh_btn)
        top_layout.addWidget(delete_btn)
        
        layout.addLayout(top_layout)
        
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
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
                gridline-color: #f0f0f0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #495057;
                font-weight: 600;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                color: #212529;
            }
            QTableWidget::item:selected {
                background-color: #e7f3ff;
                color: #1a1a1a;
            }
        """)
        
        layout.addWidget(self.users_table)
        tab.setLayout(layout)
        return tab
    
    def create_logs_tab(self):
        """Создание вкладки с логами входов/выходов"""
        tab = QWidget()
        tab.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Информационная панель
        top_layout = QHBoxLayout()
        
        info_label = QLabel("🔴 Live мониторинг • Обновление каждые 5 сек")
        info_label.setStyleSheet("color: #dc3545; font-weight: 500; font-size: 13px;")
        top_layout.addWidget(info_label)
        
        top_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        refresh_btn.clicked.connect(self.load_logs)
        top_layout.addWidget(refresh_btn)
        
        layout.addLayout(top_layout)
        
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
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
                gridline-color: #f0f0f0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #495057;
                font-weight: 600;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                color: #212529;
            }
            QTableWidget::item:selected {
                background-color: #e7f3ff;
                color: #1a1a1a;
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
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
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
                        item.setBackground(QColor(212, 237, 218))  # Светло-зеленый
                        item.setForeground(QColor(21, 87, 36))
                    elif value == "Выход":
                        item.setBackground(QColor(255, 243, 205))  # Светло-желтый
                        item.setForeground(QColor(133, 100, 4))
                
                self.logs_table.setItem(row, col, item)
    
    def refresh_logs(self):
        """Автоматическое обновление логов"""
        self.load_logs()
    
    def delete_user(self):
        """Удаление выбранного пользователя"""
        selected = self.users_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления")
            return
        
        user_id = int(self.users_table.item(selected, 0).text())
        student_id = self.users_table.item(selected, 1).text()
        
        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Удалить пользователя {student_id}?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            delete_user(user_id)
            QMessageBox.information(self, "Успех", "Пользователь удален")
            self.load_users()
    
    def closeEvent(self, event):
        """Остановка таймера при закрытии"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        super().closeEvent(event)