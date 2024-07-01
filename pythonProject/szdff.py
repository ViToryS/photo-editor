import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog

def capture_image():
    c = cv2.VideoCapture(0)
    ret, frame = c.read()
    if ret:
        cv2.imshow("dfrd", frame)
        cv2.waitKey(0)

        height, width = frame.shape[0], frame.shape[1]
        centre_y, centre_x = height // 2, width // 2
        print(centre_y, centre_x)

        rotation_matrix = cv2.getRotationMatrix2D((centre_y, centre_x), 45, 1)

        cos_of_rotation_matrix = np.abs(rotation_matrix[0][0])
        sin_of_rotation_matrix = np.abs(rotation_matrix[0][1])

        new_image_height = int((height * sin_of_rotation_matrix) +
                             (width * cos_of_rotation_matrix))
        new_image_width = int((height * cos_of_rotation_matrix) +
                            (width * sin_of_rotation_matrix))

        rotation_matrix[0][2] += (new_image_width / 2) - centre_x
        rotation_matrix[1][2] += (new_image_height / 2) - centre_y

        rotating_image = cv2.warpAffine(
           frame, rotation_matrix, (width, height))
        cv2.imshow("dgdg", rotating_image)
        cv2.waitKey(0)


capture_image()


