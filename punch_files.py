#!/usr/bin/env python3

# 029 Puncher (Jul-17-2025)
# By Luca Severini

# punch_files.py

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QMessageBox, QMainWindow, QTextEdit, QApplication
from CDto029b import punch_file
from CDto029b import punching_stopped
import os
import time

class PunchFilesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ETL Control Panel")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.file_label = QLabel("No file selected")
        
        self.select_button = QPushButton("Select File to Punch")
        self.select_button.clicked.connect(self.select_file)
        
        self.punch_button = QPushButton("Punch Selected File")
        self.punch_button.clicked.connect(self.punch_file)
        
        self.stop_button = QPushButton("Stop Punching")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_punching_file) 
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: red; 
                color: black; 
                border-radius: 8px;
                border: 1px solid black;
                font-weight: bold;
                font-size: 16px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ff4444;
            }
            QPushButton:disabled {
                background-color: #888888;
                color: #444444;
                border: 1px solid #666666;
            }
        """)

        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.file_label)
        self.layout.addWidget(self.punch_button)
        self.layout.addWidget(self.stop_button)

        self.arduino_label = QLabel("Arduino Messages:")
        self.arduino_messages = QTextEdit()
        self.arduino_messages.setReadOnly(True)
        
        self.layout.addWidget(self.arduino_label, 0)
        self.layout.addWidget(self.arduino_messages, 1)

        self.cd_file = None
        
        self.resize(800, 600)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select a Card Deck (.cd) or a Text file (.txt)", "", "Card Deck or Text Files (*.cd *.txt)")
        if path:
            self.cd_file = path
            filename = os.path.basename(path)
            self.file_label.setText(f"Selected: {filename}")
            self.punch_button.setText(f"Punch {filename}")

    def continue_punching(self):
        try:
            punch_file(self.cd_file)
            
            filename = os.path.basename(self.cd_file)
            QMessageBox.information(self, "Success", f"CD file {filename} punched.")
            
            self.stop_button.setEnabled(False)
            
        except Exception as e:
            filename = os.path.basename(self.cd_file)
            QMessageBox.critical(self, f"Punch {filename} failed", str(e))

    def punch_file(self):
        if not self.cd_file:
            QMessageBox.warning(self, "No File", "Please select a file.")
            return
        try:
            punching_stopped = False
            
            self.stop_button.setEnabled(True)
            
            # Use QTimer for the delay to let the GUI fully update, then continue with punching
            QTimer.singleShot(1000, self.continue_punching)  # 1 second delay
                        
        except Exception as e:
            filename = os.path.basename(self.cd_file)
            QMessageBox.critical(self, f"Punching {filename} failed.", str(e))

    def add_arduino_message(self, message):
        """Add a message to the Arduino messages display"""
        self.arduino_messages.append(message)
        # Auto-scroll to bottom
        self.arduino_messages.verticalScrollBar().setValue(
            self.arduino_messages.verticalScrollBar().maximum()
        )

    def stop_punching_file(self):
        punching_stopped = True
        QMessageBox.critical(self, "Punching stopped.", "...")
