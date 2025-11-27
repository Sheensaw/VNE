from typing import Dict, Any, List
from src.common.models import ProjectModel, VariableDefinition


class SessionState:
    """
    Gère l'état courant d'une partie (Session).
    Stocke les variables et l'historique de navigation.
    """

    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.history: List[str] = []  # Stack des IDs de noeuds visités
        self.current_node_id: str = None

    def initialize_from_project(self, project: ProjectModel):
        """Initialise les variables avec les valeurs par défaut du projet."""
        self.variables = {}
        for name, var_def in project.variables.items():
            self.variables[name] = var_def.default_value

        self.history = []
        self.current_node_id = project.start_node_id

    def set_variable(self, name: str, value: Any):
        if name in self.variables:
            self.variables[name] = value
        else:
            print(f"Attention: Tentative d'écriture sur variable inconnue '{name}'")

    def get_variable(self, name: str) -> Any:
        return self.variables.get(name, 0)

    def push_history(self, node_id: str):
        self.history.append(node_id)

    def pop_history(self) -> str:
        if self.history:
            return self.history.pop()
        return None