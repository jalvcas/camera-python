from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import sys
import cv2
import wmi

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        list_available_cameras()

        # Create a QComboBox
        self.combo_box = QComboBox()
        self.combo_box.addItem(QIcon("icon1.png"), "Option 1")
        self.combo_box.addItem(QIcon("icon2.png"), "Option 2")
        self.combo_box.addItem(QIcon("icon3.png"), "Option 3")

        self.setWindowTitle("QComboBox Example")
        self.setGeometry(100, 100, 300, 200)

        # Create a central widget and set layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add the combo box to the layout
        layout.addWidget(self.combo_box)

def list_available_cameras():
    available_cameras = []
    max_camera_index = 10

    c = wmi.WMI()
    wmi_devices = c.Win32_PnPEntity(PNPClass="Camera")

    print(f"Found {len(wmi_devices)} imaging devices via WMI")
    for device in wmi_devices:
        print(f"Device: {device.Name}")
        print(f"Device ID: {device.DeviceID}")

    for index in range(max_camera_index):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Camera {index} is working.")
                if index < len(wmi_devices):
                    available_cameras.append((index, wmi_devices[index].Name))
                else:
                    available_cameras.append((index, f"Unknown Camera {index}"))

        cap.release()

    return available_cameras

app = QApplication(sys.argv)
window = MainWindow()
window.show()

print(list_available_cameras())

sys.exit(app.exec())