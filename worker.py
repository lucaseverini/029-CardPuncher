#!/usr/bin/env python3

# 029 Puncher
# worker.py (8-23-2025)
# By Luca Severini (lucaseverini@mac.com)

import traceback
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

class PunchWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(object)
    result = pyqtSignal(object)
    message = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        try:
            res = self.func(*self.args, **self.kwargs)
            self.result.emit(res)
            
        except Exception:
            self.error.emit(traceback.format_exc())
            
        finally:
            self.finished.emit()
