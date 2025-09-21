import os
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout
)
from PyQt5.QtCore import Qt


class UpdateDialog(QDialog):
    def __init__(self, message: str, commits=None):
        super().__init__()
        self.setWindowTitle("Git Repository")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        self.resize(600, 350)

        layout = QVBoxLayout(self)

        # Message text
        label = QLabel(message)
        layout.addWidget(label)

        # Table with 3 columns: Date, Author, Subject
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Date", "Author", "Subject"])
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.ElideNone)        
        layout.addWidget(self.table)

        if commits:
            self.table.setRowCount(len(commits))
            for i, commit in enumerate(commits):
                date, author, subject = commit
                self.table.setItem(i, 0, QTableWidgetItem(date))
                self.table.setItem(i, 1, QTableWidgetItem(author))
                self.table.setItem(i, 2, QTableWidgetItem(subject))

            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.resizeRowsToContents()

        # Buttons
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Update")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.update_button.clicked.connect(self.accept)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Example commit list: (date, author, subject)
    commits = [
        ("2025-09-19 14:22:00", "Alice", "Fix bug in parsing"),
        ("2025-09-18 09:15:32", "Bob", "Add feature X"),
        ("2025-09-17 20:45:10", "Luca Severini", "Update documentation\nUpdate documentation\nUpdate documentation\nUpdate documentation"),
        ("2025-09-17 20:50:10", "Luca Severini", "Update documentation Update documentation Update documentation Update documentation"),
    ]

    dlg = UpdateDialog("Commits available:", commits)
    if dlg.exec_() == QDialog.Accepted:
        print("User chose Update")
    else:
        print("User cancelled")

    sys.exit(0)
