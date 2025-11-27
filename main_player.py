from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QLabel, QScrollArea
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QKeyEvent
from src.engine.core import GameEngine
from src.engine.ui.widgets import TypewriterLabel, ChoiceButton, SceneView
from src.common.models import NodeModel
from src.common.constants import NodeType
from src.common.paths import get_assets_path
import os


class GameWindow(QMainWindow):
    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Visual Novel Player")
        self.resize(1280, 720)

        # Connexions
        self.engine.nodeChanged.connect(self.on_node_changed)
        self.engine.gameEnded.connect(self.close)

        self._setup_ui()

    def _setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Fond (SceneView)
        self.scene_view = SceneView(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.scene_view)

        # Conteneur Textuel (Centré)
        self.text_container = QFrame()
        self.text_container.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 20, 0.9);
                border-radius: 12px;
                padding: 25px;
                border: 1px solid #444;
            }
        """)
        self.text_container.setFixedWidth(800)  # Largeur fixe pour la lisibilité

        self.container_layout = QVBoxLayout(self.text_container)
        self.container_layout.setSpacing(20)

        # 1. Nom (Optionnel)
        self.char_label = QLabel()
        self.char_label.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 18px;")
        self.char_label.hide()
        self.container_layout.addWidget(self.char_label)

        # 2. Texte Récit
        self.text_label = TypewriterLabel()
        self.text_label.setStyleSheet(
            "color: #EEE; font-size: 20px; line-height: 1.6; font-family: 'Segoe UI', sans-serif;")
        self.container_layout.addWidget(self.text_label)

        # 3. Liste des Choix
        self.choices_layout = QVBoxLayout()
        self.choices_layout.setSpacing(10)
        self.container_layout.addLayout(self.choices_layout)

        # Mise en page globale
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(self.text_container, 0, Qt.AlignCenter)
        wrapper_layout.addStretch()

        self.scene_view.setLayout(wrapper_layout)

        # Clic pour avancer
        self.scene_view.mousePressEvent = self.on_scene_click

    @Slot(object)
    def on_node_changed(self, node: NodeModel):
        # 1. Background
        if node.content.background_image:
            bg_path = get_assets_path() / node.content.background_image
            if os.path.exists(bg_path):
                self.scene_view.setPixmap(QPixmap(str(bg_path)))

        # 2. Affichage Scène
        if node.type == NodeType.SCENE:
            # Personnage (si défini)
            if node.content.character_id:
                self.char_label.setText(node.content.character_id)
                self.char_label.show()
            else:
                self.char_label.hide()

            # Texte
            self.text_label.show_text(node.content.text)

            # Génération des boutons
            self._build_choices(node)

    def _build_choices(self, node: NodeModel):
        # Nettoyage
        while self.choices_layout.count():
            item = self.choices_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Création
        if node.content.choices:
            for i, choice in enumerate(node.content.choices):
                # On pourrait ajouter ici une vérification de condition (choice.condition)
                btn = ChoiceButton(choice.text, i)
                btn.clicked.connect(lambda checked=False, idx=i: self.engine.select_choice(idx))
                self.choices_layout.addWidget(btn)

        # Si aucun choix bouton mais une sortie par défaut -> "Continuer" implicite
        elif node.outputs:
            lbl = QLabel("▼")
            lbl.setStyleSheet("color: #777; font-size: 24px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.choices_layout.addWidget(lbl)

    def on_scene_click(self, event):
        # Si le texte est en train de s'écrire, on l'affiche tout de suite
        if self.text_label.is_animating():
            self.text_label.complete()
            return

        # Si pas de choix interactifs, le clic sert à avancer
        current_node = self.engine.flow.get_node(self.engine.state.current_node_id)
        if current_node and not current_node.content.choices:
            self.engine.next_dialogue()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Space, Qt.Key_Return):
            self.on_scene_click(None)