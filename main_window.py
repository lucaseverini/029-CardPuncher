#!/usr/bin/env python3

# 029 Puncher
# main_window.py (8-23-2025)
# By Luca Severini (lucaseverini@mac.com)

import os
import sys
import subprocess
import traceback
from git import get_git_version
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication, QDialog
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit, QLabel
from PyQt5.QtWidgets import QComboBox, QMessageBox
from PyQt5.QtWidgets import QWidget, QInputDialog, QFileDialog
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap
from main_view import MainView
from git import git_check_update
from git_dialog import UpdateDialog

kLogDir = "LOGS"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.menu = self.menuBar()
        self.current_widget = None
                
        # File menu
        self.info_menu = self.menu.addMenu("File")
        about_action = QAction("About 029 Puncher…", self)
        about_action.triggered.connect(self.show_about_dialog)
        self.info_menu.addAction(about_action)

        # Actions menu
        self.actions_menu = self.menu.addMenu("Actions")
        self.action_punch_cd_files = QAction("Punch File…", self)
        self.action_punch_cd_files.triggered.connect(self.select_punch_file)
        self.actions_menu.addAction(self.action_punch_cd_files)

        # Utility menu
        self.utils_menu = self.menu.addMenu("Utility")
        self.action_clear_logs = QAction("Delete Log Files…", self)
        self.action_clear_logs.triggered.connect(self.clear_logs)
        self.utils_menu.addAction(self.action_clear_logs)
        self.action_open_logs = QAction("Open Log folder", self)
        self.action_open_logs.triggered.connect(self.open_log_folder)
        self.utils_menu.addAction(self.action_open_logs)
        self.action_delete_log = QAction("Delete Log Text", self)
        self.action_delete_log.triggered.connect(self.delete_log)
        self.utils_menu.addAction(self.action_delete_log)
        self.utils_menu.addSeparator()
        self.action_update_check = QAction("Update Check…", self)
        self.action_update_check.triggered.connect(self.update_check)
        self.utils_menu.addAction(self.action_update_check)
                 
        self.show_punch_files()
        # self.show_about_dialog()
            
        self.resize(600, 400)
        self.center_on_screen()
        
    def set_window_title(self):
        version = get_git_version()
        version_str = f" - Version {version}" if version else ""
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
        if not hasattr(self, "main_view") or self.main_view is None:
            self.main_view = MainView()
        self.set_central_widget(self.main_view)

    def select_punch_file(self):
        self.show_punch_files()
        self.main_view.select_file()
        
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
            "This program punches card deck files (.cd) and text files (.txt) with the IBM 029 Card Punch through the connection with relays in an Arduino® controlled board."
        )   
        
        image_path = os.path.join(os.path.dirname(__file__), "Images/CHM-logo-2.png")
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About")
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setIconPixmap(scaled_pixmap)
        msg_box.exec_()
        
    def delete_log(self):
        self.main_view.arduino_messages.clear()

    def update_check(self):
        result = git_check_update(do_update = False)
        commits = result["commits"]
        if commits:
            print(len(commits), "commit(s) behind")
            dlg = UpdateDialog(f"Commits available: {len(commits)}", commits)
            if dlg.exec_() == QDialog.Accepted:
                print("Updating...")
                result = git_check_update(do_update = True)
                if result["updated"]:
                    print("Program updated. Restarting...")
                    os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print("Update cancelled")
        else:
            print("No commits to apply")
            QMessageBox.information(
                self,
                "Update Check",
                "Program 029 Puncher is up to date.",
                QMessageBox.Ok
            )
            
    def open_log_folder(self):
        log_dir = os.path.abspath(kLogDir)
        if not os.path.isdir(log_dir):
            QMessageBox.information(self, "Logs", f"No {kLogDir} folder found at:\n{log_dir}")
            return

        if sys.platform.startswith("darwin"):        # macOS
            subprocess.run(["open", log_dir])
        elif sys.platform.startswith("win"):         # Windows
            os.startfile(log_dir)  # built-in
        else:
            QMessageBox.warning(self, "Logs", f"Unsupported platform: {sys.platform}")
         
    def clear_logs(self):
        log_files = []
        log_dir = os.path.abspath(kLogDir)
        if os.path.isdir(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
        if len(log_files) == 0:
            QMessageBox.information(self, "Information", "No log file to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm delete",
            f"Delete all log files in {log_dir} folder ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return 0

        count = 0
        for name in os.listdir(log_dir):
            if name.endswith(".log"):
                try:
                    os.remove(os.path.join(log_dir, name))
                    count += 1
                except Exception as e:
                    print(f"Could not remove log file {name}: {e}")

        QMessageBox.information(self, "Logs", f"Removed {count} log files.")
        return
