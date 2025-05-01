from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QComboBox, QPushButton, QWidget

import sys
import wmi
import cv2

def list_camera_devices_wmi():
    
        # Get the WMI service
        c = wmi.WMI()
        
        # Query all video devices
        wmi_devices = c.Win32_PnPEntity(PNPClass="Camera")
        
        print(f"Found {len(wmi_devices)} imaging devices via WMI:")
        for i, device in enumerate(wmi_devices):
            print(f"Device {i}: {device.Name}")
        
        # Now check which ones OpenCV can access
        available_cameras = []
        max_to_check = 10  # Check reasonable number of indices
        
        for i in range(max_to_check):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # We have a working camera at this index
                    print(f"\nOpenCV camera at index {i} is working")
                    # Try to match it with a WMI device (imperfect, but provides a guess)
                    if i < len(wmi_devices):
                        available_cameras.append((i, wmi_devices[i].Name))
                    else:
                        available_cameras.append((i, f"Unknown Camera {i}"))
                cap.release()
        
        return available_cameras


class WebcamTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Webcam Test")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # Label
        self.device_label = QLabel("Select Camera Device:")
        layout.addWidget(self.device_label)

        # Dropdown for camera selection
        self.camera_dropdown = QComboBox()
        layout.addWidget(self.camera_dropdown)

        self.cameras = list_camera_devices_wmi()
        if self.cameras:
            for index, name in self.cameras:
                if name.startswith("Unknown Camera"):
                    break
                # Add both the index and name to the dropdown
                self.camera_dropdown.addItem(f"{name} (Index: {index})", index)
        else:
            self.camera_dropdown.addItem("No cameras found")

        # Button to select camera
        select_button = QPushButton("Select Camera")
        select_button.clicked.connect(self.select_camera)
        layout.addWidget(select_button)

        # Status label
        self.status_label = QLabel("No camera selected")
        layout.addWidget(self.status_label)

        self.setCentralWidget(main_widget)

    def select_camera(self):
        if not self.cameras:
            self.status_label.setText("No cameras available")
            return

        # Get the selected camera index from the dropdown's user data
        selected_index = self.camera_dropdown.currentIndex()
        if selected_index >= 0:
            camera_index = self.camera_dropdown.itemData(selected_index)
            camera_name = self.camera_dropdown.currentText().split(" (Index:")[0]
            
            self.status_label.setText(f"Selected: {camera_name} (Index: {camera_index})")
            print(f"Selected camera index: {camera_index}, name: {camera_name}")
    

app = QApplication(sys.argv)
window = WebcamTest()
window.show()
sys.exit(app.exec())