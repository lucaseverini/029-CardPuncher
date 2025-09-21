#!/usr/bin/env python3

# 029 Puncher
# main.py (9-20-2025)
# By Luca Severini (lucaseverini@mac.com)

import os
import sys
import signal
import traceback
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QTimer
from main_window import MainWindow


kSplashTimeout = 3000 # millisecs

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

# ------------------------------------------------------------------------------
def handle_interrupt():
    print(f"{BOLD}\nProgram interrupted.{RESET}")
    # QApplication.quit()
    sys.exit(1)

# ------------------------------------------------------------------------------
def show_splash_screen_2(app):
    img1_path = os.path.join(os.path.dirname(__file__), "Images/CHM-logo.png")
    img2_path = os.path.join(os.path.dirname(__file__), "Images/IBM029.png")

    p1 = QPixmap(img1_path)
    p2 = QPixmap(img2_path)

    target_w = max(p1.width(), p2.width())
    p1 = p1.scaledToWidth(target_w, Qt.SmoothTransformation)
    p2 = p2.scaledToWidth(target_w, Qt.SmoothTransformation)

    images_spacing = 0
    combo = QPixmap(target_w, p1.height() + images_spacing + p2.height())
    combo.fill(Qt.transparent)

    p = QPainter(combo)
    p.drawPixmap(0, 0, p1)
    p.drawPixmap(0, p1.height() + images_spacing, p2)
    p.end()

    splash = QSplashScreen(combo)
    splash.show()
    splash.raise_()
    splash.activateWindow()

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
        
    QTimer.singleShot(kSplashTimeout, show_main_window)
    app.processEvents()
    
# ------------------------------------------------------------------------------
def show_splash_screen(app):
    image_path = os.path.join(os.path.dirname(__file__), "Images/CHM-logo.png")
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
        
    QTimer.singleShot(kSplashTimeout, show_main_window)
    app.processEvents()

# ------------------------------------------------------------------------------
def main():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    app = QApplication(sys.argv)
    app.setApplicationName("029 Puncher")
    
    signal.signal(signal.SIGINT, lambda sig, frame: handle_interrupt())

    show_splash_screen_2(app)
   
    # Dummy timer to keep the Qt event loop alive and processing events
    app.window = None
    app.timer = QTimer()
    app.timer.timeout.connect(lambda: None)
    app.timer.start(100)

    status = app.exec_()
    print(f"{BOLD}Program quit.{RESET}")
    sys.exit(status)

if __name__ == "__main__":
    try:
        main()
                
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\nProgram Interrupted.")
        sys.exit(1)
            