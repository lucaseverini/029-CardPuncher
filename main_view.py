#!/usr/bin/env python3

# 029 Puncher
# main_view.py (8-23-2025)
# By Luca Severini (lucaseverini@mac.com)

import os
import time
from PyQt5.QtCore import Qt, QTimer, QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QMessageBox, QMainWindow, QTextEdit, QApplication
from CDto029b import punch_file, punch_file_test, punching_stopped
from worker import PunchWorker

class MainView(QWidget):
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
        self.punch_button.setEnabled(False)
        
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
            print(f"Selected file: {path}")
            self.cd_file = path
            filename = os.path.basename(path)
            self.file_label.setText(f"Selected: {filename}")
            self.punch_button.setText(f"Punch {filename}")
            self.punch_button.setEnabled(True)

    def continue_punching(self):
        self.stop_button.setEnabled(True)
        file_name = os.path.basename(self.cd_file)
        
        try:
            # Create thread + worker
            self.thread = QThread(self)
            self.worker = PunchWorker(punch_file_test, self.cd_file)
            self.worker.moveToThread(self.thread)

            # Start + cleanup
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            # Show outcome and errors and disable Stop when done
            self.worker.result.connect(self._on_punch_result)
            self.worker.error.connect(self._on_punch_error)         
            self.worker.finished.connect(self._on_punch_finished)
            self.worker.message.connect(self._on_punch_log)

            # Patch the func args so punch_file_test will get the emitter
            self.worker.args = (self.cd_file,)
            self.worker.kwargs = {"log": self.worker.message.emit}

            self.thread.start()

        except Exception as e:
            QMessageBox.critical(self, f"Punch {file_name} failed", str(e))

    def punch_file(self):
        if not self.cd_file:
            QMessageBox.warning(self, "No File", "Please select a .cd or .txt file to punch .")
            return
        try:            
            # Use QTimer for the delay to let the GUI fully update, then continue with punching
            QTimer.singleShot(1000, self.continue_punching)  # 1 second delay
                        
        except Exception as e:
            file_name = os.path.basename(self.cd_file)
            QMessageBox.critical(self, f"Punching {file_name} failed.", str(e))

    def add_arduino_message(self, message):
        """Add a message to the Arduino messages display"""
        self.arduino_messages.append(message)
        # Auto-scroll to bottom
        self.arduino_messages.verticalScrollBar().setValue(
            self.arduino_messages.verticalScrollBar().maximum()
        )

    def stop_punching_file(self):
        punching_stopped.set()
 
    @pyqtSlot(object)
    def _on_punch_result(self, res):
        msg = str(res)
        if msg.lower().startswith("aborted"):
            print(f"Punching aborted: {msg}")
            QMessageBox.warning(self, "Punching Aborted", msg)
        else:
            print(f"Punching completed: {msg}")
            QMessageBox.information(self, "Punching Completed", msg)

    @pyqtSlot(object)
    def _on_punch_error(self, err):
        msg = str(err)
        print(f"Punching error: {msg}")
        QMessageBox.critical(self, "Punching Error", msg)

    @pyqtSlot(object)
    def _on_punch_log(self, log):
        msg = str(log)
        self.arduino_messages.append(msg)

    @pyqtSlot()
    def _on_punch_finished(self):        
        self.stop_button.setEnabled(False)
