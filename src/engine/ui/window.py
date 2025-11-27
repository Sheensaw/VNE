from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QKeyEvent
from src.engine.core import GameEngine
from src.engine.ui.widgets import TypewriterLabel, ChoiceButton, SceneView
from src.common.models import NodeModel
from src.common.constants import NodeType
from src.common.paths import get_assets_path
import os


class GameWindow(QMainWindow):
    """
    Fenêtre principale du joueur.
    Connecte les widgets visuels aux signaux du GameEngine.
    """

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Visual Novel Player")
        self.resize(1280, 720)

        # Connexions Moteur -> UI
        self.engine.nodeChanged.connect(self.on_node_changed)
        self.engine.gameEnded.connect(self.close)

        self._setup_ui()

    def _setup_ui(self):
        """Construction de l'interface en couches."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal (Stacking)
        # On utilise un QVBoxLayout mais on va gérer le background différemment
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Zone Scène (Background + Personnages)
        # Pour faire simple, la SceneView prend toute la place en arrière-plan
        # et on met l'UI par dessus. Mais ici, on va utiliser un layout vertical simple
        # avec le background qui s'étend et la boite de dialogue en bas.

        # Conteneur principal avec image de fond
        self.scene_view = SceneView()
        self.scene_view.setLayout(QVBoxLayout())  # Permet de mettre des widgets DANS le label
        self.main_layout.addWidget(self.scene_view)

        # Layout interne de la scène (pour centrer les choix et mettre le texte en bas)
        self.scene_layout = QVBoxLayout()
        self.scene_layout.addStretch()  # Pousse tout vers le bas

        # 2. Zone de Choix (Apparaît au milieu/bas)
        self.choice_container = QWidget()
        self.choice_layout = QVBoxLayout(self.choice_container)
        self.choice_layout.setSpacing(10)
        self.scene_layout.addWidget(self.choice_container)

        # 3. Boite de Dialogue (En bas)
        self.dialogue_box = QFrame()
        self.dialogue_box.setStyleSheet("background-color: rgba(0, 0, 0, 0.8); border-top: 2px solid #555;")
        self.dialogue_box.setFixedHeight(200)

        dialogue_layout = QVBoxLayout(self.dialogue_box)

        # Nom du personnage
        self.name_label = QLabel("???")
        self.name_label.setStyleSheet("font-weight: bold; color: #AAA; font-size: 14px;")
        dialogue_layout.addWidget(self.name_label)

        # Texte machine à écrire
        self.text_label = TypewriterLabel()
        dialogue_layout.addWidget(self.text_label)

        self.scene_layout.addWidget(self.dialogue_box)
        self.scene_view.layout().addLayout(self.scene_layout)

        # Clic pour avancer
        self.scene_view.mousePressEvent = self.on_scene_click

    @Slot(object)
    def on_node_changed(self, node: NodeModel):
        """Mise à jour de l'UI quand le noeud change."""
        # 1. Background
        if node.content.background_image:
            bg_path = get_assets_path() / node.content.background_image
            if os.path.exists(bg_path):
                self.scene_view.setPixmap(QPixmap(str(bg_path)))

        # 2. Gestion Dialogue vs Choix
        if node.type == NodeType.DIALOGUE:
            self.choice_container.hide()
            self.dialogue_box.show()

            # Mise à jour nom/texte
            char_name = node.content.character_id if node.content.character_id else ""
            self.name_label.setText(char_name)
            self.text_label.show_text(node.content.text)

        elif node.type == NodeType.CHOICE:
            # On garde souvent le texte du dernier dialogue affiché,
            # ou on affiche le texte de la question si le noeud Choice en a.
            # Ici, on affiche les boutons.
            self._clear_choices()

            for i, choice_data in enumerate(node.content.choices):
                # On vérifie la condition ici ou on laisse le moteur filtrer?
                # Le moteur filtre souvent avant, mais ici on le fait à l'affichage si on veut griser.
                # Pour l'instant, on affiche tout ce que le modèle contient.
                btn = ChoiceButton(choice_data.get("text", "Choix..."), i)
                btn.clicked.connect(lambda checked=False, idx=i: self.engine.select_choice(idx))
                self.choice_layout.addWidget(btn)

            self.choice_container.show()
            # On peut cacher la boite de dialogue ou l'utiliser pour poser la question
            if node.content.text:
                self.dialogue_box.show()
                self.text_label.show_text(node.content.text)
            else:
                self.dialogue_box.hide()

    def _clear_choices(self):
        while self.choice_layout.count():
            item = self.choice_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def on_scene_click(self, event):
        """Gestion du clic pour avancer le texte ou le dialogue."""
        current_node = self.engine.flow.get_node(self.engine.state.current_node_id)

        if not current_node:
            return

        if current_node.type == NodeType.DIALOGUE:
            if self.text_label.is_animating():
                self.text_label.complete()
            else:
                self.engine.next_dialogue()

    def keyPressEvent(self, event: QKeyEvent):
        """Permet d'avancer avec Espace ou Entrée."""
        if event.key() in (Qt.Key_Space, Qt.Key_Return):
            self.on_scene_click(None)