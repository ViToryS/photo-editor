import sys
import cv2
import numpy
import numpy as np
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout, \
    QComboBox, QSpinBox, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QPainter


class MainWindow(QWidget):
    """Класс, создает окно для отображения фото, выбора функции, создания снимка с веб-камеры.

    Функции: Вывод изображения на экран, снимок с веб-камеры, обрезка, поворот фото, рисование синего прямоугольника,
    выбор цветового канала.
        Attributes
        ----------
        self.selected_image : Image
            Переменная, хранящая оригинал загруженного изображения
        self.displayed_image : numpy.ndarray
            Изображение - многомерный массив. Обновляется при редактировании изображения
        self.is_loaded : boolean
            Загружено ли изображение
        self.actions : list
            Список - порядок действий редактирования изображения

        Methods
        -------
        __init__(self)
            Инициализирует окно приложения, создает, настраивает
            виджеты, создает необходимые переменные
        add_function_panel(self)
            После загрузки фото добавляет панель управления функциями
        update_function_panel(self)
            Обновляет панель управления функциями при изменении свойств изображения
        load_image(self)
            Загружает изображение и обновляет связанные переменные
        capture_image(self)
            Создает снимок, с веб-камеры или сообщает об ошибке, обновляет связанные переменные
        display_image(self)
            Выводит изображение на экран, меняет размер изображения для размещения в окне, преобразует изображение
            согласно self.actions
        change_channel(self, channel):
            Меняет цветовой канал изображения
        crop_image(self)
            Обрезает изображение по координатам
        rotate_image(self)
            Поворачивает изображение по значению угла
        draw_blue_rectangle(self):
        Рисует синий прямоугольник на изображении по координатам двух противоположных углов
        cancel_changes(self):
            Отменяет все действия, совершенные над изображением
        """

    def __init__(self):
        """Инициализирует окно приложения с местом для изображения и кнопками для загрузки и создания снимка

        Создает необходимые виджеты, связывает их с соответствующими функциями, создает массив self.actions = [],
        флаг self.is_loaded = False, переменные self.crop_coordinates_list = None, self.draw_coordinates_list = None,
        self.rotate_angels_list = None, для хранения копий аттрибутов self.selected_image.
        """
        super().__init__()
        self.selected_image = Image()
        self.displayed_image = None
        self.is_loaded = False
        self.actions = []
        # Флаг, определяет, как ведут себя функции редактирования:
        self.editing_is_complete = False
        # False - добавление новых изменения в атрибуты изображения Image
        # True - редактирование self.displayed_image

        self.crop_coordinates_list = None
        self.draw_coordinates_list = None
        self.rotate_angels_list = None

        self.setWindowTitle("Photo Editor")
        self.setFixedSize(1030, 630)

        desktop = QApplication.desktop()
        x = (desktop.width() - self.width()) // 2
        y = (desktop.height() - self.height()) // 2
        self.move(x, y)  # Помещение окна в центре экрана

        self.layout = QVBoxLayout()
        self.image_layout = QHBoxLayout()
        self.function_widget = QWidget()
        self.function_widget.setFixedSize(400, 550)

        self.functions_layout = QVBoxLayout()
        self.function_widget.setLayout(self.functions_layout)
        self.layout.addLayout(self.image_layout)

        self.label_image = QLabel(self)
        self.label_image.setFixedSize(QSize(1000, 500))
        self.label_image.setStyleSheet("border: 2px solid gray;")
        self.image_layout.addWidget(self.label_image, alignment=Qt.AlignCenter)
        self.image_layout.addWidget(self.function_widget)

        self.channel_combo_box = QComboBox()
        self.channel_combo_box.addItems(
            ["Без эффекта", "Красный", "Зеленый", "Синий"])
        (self.channel_combo_box.currentIndexChanged.connect
         (lambda index: self.change_channel(self.channel_combo_box.itemText(index))))

        self.crop_label = QLabel("Введите координаты для обрезки изображения: ")
        self.crop_button = QPushButton("Обрезать изображение")
        self.crop_button.clicked.connect(self.crop_image)
        self.crop_spin_boxes = []

        self.label_rotation = QLabel("Введите угол поворота изображения:")
        self.rotation_spin_box = QSpinBox()
        self.rotation_spin_box.setMaximum(360)
        self.rotation_spin_box.setMinimum(-360)

        self.button_widget = QWidget()
        self.button_layout = QVBoxLayout()
        self.button_widget.setLayout(self.button_layout)

        self.btn_load_image = QPushButton("Загрузить изображение", self)
        self.btn_load_image.clicked.connect(self.load_image)
        self.btn_load_image.setMinimumWidth(300)
        self.button_layout.addWidget(self.btn_load_image, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.button_widget)

        self.btn_capture_image = QPushButton(
            "Сделать снимок с веб-камеры", self)
        self.btn_capture_image.clicked.connect(self.capture_image)
        self.btn_capture_image.setMinimumWidth(300)
        self.button_layout.addWidget(self.btn_capture_image, alignment=Qt.AlignCenter)

        self.channel_btn = QLabel("Выберите цветовой канал: ")
        self.size_label = QLabel()
        self.rotate_button = QPushButton("Повернуть изображение")
        self.rotate_button.clicked.connect(self.rotate_image)

        self.draw_label = QLabel(
            "Чтобы нарисовать синий прямоугольник,\nвыберете"
            " координаты двух противоположных углов: ")
        self.draw_spin_boxes = []
        self.draw_blue_rectangle_button = QPushButton(
            "Нарисовать прямоугольник")
        self.draw_blue_rectangle_button.clicked.connect(
            self.draw_blue_rectangle)

        self.cancel_button = QPushButton("Отменить все изменения")
        self.cancel_button.clicked.connect(self.cancel_changes)
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    def add_function_panel(self):
        """После загрузки фото добавляет панель управления функциями

        Создает необходимые виджеты, добавляет существующие в function_layout, устанавливает крайние значения для
        spinbox на основе высоты и ширины self.displayed_image
        """
        self.setFixedSize(1500, 650)
        desktop = QApplication.desktop()
        x = (desktop.width() - self.width()) // 2
        y = (desktop.height() - self.height()) // 2
        self.move(x, y)

        height, width = self.displayed_image.shape[:2]
        self.size_label.setText(
            f'Размер отображаемого изображения: {width}x{height}')
        self.functions_layout.addWidget(self.size_label)
        self.functions_layout.addWidget(self.channel_btn)

        self.functions_layout.addWidget(self.channel_combo_box)
        self.functions_layout.addWidget(self.crop_label)
        coordinates = ["X1", "Y1", "X2", "Y2"]

        def create_spin_boxes():
            hor_layout1 = QHBoxLayout()
            hor_layout2 = QHBoxLayout()
            spin_boxes = []
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
                spin_boxes.append(spinbox)

            self.functions_layout.addLayout(hor_layout1)
            self.functions_layout.addLayout(hor_layout2)
            return spin_boxes

        self.crop_spin_boxes = create_spin_boxes()

        self.functions_layout.addWidget(self.crop_button)

        self.functions_layout.addWidget(self.label_rotation)
        self.functions_layout.addWidget(self.rotation_spin_box)
        self.functions_layout.addWidget(self.rotate_button)

        self.functions_layout.addWidget(self.draw_label)
        self.draw_spin_boxes = create_spin_boxes()
        self.functions_layout.addWidget(self.draw_blue_rectangle_button)
        self.functions_layout.addWidget(self.cancel_button)

    def update_function_panel(self):
        """Обновляет панель управления функциями

        Обновляет крайние значения spinbox, на основе новых ширины и длины, сбрасывает некоторые виджеты
        """
        self.channel_combo_box.setCurrentText(
            self.selected_image.get_color_channel())

        height, width = self.displayed_image.shape[:2]
        self.size_label.setText(
            f'Размер отображаемого изображения: {width}x{height}')

        for i in self.crop_spin_boxes:
            if self.crop_spin_boxes.index(i) % 2 == 0:
                i.setMaximum(width)
            else:
                i.setMaximum(height)

        for i in self.draw_spin_boxes:
            if self.draw_spin_boxes.index(i) % 2 == 0:
                i.setMaximum(width)
            else:
                i.setMaximum(height)

    def load_image(self):
        """Загружает изображение

        Получает путь к изображению, преобразует изображение в многомерный массив, создает объект Image, при
        возникновении ошибки отображает QMessageBox с сообщением. Добавляет или обновляет панель управления.
        """
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg)")
        file_dialog.setViewMode(QFileDialog.Detail)
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            file = open(file_path, "rb")
            in_bytes = file.read()
            # Для правильной обработки кириллицы
            numpy_array = numpy.frombuffer(in_bytes, dtype=numpy.uint8)
            image = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
            if image is not None:
                self.selected_image = Image(image, "Без эффекта", )
                self.displayed_image = self.selected_image.get_image()

                self.display_image()
                if not self.is_loaded:
                    self.add_function_panel()
                    self.is_loaded = True
                else:
                    self.update_function_panel()
            else:
                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Critical)
                error_box.setText("Ошибка загрузки изображения")
                error_box.setWindowTitle("Ошибка")
                error_box.exec_()

    def capture_image(self):
        """Создает снимок с веб-камеры.

        Создает объект Image. Добавляет или обновляет панель управления. Проверят наличие подключенных к устройству
        и включенных камер. Отображает сообщение с инструкцией в случае отсутствия камер (первые 6 индексов) и
        сообщение об ошибке, если не получает изображение от работающей камеры.
        """
        index = 0
        is_camera_connect = False
        while index != 5:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                index += 1
                continue
            else:
                is_camera_connect = True
                break

        if is_camera_connect:
            c = cv2.VideoCapture(index)
            ret, frame = c.read()
            if ret:
                self.selected_image = Image(frame, "Без эффекта", )
                self.displayed_image = self.selected_image.get_image()
                self.display_image()
                if not self.is_loaded:
                    self.add_function_panel()
                    self.is_loaded = True
                else:
                    self.update_function_panel()
            else:
                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Critical)
                error_box.setText(
                    "Невозможно сделать снимок. Проверьте исправность подключенных камер")
                error_box.setWindowTitle("Ошибка")
                error_box.exec_()
        else:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setText(
                "Невозможно сделать снимок.\n Убедитесь, что к устройству подключена работающая камера\n"
                "Перейдите: Диспетчер устройств >> Камеры\n"
                " ---Если устройство отображается: правая кнопка мыши >> включить устройство\n"
                " ---Иначе: Проверьте исправность подключения")
            error_box.setWindowTitle("Ошибка")
            error_box.exec_()

    def display_image(self):
        """Выводит изображение на экран

        Запускается при каждом изменении изображения. Меняет размер изображения для размещения в окне. Создает копии
        атрибутов self.selected_image, преобразует изображение согласно действиям в массиве self.actions, удаляя
        значения из копий атрибутов.
        """
        self.editing_is_complete = False
        self.displayed_image = self.selected_image.get_image()
        self.crop_coordinates_list = self.selected_image.get_crop_coordinates().copy()
        self.draw_coordinates_list = self.selected_image.get_draw_coordinates().copy()
        self.rotate_angels_list = self.selected_image.get_angel_rotation().copy()

        height, width, channels = self.displayed_image.shape

        width_ratio = 1000 / width  # Определение коэффициента масштабирования для ширины
        scaled_width = 1000
        scaled_height = int(height * width_ratio)

        if scaled_height > 500:  # Регулирование высоты, чтобы изображение не было слишком высоким
            height_ratio = 500 / scaled_height
            scaled_height = 500
            scaled_width = int(scaled_width * height_ratio)

        self.displayed_image = cv2.resize(
            self.displayed_image, (scaled_width, scaled_height))

        for i in self.actions:
            try:
                if i == "crop":
                    self.crop_image()
                    self.crop_coordinates_list.pop(0)
                elif i == "rotate":
                    self.rotate_image()
                    self.rotate_angels_list.pop(0)
                elif i == "draw":
                    self.draw_blue_rectangle()
                    self.draw_coordinates_list.pop(0)
            except IndexError:
                continue
        self.change_channel(self.selected_image.get_color_channel())
        height, width, channels = self.displayed_image.shape

        width_ratio = 1000 / width
        scaled_width = 1000
        scaled_height = int(height * width_ratio)

        if scaled_height > 500:
            height_ratio = 500 / scaled_height
            scaled_height = 500
            scaled_width = int(scaled_width * height_ratio)

        image = cv2.resize(self.displayed_image, (scaled_width, scaled_height))
        bytes_per_line = channels * scaled_width
        q_img = QImage(image.data, scaled_width, scaled_height, bytes_per_line,
                       QImage.Format_RGB888).rgbSwapped()

        # Создание нового изображения с пустым пространством по бокам
        new_image = QImage(1000, 500, QImage.Format_RGB888)
        new_image.fill(Qt.white)
        painter = QPainter(new_image)
        painter.drawImage(
            (1000 - scaled_width) // 2,
            (500 - scaled_height) // 2,
            q_img)
        painter.end()
        self.displayed_image = image
        self.update_function_panel()
        self.label_image.setPixmap(QPixmap.fromImage(new_image))
        self.editing_is_complete = True

    def change_channel(self, channel):
        """Меняет цветовой канал

        Если нажата соответствующая кнопка: обновляет аттрибут Image - self.color_channel
        Если идет процесс редактирования для отображения: изменяет self.displayed_image
        """
        if self.editing_is_complete:
            self.selected_image.set_color_channel(channel)
            self.display_image()
        else:
            red, green, blue = cv2.split(self.displayed_image)
            if channel == "Красный":
                self.displayed_image = cv2.merge(
                    (np.zeros_like(blue), np.zeros_like(blue), blue))
            elif channel == "Зеленый":
                self.displayed_image = cv2.merge(
                    (np.zeros_like(green), green, np.zeros_like(green)))
            elif channel == "Синий":
                self.displayed_image = cv2.merge(
                    (red, np.zeros_like(red), np.zeros_like(red)))

    def crop_image(self):
        """Обрезает изображение по координатам

        Если нажата соответствующая кнопка: обновляет аттрибут Image - self.crop_coordinates - обновляет self.actions
        Если идет процесс редактирования для отображения: изменяет self.displayed_image по первым координатам в
        self.crop_coordinates_list
        """
        if self.editing_is_complete:
            x1, y1, x2, y2 = [sb.value() for sb in self.crop_spin_boxes]
            if x2 <= x1 or y2 <= y1:
                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Critical)
                error_box.setText("Вторые координаты должны быть больше первых")
                error_box.setWindowTitle("Ошибка")
                error_box.exec_()
                return
            self.selected_image.crop_coordinates.append([y1, y2, x1, x2])
            self.actions.append("crop")
            self.display_image()
        else:
            c_crop = self.crop_coordinates_list[0]
            if c_crop is not []:
                self.displayed_image = self.displayed_image[c_crop[0]:c_crop[1], c_crop[2]:c_crop[3]]

    def rotate_image(self):
        """Поворачивает изображение по значению угла

        Если нажата соответствующая кнопка: обновляет аттрибут Image - self.angel_rotation - обновляет self.actions,
        если пользователь несколько раз подряд поворачивает изображения, получается итоговый угол поворота
        Если идет процесс редактирования для отображения: изменяет self.displayed_image по первым координатам в
        self.crop_coordinates_list. Для корректного отображения без обрезания сторон, длина и ширина
        изображения меняются.
        """
        if self.editing_is_complete:
            if self.actions != [] and self.actions[-1] == "rotate":
                print(self.actions)
                old_angel = self.selected_image.get_angel_rotation()[-1]
                self.selected_image.angel_rotation.append(
                    self.rotation_spin_box.value() + old_angel)
                print(self.rotation_spin_box.value() + old_angel)
                self.selected_image.angel_rotation.pop(-2)
            else:
                self.selected_image.angel_rotation.append(
                    self.rotation_spin_box.value())
                self.actions.append("rotate")
            self.display_image()
        else:
            angel = self.rotate_angels_list[0]
            if angel is not None:
                height, width = self.displayed_image.shape[:2]
                centre = (width // 2, height // 2)

                rotation_matrix = cv2.getRotationMatrix2D(centre, angel, 1)

                cos_of_rotation_matrix = np.abs(rotation_matrix[0][0])
                sin_of_rotation_matrix = np.abs(rotation_matrix[0][1])

                new_image_height = int((height * cos_of_rotation_matrix) +
                                       (width * sin_of_rotation_matrix))
                new_image_width = int((height * sin_of_rotation_matrix) +
                                      (width * cos_of_rotation_matrix))

                rotation_matrix[0][2] += (new_image_width - width) / 2
                rotation_matrix[1][2] += (new_image_height - height) / 2

                self.displayed_image = cv2.warpAffine(
                    self.displayed_image, rotation_matrix, (new_image_width, new_image_height))

    def draw_blue_rectangle(self):
        """Рисует синий прямоугольник на изображении по координатам двух противоположных углов

        Если нажата соответствующая кнопка: обновляет аттрибут Image - self.draw_coordinates - обновляет self.actions,
        Если идет процесс редактирования для отображения: изменяет self.displayed_image по первым координатам в
        self.draw_coordinates_list.

        """
        if self.editing_is_complete:
            x1, y1, x2, y2 = [sb.value() for sb in self.draw_spin_boxes]
            self.selected_image.draw_coordinates.append([y1, y2, x1, x2])
            self.actions.append("draw")
            print("yt")
            self.display_image()
        else:
            coordinates_list = self.draw_coordinates_list
            print(self.draw_coordinates_list)
            if coordinates_list is not []:
                d_c = coordinates_list[0]
                cv2.rectangle(
                    self.displayed_image, (d_c[2], d_c[0]), (d_c[3], d_c[1]), (255, 0, 0), 2)

    def cancel_changes(self):
        """Отменяет все действия, совершенные над изображением

        Сбрасывает массив self.actions, обновляет self.displayed_image на изначальное изображение,
        создает новый объект Image
        """
        self.displayed_image = self.selected_image.get_image()
        self.selected_image = Image(self.displayed_image)
        self.display_image()
        self.actions = []


class Image:
    """Класс Image используется для хранения изображения, его свойств, и истории действий, совершенных над ним

        Attributes
        ----------
        image : numpy.ndarray
            Изображение - многомерный массив
        color_channel : str
            Названия цветового канала изображения: "Красный", "Синий", "Зеленый", "Без эффекта"
        angel_rotation : list
            Список из значений углов поворота изображения
        crop_coordinates : list
            Список списков, каждый состоит из координат для обрезки изображения: [y1, y2, x1, x2]
        draw_coordinates : list
            Список списков, состоит из координат для рисования синего прямоугольника на изображении: [y1, y2, x1, x2]
        """

    def __init__(
            self,
            image=None,
            color_channel="Без эффекта",
            angel_rotation=None,
            crop_coordinates=None,
            draw_coordinates=None):
        if draw_coordinates is None:
            draw_coordinates = []
        if angel_rotation is None:
            angel_rotation = []
        if crop_coordinates is None:
            crop_coordinates = []
        self.image = image
        self.color_channel = color_channel
        self.angel_rotation = angel_rotation
        self.crop_coordinates = crop_coordinates
        self.draw_coordinates = draw_coordinates

    def set_color_channel(self, color_channel):
        self.color_channel = color_channel

    def set_angel_rotation(self, angel_rotation):
        self.angel_rotation = angel_rotation

    def set_crop_coordinates(self, crop_coordinates):
        self.crop_coordinates = crop_coordinates

    def set_draw_coordinates(self, draw_coordinates):
        self.draw_coordinates = draw_coordinates

    def get_color_channel(self):
        return self.color_channel

    def get_angel_rotation(self):
        return self.angel_rotation

    def get_crop_coordinates(self):
        return self.crop_coordinates

    def get_draw_coordinates(self):
        return self.draw_coordinates

    def get_image(self):
        return self.image


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
