import sys
from PySide6.QtWidgets import QApplication
from src.editor.main_window import EditorWindow
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


def main():
    """
    Point d'entrée de l'Éditeur de Visual Novel.
    Initialise l'application Qt et lance la fenêtre principale.
    """
    # Initialisation de l'application
    app = QApplication(sys.argv)
    app.setApplicationName("Visual Novel Editor")

    # Style Fusion pour un look moderne et sombre
    app.setStyle("Fusion")

    # Palette sombre manuelle (Dark Mode)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    # Lancement de la fenêtre de l'éditeur
    window = EditorWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()