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
    QHBoxLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt
from git import git_check_update

class UpdateDialog(QDialog):
    def __init__(self, message: str, commits = None):
        super().__init__()
        self.setWindowTitle("029 Puncher - Update Check")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        self.resize(800, 360)

        layout = QVBoxLayout(self)

        # Message text
        label = QLabel(message)
        layout.addWidget(label)

        # Table with 4 columns: Date, Author, Subject, File
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Date", "Author", "Subject", "File"])
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setWordWrap(True)
        self.table.setTextElideMode(Qt.ElideNone)  
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        if commits:
            self.table.setRowCount(len(commits))
            for i, commit in enumerate(commits):
                # Commit date
                self.table.setItem(i, 0, QTableWidgetItem(commit["date"]))
                
                # Commit author
                self.table.setItem(i, 1, QTableWidgetItem(commit["author"]))
                
                # Commit messages
                self.table.setItem(i, 2, QTableWidgetItem(commit["subject"]))
                
                # Commit files
                files_lines = []
                for f in commit.get("files", []):
                    if "old_path" in f:
                        files_lines.append(f'{f.get("status", "")} : {f.get("old_path", "")} \u2192 {f.get("path", "")}')
                    else:
                        files_lines.append(f'{f.get("status", "")} : {f.get("path", "")}')
                self.table.setItem(i, 3, QTableWidgetItem("\n".join(files_lines)))

            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.resizeRowsToContents()

        # Buttons
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Update")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.update_button.clicked.connect(self.confirm_update)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    # Confrimation dialog
    def confirm_update(self):
        box = QMessageBox(self)
        box.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        box.setWindowTitle("Confirm to Update")
        box.setText("Are you sure you want to update?")

        cancel_btn = box.addButton(QMessageBox.Cancel)
        update_btn = box.addButton("Update", QMessageBox.AcceptRole)
        
        box.setDefaultButton(update_btn)
        box.exec_()

        if box.clickedButton() == update_btn:
            self.accept()
        else:
            self.reject()
            
if __name__ == "__main__":
    app = QApplication(sys.argv)

    result = git_check_update(do_update = False)
    commits = result["commits"]
    # print(commits)
    
    if commits:
        print(len(commits), "commit(s) behind")
        dlg = UpdateDialog(f"Commits available: {len(commits)}", commits)
        if dlg.exec_() == QDialog.Accepted:
            print("Updating...")
            result = git_check_update(do_update = True)
            if result["updated"]:
                print("Program updated. Restarting...")
                # os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("Update cancelled")
    else:
       print("No commits") 

    sys.exit(0)
