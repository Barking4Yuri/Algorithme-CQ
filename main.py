
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

from fonctions import compte
from fonctions.compte import utilisateurs


from fonctions import haveibeenpwned


from fonctions import interface


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setFixedSize(350, 460)
        self.mode = "login"

        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(35, 30, 35, 30)

        self.title = QLabel("Bienvenue!")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: white;
        """)

        self.subtitle = QLabel("Connectez vous pour continuer")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setStyleSheet("color: #aaaaaa;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Pseudonyme")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.action_btn = QPushButton("Connexion")
        self.action_btn.clicked.connect(self.submit)

        self.switch_label = QLabel(
            '<a href="#">Pas de compte? Enregistrez vous!</a>'
        )
        self.switch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.switch_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        self.switch_label.setStyleSheet("""
            QLabel {
                color: #528bff;
                font-size: 12px;
            }
        """)

        self.switch_label.linkActivated.connect(self.switch_mode)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.subtitle)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.username)
        self.layout.addWidget(self.email)
        self.layout.addWidget(self.password)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.action_btn)
        self.layout.addWidget(self.switch_label)

        self.setLayout(self.layout)

        self.email.hide()

        self.setStyleSheet("""
            QWidget {
                background-color: #20232a;
                color: white;
                font-size: 14px;
            }

            QLineEdit {
                background-color: #2c303a;
                border: 1px solid #454b57;
                border-radius: 8px;
                padding: 12px;
                color: white;
            }

            QLineEdit:focus {
                border: 1px solid #528bff;
            }

            QPushButton {
                background-color: #3978f6;
                border: none;
                border-radius: 8px;
                padding: 12px;
                color: white;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #2865dc;
            }

            QLabel a {
                color: #528bff;
                text-decoration: none;
            }
        """)

    def switch_mode(self):
        if self.mode == "login":
            self.mode = "register"

            self.title.setText("Create Account")
            self.subtitle.setText("Register to get started")
            self.email.show()
            self.action_btn.setText("Register")

            self.switch_label.setText(
                '<a href="#">Already have an account? Login</a>'
            )

        else:
            self.mode = "login"

            self.title.setText("Welcome Back")
            self.subtitle.setText("Please login to continue")
            self.email.hide()
            self.action_btn.setText("Login")

            self.switch_label.setText(
                '<a href="#">Don\'t have an account? Register</a>'
            )

    def submit(self):
        username = self.username.text()
        password = self.password.text()

        if username == "" or password == "":
            QMessageBox.warning(
                self, "Error", "Remplissez tous les champs."
            )
            return

        if self.mode == "login":
            if compte.check_login(username, password):
                user = compte.get_utilisateur(username)
                if user is None:
                    QMessageBox.warning(
                        self, "Erreur", "Utilisateur introuvable."
                    )
                    return
                role = user['role']
                self.welcome_window = interface.WelcomeWindow(username, role)
                self.welcome_window.showMaximized()
                self.close()

            else:
                QMessageBox.warning(
                    self,
                    "Login Failed",
                    "Pseudonyme ou mot de passe invalide."
                )
        else:
            email = self.email.text()

            if email == "":
                QMessageBox.warning(
                    self, "Error", "Veuillez mettre une adresse email."
                )
                return

            else:
                if username or email in utilisateurs:
                    QMessageBox.warning(
                        self, "Error", "Votre email ou votre pseudo est déjà utilisé"
                    )
                if haveibeenpwned.check_hibp(password):
                    suggestion = haveibeenpwned.suggestions(password)

                    msg = QMessageBox(self)
                    msg.setWindowTitle("Mot de passe compromis")
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText(
                        "Ce mot de passe a été trouvé dans une fuite de données."
                    )
                    msg.setInformativeText(
                        "Choisissez un autre mot de passe en suivant ces suggestions :\n\n"
                        + "\n".join(f"• {s}" for s in suggestion)
                    )
                    msg.setMinimumWidth(500)
                    msg.exec()

                    return

                if compte.creation_compte(email, username, password):
                    QMessageBox.information(
                    self, "Success", "Connexion réussie!"
                    )

                else:
                    QMessageBox.warning(
                        self, "Erreur de la connexion.",
                        "Error"
                    )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())
