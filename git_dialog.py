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
from git import git_check_update

class UpdateDialog(QDialog):
    def __init__(self, message: str, commits = None):
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
        self.table.verticalHeader().setVisible(False)      
        layout.addWidget(self.table)

        if commits:
            self.table.setRowCount(len(commits))
            for i, commit in enumerate(commits):
                self.table.setItem(i, 0, QTableWidgetItem(commit["date"]))
                self.table.setItem(i, 1, QTableWidgetItem(commit["author"]))
                self.table.setItem(i, 2, QTableWidgetItem(commit["subject"]))

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

    result = git_check_update(do_update = False)
    commits = result["commits"]
    # print(commits)
    
    if commits:
        dlg = UpdateDialog("Commits available:", commits)
        if dlg.exec_() == QDialog.Accepted:
            print("Updating...")
            result = git_check_update(do_update = True)
            if result["updated"]:
                print("Program updated. Restarting...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("Update cancelled")
    else:
       print("No commits.") 

    sys.exit(0)
