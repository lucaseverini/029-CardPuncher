#!/usr/bin/env python3

# 029 Puncher (Jul-17-2025)
# By Luca Severini

# main_window.py

from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit, QLabel
from PyQt5.QtWidgets import QComboBox, QMessageBox
from PyQt5.QtWidgets import QWidget, QInputDialog, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from punch_files import PunchFilesView
from git import get_git_version
from datetime import datetime
import os
import sys
import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.menu = self.menuBar()

        self.current_widget = None
                
        # Info menu
        self.info_menu = self.menu.addMenu("Info")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        self.info_menu.addAction(about_action)

        # Actions menu
        self.actions_menu = self.menu.addMenu("Actions")

        self.action_punch_cd_files = QAction("Punch Files…", self)
        self.action_punch_cd_files.triggered.connect(self.show_punch_files)
        self.actions_menu.addAction(self.action_punch_cd_files)

        # Utilities menu
        self.utils_menu = self.menu.addMenu("Utilities")
        self.action_clear_log = QAction("Clear Log", self)
        self.action_clear_log.triggered.connect(self.clear_log)
        self.utils_menu.addAction(self.action_clear_log)
                        
        self.show_punch_files()
        # self.show_about_dialog()
            
        self.resize(600, 400)
        self.center_on_screen()
        
    def set_window_title(self):
        version = get_git_version()
        version_str = f" - version 0.{version}" if version else ""
        self.setWindowTitle(f"029 Puncher{version_str}")

    def set_central_widget(self, widget):
        if self.current_widget:
            self.current_widget.setParent(None)
        self.current_widget = widget
        self.setCentralWidget(widget)
        self.set_window_title()

    def center_on_screen(self):
        frame = self.frameGeometry()
        screen = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())
                
    def show_punch_files(self):
        if not hasattr(self, "etl_control") or self.etl_control is None:
            self.etl_control = PunchFilesView()
        self.set_central_widget(self.etl_control)

    def clear_log(self):
        print(f"Clear Log")
        pass

    def show_about_dialog(self):
        version = get_git_version()        
   
        text = "029 Puncher<br><br>"
    
        if version:
            text += (
                f"Version:<br>{version}<br>"
                f"<br>"
            )
   
        text += (
            "By:<br>"
            "John Howard<br>"
            "Stan Paddock<br>"
            "Luca Severini<br>"
            "<br>"
            "This program punches card deck files (.CD) and text files (.txt) to the 029 puncher through an Arduino® controlled board."
        )   
        
        image_path = os.path.join(os.path.dirname(__file__), "CHM-logo-2.png")
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About")
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setIconPixmap(scaled_pixmap)
        msg_box.exec_()
            