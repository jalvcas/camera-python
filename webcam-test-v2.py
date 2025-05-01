from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QComboBox, QPushButton, QWidget, QHBoxLayout, QGroupBox,QTextEdit,QStatusBar, QSizePolicy
from PyQt6.QtGui import QImage, QPixmap, QFont


import sys
import wmi
import cv2
import time
from datetime import datetime

def list_camera_devices_wmi():
        c = wmi.WMI()
        wmi_devices = c.Win32_PnPEntity(PNPClass="Camera")
        
        print(f"Found {len(wmi_devices)} imaging devices via WMI:")
        for i, device in enumerate(wmi_devices):
            print(f"Device {i}: {device.Name}")

        available_cameras = []
        max_to_check = 10  # Check reasonable number of indices
        
        for i in range(max_to_check):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"\nOpenCV camera at index {i} is working")
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
        self.setGeometry(100, 100, 1000, 700)
        
        # Initialize variables
        self.cap = None
        self.current_camera_index = None
        self.frame_count =0
        self.start_time = 0
        self.fps = 0
        self.resolution = (0,0)

        # Create the main layout
        self.setup_ui()

        # Load available cameras
        self.load_cameras()


    def setup_ui(self):
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Left panel: Control and status
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(300)

        # Camera controls group
        controls_group = QGroupBox("Camera Controls")
        controls_layout = QVBoxLayout(controls_group)

        # Camera selector
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Camera:")
        self.camera_combo = QComboBox()
        self.camera_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.camera_combo)
        controls_layout.addLayout(selector_layout)

        left_layout.addWidget(controls_group)

        # TODO: Camera control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.load_cameras)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.refresh_button)
        controls_layout.addLayout(button_layout)

        left_layout.addWidget(controls_group)

        # Status information group
        status_group=QGroupBox("Camera Status")
        status_layout = QVBoxLayout(status_group)

        # Status text display
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(200)
        status_layout.addWidget(self.status_text)

        left_layout.addWidget(status_group)

        # Log group
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout(log_group)

        # Log text display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        left_layout.addWidget(log_group)

        # Right panel: Video display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Video frame
        self.video_frame = QLabel()
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setMinimumSize(640, 480)
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setText("No Camera Feed")
        self.video_frame.setFont(QFont("Arial",14))

        # Add video frame to right panel
        right_layout.addWidget(self.video_frame)

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)

        # Status bar at the bottom
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

    def load_cameras(self):
        """Load available cameras into the combo box."""
        self.camera_combo.clear()
        
        self.cameras = list_camera_devices_wmi()
        if self.cameras:
            for index, name in self.cameras:
                self.camera_combo.addItem(f"{name} (Index: {index})", index)
            self.log_message(f"Found {len(self.cameras)} camera(s)")
            # TODO self.start_button.setEnabled(True)
        else:
            self.camera_combo.addItem("No cameras found")
            self.log_message("No cameras found")
            # TODO self.start_button.setEnabled(True)

        self.update_status_info()

    def start_camera(self):
        """Start the selected camera."""
        selected_index = self.camera_combo.currentIndex()
        if selected_index >= 0:
            camera_index = self.camera_combo.itemData(selected_index)
            camera_name = self.camera_combo.currentText().slipt(" (Index:")[0]

        self.stop_camera()

        self.cap= cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if self.cap.isOpened():
            # Get camera properties
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.resolution = (width, height)

            # Start capturing frames
            self.current_camera_index = camera_index
            self.frame_count = 0
            self.start_time = time.time()
            self.timer.start(30)  # ~33 fps

            # Update UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.camera_combo.setEnabled(False)
            self.refresh_button.setEnabled(False)

            # Log the action
            self.log_message(f"Started camera: {camera_name} (Index: {camera_index})")
            self.statusBar.showMessage(f"Camera started: {camera_name}")
        else:
            self.log_message(f"Failed to open camera: {camera_name} (Index: {camera_index})")
            self.statusBar.showMessage(f"Failed to open camera: {camera_name}")

    def stop_camera(self):
        pass

    @pyqtSlot()
    def update_status(self):
        """Update the status information periodically."""
        self.update_status_info()

    def update_status_info(self):
        """Update the status information panel."""
        status_text = "Información del estado"

        # TODO: Completar

        self.status_text.setText(status_text)

    def log_message(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamTest()
    window.show()
    sys.exit(app.exec())
