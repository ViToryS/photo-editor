import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout, \
    QComboBox, QSpinBox
from PyQt5.QtGui import QPixmap, QImage, QPainter
import matplotlib.pyplot as plt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_image = Image()
        self.selected_channel = None
        self.displayed_image = None
        self.is_loaded = False
        self.actions = []

        self.flag = False
        self.setWindowTitle("Photo Editor")
        self.setGeometry(400, 400, 1280, 720)

        desktop = QApplication.desktop()
        x = (desktop.width() - self.width()) // 2
        y = (desktop.height() - self.height()) // 2
        self.move(x, y)

        self.layout = QVBoxLayout()
        self.image_layout = QHBoxLayout()
        self.functions_layout = QVBoxLayout()
        self.layout.addLayout(self.image_layout)

        self.label_image = QLabel(self)
        self.label_image.setFixedSize(QSize(1000, 500))
        self.label_image.setStyleSheet("border: 2px solid gray;")
        self.image_layout.addWidget(self.label_image, alignment=Qt.AlignCenter)
        self.image_layout.addLayout(self.functions_layout)

        self.channel_combo_box = QComboBox()
        self.channel_combo_box.addItems(["Без эффекта", "Красный", "Зеленый", "Синий"])
        (self.channel_combo_box.currentIndexChanged.connect
         (lambda index: self.change_channel(self.channel_combo_box.itemText(index))))

        self.crop_button = QPushButton("Обрезать изображение", self)
        self.crop_button.clicked.connect(self.crop_image)

        self.label_rotation = QLabel("Введите угол поворота изображения")
        self.rotation_spin_box = QSpinBox()
        self.rotation_spin_box.setMaximum(360)
        self.rotation_spin_box.setMinimum(-360)

        self.btn_load_image = QPushButton("Загрузить изображение", self)
        self.btn_load_image.clicked.connect(self.load_image)
        self.layout.addWidget(self.btn_load_image)

        self.btn_capture_image = QPushButton("Сделать снимок с веб-камеры", self)
        self.btn_capture_image.clicked.connect(self.capture_image)
        self.layout.addWidget(self.btn_capture_image)
        self.crop_spin_boxes = []
        self.size_label = QLabel()
        self.rotate_button = QPushButton("Повернуть изображение")
        self.rotate_button.clicked.connect(self.rotate_image)

        self.cancel_button = QPushButton("Отменить все изменения")
        self.cancel_button.clicked.connect(self.cancel_changes)
        self.setLayout(self.layout)

    def add_function_panel(self, image):
        self.functions_layout.addWidget(self.channel_combo_box)

        height, width = image.shape[:2]
        self.size_label.setText(f'Размер изображения: {width}x{height}')
        self.functions_layout.addWidget(self.size_label)

        coordinates = ["X1", "Y1", "X2", "Y2"]
        hor_layout1 = QHBoxLayout()
        hor_layout2 = QHBoxLayout()
        for i in coordinates:
            label = QLabel(f'{i}: ')
            spinbox = QSpinBox()
            if coordinates.index(i) <= 1:
                hor_layout1.addWidget(label)
                hor_layout1.addWidget(spinbox)
            else:
                hor_layout2.addWidget(label)
                hor_layout2.addWidget(spinbox)
            if coordinates.index(i) % 2 == 0:
                spinbox.setMaximum(width)
            else:
                spinbox.setMaximum(height)
            spinbox.setMinimum(0)
            self.crop_spin_boxes.append(spinbox)

        self.functions_layout.addLayout(hor_layout1)
        self.functions_layout.addLayout(hor_layout2)

        self.functions_layout.addWidget(self.crop_button)

        self.functions_layout.addWidget(self.label_rotation)
        self.functions_layout.addWidget(self.rotation_spin_box)
        self.functions_layout.addWidget(self.rotate_button)
        self.functions_layout.addWidget(self.cancel_button)

    def update_function_panel(self):
        self.channel_combo_box.setCurrentText(self.selected_image.get_color_channel())

        height, width = self.displayed_image.shape[:2]
        self.size_label.setText(f'Размер изображения: {width}x{height}')

        for i in self.crop_spin_boxes:
            if self.crop_spin_boxes.index(i) % 2 == 0:
                i.setMaximum(width)
            else:
                i.setMaximum(height)

    def load_image(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg)")
        file_dialog.setViewMode(QFileDialog.Detail)
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            image = cv2.imread(file_path)
            if image is not None:
                self.selected_image = Image(image, "Без эффекта", )
                self.displayed_image = self.selected_image.get_image()
                self.display_image()
                if not self.is_loaded:
                    self.add_function_panel(self.displayed_image)
                    self.is_loaded = True
                else:
                    self.update_function_panel(self.displayed_image)

            else:
                print("Ошибка загрузки изображения") # Русский путь не робит

    def capture_image(self):
        c = cv2.VideoCapture(0)
        ret, frame = c.read()
        if ret:
            if self.selected_image is None:
                self.add_function_panel(frame)
            else:
                self.update_function_panel(frame)
            self.selected_image = frame
            self.display_image(frame)
        else:
            print("Ошибка подключения к веб-камере. Проверьте наличие и корректность подключения камеры.")

    def display_image(self):
        self.flag = False
        self.displayed_image = self.selected_image.get_image()

        for i in self.actions:
            if i == "channel":
                self.change_channel(self.selected_image.get_color_channel())
            elif i == "crop":
                self.crop_image()
            elif i == "rotate":
                self.rotate_image()

        height, width, channels = self.displayed_image.shape

        # Определение коэффициента масштабирования для ширины
        width_ratio = 1000 / width
        scaled_width = 1000
        scaled_height = int(height * width_ratio)

        # Регулирование высоты, чтобы изображение не было слишком высоким
        if scaled_height > 500:
            height_ratio = 500 / scaled_height
            scaled_height = 500
            scaled_width = int(scaled_width * height_ratio)

        # Масштабирование изображения с сохранением пропорций
        image = cv2.resize(self.displayed_image, (scaled_width, scaled_height))
        bytes_per_line = channels * scaled_width
        q_img = QImage(image.data, scaled_width, scaled_height, bytes_per_line,
                       QImage.Format_RGB888).rgbSwapped()

        # Создание нового изображения с пустым пространством по бокам
        new_image = QImage(1000, 500, QImage.Format_RGB888)
        new_image.fill(Qt.white)
        painter = QPainter(new_image)
        painter.drawImage((1000 - scaled_width) // 2, (500 - scaled_height) // 2, q_img)
        painter.end()
        self.update_function_panel()
        self.label_image.setPixmap(QPixmap.fromImage(new_image))
        self.flag = True

    def change_channel(self, channel):
        if self.flag:
            self.selected_image.set_color_channel(channel)
            self.actions.append("channel")
            self.display_image()
        else:
            red, green, blue = cv2.split(self.displayed_image)
            if channel == "Красный":
                self.displayed_image = cv2.merge((np.zeros_like(blue), np.zeros_like(blue), blue))
            elif channel == "Зеленый":
                self.displayed_image = cv2.merge((np.zeros_like(green), green, np.zeros_like(green)))
            elif channel == "Синий":
                self.displayed_image = cv2.merge((red, np.zeros_like(red), np.zeros_like(red)))

    def crop_image(self):
        if self.flag:
            x1, y1, x2, y2 = [sb.value() for sb in self.crop_spin_boxes]
            self.selected_image.crop_coordinates.append([y1, y2, x1, x2])
            self.actions.append("crop")
            self.display_image()
        else:
            coordinates = self.selected_image.get_crop_coordinates()
            if coordinates is not []:
                for i in coordinates:
                    self.displayed_image = self.displayed_image[i[0]:i[1], i[2]:i[3]]

    def rotate_image(self):
        if self.flag:
            self.selected_image.angel_rotation.append(self.rotation_spin_box.value())
            print(self.selected_image.get_angel_rotation())
            self.actions.append("rotate")
            self.display_image()
        else:
            angels = self.selected_image.get_angel_rotation()
            if angels is not []:
                for i in angels:
                    height, width = self.displayed_image.shape[:2]
                    centre = (width // 2, height // 2)

                    rotation_matrix = cv2.getRotationMatrix2D(centre, i, 1)

                    cos_of_rotation_matrix = np.abs(rotation_matrix[0][0])
                    sin_of_rotation_matrix = np.abs(rotation_matrix[0][1])

                    new_image_height = int((height * cos_of_rotation_matrix) +
                                     (width * sin_of_rotation_matrix))
                    new_image_width = int((height * sin_of_rotation_matrix) +
                                    (width * cos_of_rotation_matrix))

                    rotation_matrix[0][2] += (new_image_width - width) /2
                    rotation_matrix[1][2] += (new_image_height - height) /2
                    print(new_image_height, new_image_width)

                    self.displayed_image = cv2.warpAffine(
                        self.displayed_image, rotation_matrix, (new_image_width, new_image_height))

    def cancel_changes(self):
        self.displayed_image = self.selected_image.get_image()
        self.selected_image = Image(self.displayed_image)
        self.display_image()
        self.actions = []



class Image:
    def __init__(self, image=None, color_channel="Без эффекта", angel_rotation=None, crop_coordinates=None):
        if angel_rotation is None:
            angel_rotation = []
        if crop_coordinates is None:
            crop_coordinates = []
        self.image = image
        self.color_channel = color_channel
        self.angel_rotation = angel_rotation
        self.crop_coordinates = crop_coordinates

    def set_color_channel(self, color_channel):
        self.color_channel = color_channel

    def set_angel_rotation(self, angel_rotation):
        self.angel_rotation = angel_rotation

    def set_crop_coordinates(self, crop_coordinates):
        self.crop_coordinates = crop_coordinates

    def get_color_channel(self):
        return self.color_channel

    def get_angel_rotation(self):
        return self.angel_rotation

    def get_crop_coordinates(self):
        return self.crop_coordinates

    def get_image(self):
        return self.image

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())