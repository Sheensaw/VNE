import json
from PySide6.QtCore import QObject, Signal
from src.common.models import ProjectModel, NodeModel
from src.engine.state import SessionState
from src.engine.flow import FlowManager
from src.engine.audio import AudioManager


class GameEngine(QObject):
    """
    Contrôleur principal du jeu.
    Fait le lien entre les données (ProjectModel), la logique (Flow) et l'UI.
    Émet des signaux Qt quand l'état change pour que l'UI se mette à jour.
    """
    # Signaux pour l'UI
    nodeChanged = Signal(object)  # Émet le nouveau NodeModel
    gameEnded = Signal()  # Fin du jeu

    def __init__(self):
        super().__init__()
        self.project: ProjectModel = None
        self.state = SessionState()
        self.flow: FlowManager = None
        self.audio = AudioManager()

    def load_project(self, json_path: str):
        """Charge le fichier story.json et initialise le moteur."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Validation Pydantic automatique
                self.project = ProjectModel(**data)

            self.state.initialize_from_project(self.project)
            self.flow = FlowManager(self.project, self.state)
            print(f"[Engine] Projet '{self.project.meta.name}' chargé.")

        except Exception as e:
            print(f"[Engine] Erreur fatale au chargement: {e}")
            raise e

    def start_game(self):
        """Lance le jeu au noeud de départ."""
        if not self.project.start_node_id:
            print("[Engine] Aucun start_node_id défini !")
            return

        start_node = self.flow.get_node(self.project.start_node_id)
        self._process_node(start_node)

    def select_choice(self, index: int):
        """Appelé par l'UI quand le joueur clique sur un choix."""
        next_node = self.flow.advance(index)
        self._process_node(next_node)

    def next_dialogue(self):
        """Appelé par l'UI pour avancer après un dialogue simple."""
        next_node = self.flow.advance()
        self._process_node(next_node)

    def _process_node(self, node: NodeModel):
        """Traite le noeud courant : audio, mise à jour état, signal UI."""
        if not node:
            print("[Engine] Fin du flux.")
            self.gameEnded.emit()
            return

        # 1. Mise à jour de l'état (History) - déjà fait dans flow.advance mais on confirme
        self.state.current_node_id = node.id

        # 2. Gestion Audio (si le noeud demande de changer la musique/jouer un son)
        if node.content.audio_clip:
            # Simplification: ici on considère que audio_clip est un SFX
            # Pour une BGM, il faudrait un champ séparé ou une convention de nommage
            self.audio.play_sfx(node.content.audio_clip)

        # 3. Notification à l'UI
        self.nodeChanged.emit(node)