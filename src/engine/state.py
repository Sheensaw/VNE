from typing import Dict, Any, List
from src.common.models import ProjectModel


class SessionState:
    """
    Gère l'état courant d'une partie (Session).
    Stocke les variables, l'historique, l'inventaire et les PNJ.
    """

    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.history: List[str] = []
        self.current_node_id: str = None

        # NOUVEAU : Systèmes RPG
        self.inventory: Dict[str, int] = {}  # item_id -> quantité
        self.npcs: Dict[str, Dict[str, Any]] = {}  # npc_id -> {status, location, inventory...}

    def initialize_from_project(self, project: ProjectModel):
        self.variables = {}
        for name, var_def in project.variables.items():
            self.variables[name] = var_def.default_value

        self.history = []
        self.current_node_id = project.start_node_id
        self.inventory = {}
        self.npcs = {}

    def set_variable(self, name: str, value: Any):
        self.variables[name] = value

    def get_variable(self, name: str) -> Any:
        return self.variables.get(name, 0)

    def push_history(self, node_id: str):
        self.history.append(node_id)

    # --- Gestion Inventaire ---
    def add_item(self, item_id: str, qty: int = 1):
        current = self.inventory.get(item_id, 0)
        self.inventory[item_id] = current + qty
        print(f"[Inventaire] Ajout: {item_id} x{qty} (Total: {self.inventory[item_id]})")

    def remove_item(self, item_id: str, qty: int = 1):
        if item_id in self.inventory:
            self.inventory[item_id] = max(0, self.inventory[item_id] - qty)
            if self.inventory[item_id] == 0:
                del self.inventory[item_id]

    # --- Gestion PNJ ---
    def update_npc(self, npc_id: str, data: Dict[str, Any]):
        if npc_id not in self.npcs:
            self.npcs[npc_id] = {"status": "fixed", "location": "unknown"}
        self.npcs[npc_id].update(data)
        print(f"[PNJ] Mise à jour {npc_id}: {data}")