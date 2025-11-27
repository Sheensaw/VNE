from PySide6.QtWidgets import QTreeView, QFileSystemModel, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QDir
from src.common.paths import get_assets_path


class AssetBrowser(QWidget):
    """
    Explorateur de fichiers pour le dossier 'assets'.
    Permet le Drag & Drop vers le graphe ou les propriétés.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Titre
        label = QLabel("Navigateur d'Assets")
        label.setStyleSheet("padding: 5px; font-weight: bold; background: #333; color: #DDD;")
        self.layout.addWidget(label)

        # Modèle de fichiers
        self.model = QFileSystemModel()
        root_path = get_assets_path()
        self.model.setRootPath(str(root_path))

        # Vue Arborescente
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(str(root_path)))

        # Masquer les colonnes inutiles (Taille, Type, Date)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.setHeaderHidden(True)

        # Activer le Drag & Drop
        self.tree.setDragEnabled(True)
        self.tree.setDragDropMode(QTreeView.DragOnly)

        self.layout.addWidget(self.tree)