from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
from src.common.constants import NodeType, VariableType, ActionType


def generate_uuid() -> str:
    return str(uuid4())


# --- Modèles Actions (Événements) ---
class ActionModel(BaseModel):
    """Une action exécutée à l'entrée d'un nœud."""
    type: ActionType = ActionType.ADD_ITEM
    # Paramètres flexibles (ex: {"item_id": "sword", "qty": 1} ou {"npc_id": "Cyndra", "status": "follow"})
    params: Dict[str, Any] = Field(default_factory=dict)


# --- Modèles Contenu ---
class ChoiceModel(BaseModel):
    text: str = "Continuer..."
    condition: str = ""
    target_node_id: Optional[str] = None


class NodeContentModel(BaseModel):
    text: str = ""
    character_id: Optional[str] = None
    background_image: Optional[str] = None
    music: Optional[str] = None

    # Liste des choix (Navigation)
    choices: List[ChoiceModel] = Field(default_factory=list)

    # Liste des actions (Logique PNJ/Inventaire)
    actions: List[ActionModel] = Field(default_factory=list)

    # Legacy
    variable_name: Optional[str] = None
    operation: Optional[str] = None
    value: str = "0"


class NodeModel(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    type: NodeType = NodeType.SCENE
    title: str = "Nouveau Passage"
    position: List[float] = [0.0, 0.0]
    content: NodeContentModel = Field(default_factory=NodeContentModel)
    outputs: List[Any] = Field(default_factory=list)


class VariableDefinition(BaseModel):
    type: VariableType
    default_value: Any


class ProjectMetadata(BaseModel):
    name: str = "Projet RPG"
    author: str = "Auteur"
    version: str = "1.0.0"
    resolution: List[int] = [1280, 720]


class ProjectModel(BaseModel):
    meta: ProjectMetadata = Field(default_factory=ProjectMetadata)
    variables: Dict[str, VariableDefinition] = Field(default_factory=dict)
    nodes: Dict[str, NodeModel] = Field(default_factory=dict)
    assets: Dict[str, str] = Field(default_factory=dict)
    start_node_id: Optional[str] = None