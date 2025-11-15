import cv2
import dlib
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QDialog, QLineEdit, 
                             QComboBox, QFormLayout)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt
from database import (load_all_encodings, save_face_encoding, log_access, 
                     get_user_by_student_id)


class RegisterDialog(QDialog):
    """Диалог регистрации нового пользователя"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Регистрация нового пользователя")
        self.setFixedSize(450, 350)
        self.setStyleSheet("""
            QLineEdit, QComboBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton {
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
        """)
        
        layout = QFormLayout()
        
        header = QLabel("📝 Введите данные студента/сотрудника")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3; padding: 10px;")
        layout.addRow(header)
        
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("Например: STU2024001")
        
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Имя студента")
        
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Фамилия студента")
        
        self.faculty_input = QComboBox()
        self.faculty_input.addItems([
            "Компьютерные науки",
            "Инженерия",
            "Бизнес",
            "Медицина",
            "Право",
            "Искусство",
            "Физика",
            "Химия"
        ])
        
        layout.addRow("🆔 ID студента:", self.student_id_input)
        layout.addRow("👤 Имя:", self.first_name_input)
        layout.addRow("👤 Фамилия:", self.last_name_input)
        layout.addRow("🎓 Факультет:", self.faculty_input)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("✅ Сохранить")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setStyleSheet("background-color: #f44336; color: white;")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        self.setLayout(layout)
    
    def get_data(self):
        return {
            'student_id': self.student_id_input.text().strip(),
            'first_name': self.first_name_input.text().strip(),
            'last_name': self.last_name_input.text().strip(),
            'faculty': self.faculty_input.currentText()
        }


class FaceRecognitionWindow(QWidget):
    """Окно системы распознавания лиц"""
    
    def __init__(self):
        super().__init__()
        
        # Загрузка dlib моделей
        try:
            self.detector = dlib.get_frontal_face_detector()
            self.sp = dlib.shape_predictor("dat/shape_predictor_68_face_landmarks.dat")
            self.facerec = dlib.face_recognition_model_v1("dat/dlib_face_recognition_resnet_model_v1.dat")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить модели dlib:\n{e}")
            return
        
        self.init_ui()
        self.init_camera()
        
        # Загружаем пользователей с encodings
        self.known_users = load_all_encodings()
        self.current_recognized = None
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("🎥 Система распознавания лиц")
        
        layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel("🎥 РАСПОЗНАВАНИЕ ЛИЦ В РЕАЛЬНОМ ВРЕМЕНИ")
        header.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("padding: 15px; background-color: #2196F3; color: white;")
        layout.addWidget(header)
        
        # Видео поток
        self.video_label = QLabel()
        self.video_label.setMinimumSize(800, 600)
        self.video_label.setStyleSheet("border: 3px solid #2196F3; background-color: black;")
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label)
        
        # Статус
        self.status_label = QLabel("⏳ Ожидание распознавания...")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(12)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("padding: 15px; background-color: #fff3cd; color: #856404;")
        layout.addWidget(self.status_label)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        register_btn = QPushButton("➕ ЗАРЕГИСТРИРОВАТЬ НОВОЕ ЛИЦО")
        register_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 12px; font-size: 14px; font-weight: bold;")
        register_btn.clicked.connect(self.register_new_face)
        
        entry_btn = QPushButton("🟢 ВХОД")
        entry_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 12px; font-size: 14px; font-weight: bold;")
        entry_btn.clicked.connect(lambda: self.log_access_event("Вход"))
        
        exit_btn = QPushButton("🟡 ВЫХОД")
        exit_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 12px; font-size: 14px; font-weight: bold;")
        exit_btn.clicked.connect(lambda: self.log_access_event("Выход"))
        
        buttons_layout.addWidget(register_btn)
        buttons_layout.addWidget(entry_btn)
        buttons_layout.addWidget(exit_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def init_camera(self):
        """Инициализация камеры и таймера"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.warning(self, "Ошибка", "Не удалось открыть камеру!")
            return
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
    
    def update_frame(self):
        """Обновление кадра с камеры и распознавание лиц"""
        if not self.cap.isOpened():
            return
        
        ret, frame = self.cap.read()
        if not ret:
            return
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dets = self.detector(gray)
        
        self.current_recognized = None
        
        for d in dets:
            shape = self.sp(gray, d)
            face_descriptor = np.array(self.facerec.compute_face_descriptor(frame, shape))
            
            # Поиск ближайшего совпадения
            best_match = None
            best_distance = float('inf')
            
            for student_id, user_data in self.known_users.items():
                distance = np.linalg.norm(face_descriptor - np.array(user_data['encoding']))
                if distance < best_distance:
                    best_distance = distance
                    best_match = (student_id, user_data['name'], user_data['id'])
            
            # Порог распознавания
            if best_match and best_distance < 0.6:
                student_id, name, user_id = best_match
                self.current_recognized = (user_id, student_id, name)
                color = (0, 255, 0)  # Зеленый
                label = f"{name} (ID: {student_id})"
                self.status_label.setText(f"✅ РАСПОЗНАН: {name} | ID: {student_id}")
                self.status_label.setStyleSheet("padding: 15px; background-color: #d4edda; color: #155724; font-weight: bold; font-size: 14px;")
            else:
                color = (0, 0, 255)  # Красный
                label = "НЕИЗВЕСТЕН"
                self.status_label.setText("❌ Лицо не распознано | Доступ запрещен")
                self.status_label.setStyleSheet("padding: 15px; background-color: #f8d7da; color: #721c24; font-weight: bold; font-size: 14px;")
            
            # Рисуем рамку и текст
            cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), color, 3)
            cv2.putText(frame, label, (d.left(), max(d.top() - 10, 0)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        if len(dets) == 0:
            self.status_label.setText("⏳ Ожидание распознавания...")
            self.status_label.setStyleSheet("padding: 15px; background-color: #fff3cd; color: #856404; font-weight: bold; font-size: 14px;")
        
        # Конвертируем для PyQt
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def register_new_face(self):
        """Регистрация нового пользователя с лицом"""
        ret, frame = self.cap.read()
        if not ret:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить кадр с камеры!")
            return
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dets = self.detector(gray)
        
        if len(dets) == 0:
            QMessageBox.warning(self, "❌ Лицо не найдено", 
                              "Убедитесь, что ваше лицо хорошо видно на камере!")
            return
        
        # Получаем encoding лица
        d = dets[0]
        shape = self.sp(gray, d)
        encoding = np.array(self.facerec.compute_face_descriptor(frame, shape))
        
        # Диалог регистрации
        dialog = RegisterDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not all(data.values()):
                QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
                return
            
            # Сохраняем в БД
            if save_face_encoding(data['student_id'], data['first_name'], 
                                 data['last_name'], data['faculty'], encoding):
                QMessageBox.information(self, "✅ Успешная регистрация", 
                    f"Пользователь зарегистрирован!\n\n"
                    f"👤 Имя: {data['first_name']} {data['last_name']}\n"
                    f"🆔 ID: {data['student_id']}\n"
                    f"🎓 Факультет: {data['faculty']}\n\n"
                    f"✅ ДОСТУП В СИСТЕМУ РАЗРЕШЕН!")
                
                # Обновляем список пользователей
                self.known_users = load_all_encodings()
            else:
                QMessageBox.warning(self, "Ошибка", "Такой ID студента уже существует!")
    
    def log_access_event(self, action):
        """Записать вход/выход текущего распознанного лица"""
        if not self.current_recognized:
            QMessageBox.warning(self, "❌ Ошибка", 
                              "Лицо не распознано!\n\nВстаньте перед камерой для распознавания.")
            return
        
        user_id, student_id, full_name = self.current_recognized
        
        # Записываем в лог
        log_access(user_id, student_id, full_name, action, "Main Entrance")
        
        # Определяем стиль сообщения
        if action == "Вход":
            icon = "🟢"
            color = "#d4edda"
            text_color = "#155724"
            message = "ДОСТУП РАЗРЕШЕН"
        else:
            icon = "🟡"
            color = "#fff3cd"
            text_color = "#856404"
            message = "ВЫХОД ЗАРЕГИСТРИРОВАН"
        
        self.status_label.setText(f"{icon} {message}: {full_name} | ID: {student_id}")
        self.status_label.setStyleSheet(f"padding: 15px; background-color: {color}; color: {text_color}; font-weight: bold; font-size: 14px;")
        
        QMessageBox.information(self, f"✅ {action} зарегистрирован", 
            f"{action} успешно записан!\n\n"
            f"👤 {full_name}\n"
            f"🆔 ID: {student_id}\n"
            f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📍 Локация: Main Entrance")
    
    def closeEvent(self, event):
        """Освобождение ресурсов при закрытии"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        super().closeEvent(event)