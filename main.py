import sys
import cv2
import dlib
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QInputDialog, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from database import load_all_encodings, save_face_encoding

# ====== DLIB МОДЕЛИ ======
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor("dat/shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("dat/dlib_face_recognition_resnet_model_v1.dat")

# ====== PyQt5 GUI ======
class FaceRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()

        # Настройки окна
        self.setWindowTitle("Face Recognition System")
        self.setFixedSize(800, 600)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # Layout
        layout = QVBoxLayout()
        self.label = QLabel()
        layout.addWidget(self.label)

        # Кнопка добавления нового лица
        self.add_face_btn = QPushButton("Добавить лицо")
        self.add_face_btn.clicked.connect(self.capture_new_face)
        layout.addWidget(self.add_face_btn)
        self.setLayout(layout)

        # Камера
        self.cap = cv2.VideoCapture(0)

        # Таймер для обновления кадров
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # Таймер удержания Q
        self._q_hold_timer = QTimer()
        self._q_hold_timer.setSingleShot(True)
        self._q_hold_timer.timeout.connect(self._on_q_held)
        self._q_hold_threshold_ms = 1000  # 1 секунда

        # Загружаем лица из базы
        self.known_faces = load_all_encodings()

    def update_frame(self):
        if not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dets = detector(gray)

        for d in dets:
            shape = sp(gray, d)
            face_descriptor = np.array(facerec.compute_face_descriptor(frame, shape))

            # Расстояния до лиц из базы
            distances = {
                name: np.linalg.norm(face_descriptor - np.array(known))
                for name, known in self.known_faces.items()
            }

            recognized = "Unknown"
            if distances:
                best = min(distances, key=distances.get)
                if distances[best] < 0.6:
                    recognized = best

            # Рисуем рамку и подпись
            cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (0, 255, 0), 2)
            cv2.putText(frame, recognized, (d.left(), max(d.top() - 10, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Конвертируем для PyQt
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qimg).scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _on_q_held(self):
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q and not event.isAutoRepeat():
            self._q_hold_timer.start(self._q_hold_threshold_ms)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Q and not event.isAutoRepeat():
            if self._q_hold_timer.isActive():
                self._q_hold_timer.stop()
        super().keyReleaseEvent(event)

    def closeEvent(self, event):
        try:
            if self.cap and self.cap.isOpened():
                self.cap.release()
        except Exception:
            pass
        super().closeEvent(event)

    def capture_new_face(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Не удалось получить кадр!")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dets = detector(gray)
        if len(dets) == 0:
            print("Лицо не найдено!")
            return

        d = dets[0]
        shape = sp(gray, d)
        encoding = np.array(facerec.compute_face_descriptor(frame, shape))

        name, ok = QInputDialog.getText(self, "Добавление лица", "Введите имя:")
        if not ok or not name.strip():
            return

        save_face_encoding(name.strip(), encoding)
        print(f"Лицо {name.strip()} сохранено в БД!")

        # Обновляем список лиц
        self.known_faces = load_all_encodings()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FaceRecognitionApp()
    win.show()
    sys.exit(app.exec_())
