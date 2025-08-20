#!/usr/bin/env python3

# 029 Puncher (Jul-17-2025)
# By Luca Severini

# main.py

from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from main_window import MainWindow
import os
import sys
import signal
import traceback, logging
from PyQt5.QtWidgets import QMessageBox
from pathlib import Path

# PRINT_ATTRIBUTES
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

def handle_interrupt():
    print(f"{BOLD}\nProgram interrupted.{RESET}")
    # QApplication.quit()
    sys.exit(1)

def main():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    app = QApplication(sys.argv)
    app.setApplicationName("029 Puncher")
    signal.signal(signal.SIGINT, lambda sig, frame: handle_interrupt())

    # Show splash screen
    image_path = os.path.join(os.path.dirname(__file__), "CHM-logo.png")
    pixmap = QPixmap(image_path)
    splash = QSplashScreen(pixmap)
    splash.show()

    def show_main_window():
        try:
            app.window = MainWindow()
            app.window.show()
            splash.finish(app.window)
        except Exception as e:
            print(f"{RED}Error showing main window: {e}{RESET}")
            err = traceback.format_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Startup Error", err)
            QApplication.quit()
        
    QTimer.singleShot(4000, show_main_window)
    app.processEvents()
   
    # Dummy timer to keep the Qt event loop alive and processing events
    app.window = None
    app.timer = QTimer()
    app.timer.timeout.connect(lambda: None)
    app.timer.start(100)

    status = app.exec_()
    print(f"{BOLD}Program quit.{RESET}")
    sys.exit(status)

if __name__ == "__main__":
    main()
