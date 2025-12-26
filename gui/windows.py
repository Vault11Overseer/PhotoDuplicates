from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel,
    QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from backend.scanner import find_duplicates
import sys
import os
from PIL import Image
import time
import getpass
from send2trash import send2trash  # Added for safe deletion

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Duplicates")
        self.resize(900, 750)

        # Dark background
        self.setStyleSheet("background-color: #121212; color: white;")

        # Layouts
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)

        # Folder selection
        self.label = QLabel("Select a folder to scan for duplicates")
        self.label.setFont(QFont("Arial", 14, QFont.Bold))
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.btn_select_folder = QPushButton("Select Folder")
        self.btn_select_folder.clicked.connect(self.select_folder)
        self.btn_select_folder.setStyleSheet("""
            QPushButton {
                background-color: #006400; color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008000;
            }
        """)
        self.layout.addWidget(self.btn_select_folder, alignment=Qt.AlignCenter)

        # Duplicate display
        self.duplicate_layout = QHBoxLayout()
        self.duplicate_layout.setSpacing(30)
        self.layout.addLayout(self.duplicate_layout)

        # Left image and metadata
        self.left_vbox = QVBoxLayout()
        self.left_image_label = QLabel()
        self.left_image_label.setFixedSize(400, 400)
        self.left_image_label.setStyleSheet("""
            border: 2px solid white;
            border-radius: 10px;
            background-color: #1e1e1e;
        """)
        self.left_vbox.addWidget(self.left_image_label)
        self.left_metadata_label = QLabel()
        self.left_metadata_label.setAlignment(Qt.AlignCenter)
        self.left_metadata_label.setWordWrap(True)
        self.left_metadata_label.setFont(QFont("Arial", 10))
        self.left_vbox.addWidget(self.left_metadata_label)
        self.duplicate_layout.addLayout(self.left_vbox)

        # Right image and metadata
        self.right_vbox = QVBoxLayout()
        self.right_image_label = QLabel()
        self.right_image_label.setFixedSize(400, 400)
        self.right_image_label.setStyleSheet("""
            border: 2px solid white;
            border-radius: 10px;
            background-color: #1e1e1e;
        """)
        self.right_vbox.addWidget(self.right_image_label)
        self.right_metadata_label = QLabel()
        self.right_metadata_label.setAlignment(Qt.AlignCenter)
        self.right_metadata_label.setWordWrap(True)
        self.right_metadata_label.setFont(QFont("Arial", 10))
        self.right_vbox.addWidget(self.right_metadata_label)
        self.duplicate_layout.addLayout(self.right_vbox)

        # Buttons
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(20)
        self.layout.addLayout(self.btn_layout)

        self.btn_delete_left = QPushButton("Delete Left")
        self.btn_delete_left.clicked.connect(lambda: self.delete_image(side="left"))
        self.btn_delete_left.setStyleSheet("""
            QPushButton {
                background-color: #b71c1c; color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.btn_layout.addWidget(self.btn_delete_left)

        self.btn_delete_right = QPushButton("Delete Right")
        self.btn_delete_right.clicked.connect(lambda: self.delete_image(side="right"))
        self.btn_delete_right.setStyleSheet("""
            QPushButton {
                background-color: #b71c1c; color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.btn_layout.addWidget(self.btn_delete_right)

        self.btn_skip = QPushButton("Skip")
        self.btn_skip.clicked.connect(self.next_duplicate)
        self.btn_skip.setStyleSheet("""
            QPushButton {
                background-color: #006400; color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008000;
            }
        """)
        self.btn_layout.addWidget(self.btn_skip)

        # Hide duplicate widgets initially
        self.left_image_label.hide()
        self.right_image_label.hide()
        self.left_metadata_label.hide()
        self.right_metadata_label.hide()
        self.btn_delete_left.hide()
        self.btn_delete_right.hide()
        self.btn_skip.hide()

        # Duplicate tracking
        self.duplicates = []
        self.current_index = 0

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.duplicates = find_duplicates(folder)
            if not self.duplicates:
                QMessageBox.information(self, "No duplicates", "No duplicates found!")
                return
            self.current_index = 0

            # Show duplicate widgets
            self.left_image_label.show()
            self.right_image_label.show()
            self.left_metadata_label.show()
            self.right_metadata_label.show()
            self.btn_delete_left.show()
            self.btn_delete_right.show()
            self.btn_skip.show()

            self.show_duplicate()

    def show_duplicate(self):
        if self.current_index >= len(self.duplicates):
            QMessageBox.information(self, "Done", "No more duplicates to review!")

            # Hide duplicate widgets again
            self.left_image_label.hide()
            self.right_image_label.hide()
            self.left_metadata_label.hide()
            self.right_metadata_label.hide()
            self.btn_delete_left.hide()
            self.btn_delete_right.hide()
            self.btn_skip.hide()
            return

        left_path, right_path = self.duplicates[self.current_index]

        # Load and scale images
        left_pixmap = QPixmap(left_path).scaled(400, 400, Qt.KeepAspectRatio)
        right_pixmap = QPixmap(right_path).scaled(400, 400, Qt.KeepAspectRatio)
        self.left_image_label.setPixmap(left_pixmap)
        self.right_image_label.setPixmap(right_pixmap)

        # Set metadata
        self.left_metadata_label.setText(self.get_image_metadata(left_path))
        self.right_metadata_label.setText(self.get_image_metadata(right_path))

    def get_image_metadata(self, path):
        try:
            size_kb = os.path.getsize(path) / 1024
            with Image.open(path) as img:
                width, height = img.size

            # Creation time
            creation_time = time.ctime(os.path.getctime(path))

            # User / owner
            user = getpass.getuser()

            return (f"Filename: {os.path.basename(path)}\n"
                    f"Dimensions: {width}x{height} px\n"
                    f"Size: {size_kb:.1f} KB\n"
                    f"Created: {creation_time}\n"
                    f"User: {user}")
        except Exception:
            return f"Filename: {os.path.basename(path)}\nMetadata not available"

    def delete_image(self, side):
        left_path, right_path = self.duplicates[self.current_index]
    # Convert to absolute path
        path_to_delete = os.path.abspath(left_path if side == "left" else right_path)

        try:
            send2trash(path_to_delete)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to move file to Trash:\n{e}")


    def next_duplicate(self):
        self.current_index += 1
        self.show_duplicate()

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
