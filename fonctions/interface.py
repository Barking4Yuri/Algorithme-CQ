import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

class WelcomeWindow(QWidget):
    def __init__(self, username, role):
        super().__init__()

        self.setWindowTitle("Accueil")
        self.showMaximized()

        layout = QVBoxLayout()

        title = QLabel(f"Bienvenue {username} ({role}) !")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title.setStyleSheet("""
            font-size: 40px;
            font-weight: bold;
            color: white;
        """)

        layout.addWidget(title)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #20232a;
            }
        """)