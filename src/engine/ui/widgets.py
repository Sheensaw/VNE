from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve


class TypewriterLabel(QLabel):
    """
    Label qui affiche le texte caractère par caractère (effet machine à écrire).
    """
    finished = Signal()  # Émis quand le texte est totalement affiché

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setStyleSheet("color: white; font-size: 18px; padding: 10px;")

        self.full_text = ""
        self.current_char_index = 0
        self.timer = QTimer()
        self.timer.setInterval(30)  # Vitesse: 30ms par lettre
        self.timer.timeout.connect(self._add_char)

    def show_text(self, text: str):
        self.full_text = text
        self.current_char_index = 0
        self.setText("")
        self.timer.start()

    def _add_char(self):
        if self.current_char_index < len(self.full_text):
            self.setText(self.full_text[:self.current_char_index + 1])
            self.current_char_index += 1
        else:
            self.complete()

    def complete(self):
        """Force l'affichage complet immédiat (si le joueur clique)."""
        self.timer.stop()
        self.setText(self.full_text)
        self.finished.emit()

    def is_animating(self) -> bool:
        return self.timer.isActive()


class ChoiceButton(QPushButton):
    """
    Bouton stylisé pour les choix narratifs.
    """

    def __init__(self, text: str, index: int, parent=None):
        super().__init__(text, parent)
        self.index = index  # Stocke l'index du choix pour le moteur
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                border: 1px solid #555;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 150, 0.8);
                border-color: #88F;
            }
        """)


class SceneView(QLabel):
    """
    Widget de fond qui gère l'image d'arrière-plan.
    Utilise QLabel avec scaledContents pour s'adapter à la fenêtre.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScaledContents(True)
        self.setStyleSheet("background-color: #222;")  # Couleur par défaut si pas d'image