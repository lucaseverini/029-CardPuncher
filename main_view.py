#!/usr/bin/env python3

# 029 Puncher
# main_view.py (8-23-2025)
# By Luca Severini (lucaseverini@mac.com)

import os
import time
from PyQt5.QtCore import Qt, QTimer, QObject, QThread, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMenu, QAction
from PyQt5.QtWidgets import QHBoxLayout, QMessageBox, QMainWindow, QTextEdit, QApplication, QSpinBox
from CDto029b import punch_file, punch_file_test, punching_stopped
from worker import PunchWorker

kPunchMethod = punch_file # punch_file / punch_file_test 

class LogTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

    def _show_menu(self, pos):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self.clear)
        menu.addAction(clear_action)
        menu.exec_(self.mapToGlobal(pos))
        
class MainView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ETL Control Panel")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(6)
        self._range_widgets_added = False
        self._range_warning_shown = False
 
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

        self.arduino_label = QLabel("Punching operations log:")
        self.arduino_messages = LogTextEdit()
        
        font = QFont()
        font.setStyleHint(QFont.TypeWriter)   # Pick a fixed-pitch font
        
        self.arduino_messages.setFont(font)
        self.arduino_messages.setReadOnly(True)
       
        self.layout.addWidget(self.arduino_label, 0)
        self.layout.addWidget(self.arduino_messages, 1)
               
        self.cd_file = None
        
        self.resize(800, 600)

    def select_file(self):
        # File unselected
        if QApplication.keyboardModifiers() & Qt.AltModifier:
            self.cd_file = None
            self.file_label.setText("No file selected")
            self.punch_button.setText("Punch Selected File")
            self.punch_button.setEnabled(False)
            
            self.layout.removeWidget(self.range_row_widget)
            self.range_row_widget.setParent(None)
            
            self.layout.removeWidget(self.rows_total_label)
            self.rows_total_label.setParent(None)

            self._range_widgets_added = False
 
            return

        # File selected
        path, _ = QFileDialog.getOpenFileName(self, "Select a Card Deck (.cd) or a Text file (.txt)", "", "Card Deck or Text Files (*.cd *.txt)")
        if path:
            print(f"Selected file: {path}")
            self.cd_file = path
            filename = os.path.basename(path)
            self.file_label.setText(f"Selected file: {filename}")
            self.punch_button.setText(f"Punch {filename}")
            self.punch_button.setEnabled(True)

            # Count rows (cards) in the selected file
            try:
                self._rows_total = 0
                with open(path, "rb") as f:
                    for _ in f:  # splitlines-agnostic, works with CRLF or LF
                        self._rows_total += 1

                if not self._range_widgets_added:
                
                    self.rows_total_label = QLabel("")
                    self.range_start = QSpinBox(); self.range_start.setMinimum(1)
                    self.range_end = QSpinBox(); self.range_end.setMinimum(1)

                    fm = self.range_start.fontMetrics()
                    min_width = fm.horizontalAdvance('0' * 7)
                    self.range_start.setMinimumWidth(min_width)
                    self.range_end.setMinimumWidth(min_width)

                    row = QHBoxLayout()
                    row.addWidget(QLabel("Range of rows to punch:"))
                    row.addWidget(self.range_start)
                    row.addWidget(QLabel("to"))
                    row.addWidget(self.range_end)
                    row.addStretch(1)

                    self.range_row_widget = QWidget()
                    self.range_row_widget.setLayout(row)
                    self.range_row_widget.setVisible(True)
                    self.range_row_widget.layout().setContentsMargins(0, 0, 0, 0)

                    # Insert between file_label and punch_button
                    idx = self.layout.indexOf(self.punch_button)
                    self.layout.insertWidget(idx, self.rows_total_label)
                    self.layout.insertWidget(idx + 1, self.range_row_widget)
                    
                    # Keep end ≥ start
                    def _sync_end_min(v):
                        if self.range_end.value() < v:
                            self.range_end.setValue(v)
                            if not self._range_warning_shown:
                                QMessageBox.warning(self, "", "End of range cannot be smaller than start.")
                                self._range_warning_shown = True
                        self.range_end.setMinimum(v)

                
                    def _sync_start_max(v):
                        if self.range_start.value() > v:
                            self.range_start.setValue(v)
                            if not self._range_warning_shown:
                                QMessageBox.warning(self, "", "Start of range cannot be larger than end.")
                                self._range_warning_shown = True
                        self.range_start.setMaximum(v)
                    
                    self.range_start.valueChanged.connect(_sync_end_min)
                    self.range_end.valueChanged.connect(_sync_start_max)

                    self._range_widgets_added = True

                self.rows_total_label.setText(f"Total rows: {self._rows_total}")
                self.range_start.setMinimum(1)
                self.range_start.setMaximum(self._rows_total)
                self.range_start.setValue(1)
                self.range_end.setMinimum(1)
                self.range_end.setMaximum(self._rows_total)
                self.range_end.setValue(self._rows_total)                

            except Exception as e:
                QMessageBox.critical(self, "Error counting file rows:", str(e))
    
    def punch_file(self):
        if not self.cd_file:
            QMessageBox.warning(self, "No File", "Please select a .cd or .txt file to punch .")
            return

        self.stop_button.setEnabled(True)
        file_name = os.path.basename(self.cd_file)
        
        try:
            # Create thread + worker
            self.worker = PunchWorker(kPunchMethod, self.cd_file)
            self.thread = QThread(self)
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

            row_start = self.range_start.value()
            row_end = self.range_end.value()
            row_range = (row_start, row_end)
            punch_all = (row_end - row_start + 1) == self._rows_total
            self.worker.kwargs = { "log": self.worker.message.emit, "range": row_range, "punch_all": punch_all }
            self.worker.args = (self.cd_file,)

            self.thread.start()

        except Exception as e:
            QMessageBox.critical(self, f"Punch {file_name} failed. Error:", str(e))

    def stop_punching_file(self):
        punching_stopped.set()
 
    @pyqtSlot(object, bool, tuple)
    def _on_punch_result(self, response, aborted, row_range):
        print(f"aborted: {aborted}")
        print(f"row_range: {row_range}")
        if aborted:
            print(f"Punch Interrupted: {response}")
            QMessageBox.warning(self, "Punch Interrupted", response)
        else:
            print(f"Punch Completed: {response}")
            QMessageBox.information(self, "Punch Completed", response)

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
