from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
from src.common.constants import NodeType, VariableType

def generate_uuid() -> str:
    return str(uuid4())

class ConnectionModel(BaseModel):
    target_node_id: str

class ChoiceModel(BaseModel):
    text: str = "Continuer..."
    condition: str = ""
    target_node_id: Optional[str] = None

class NodeContentModel(BaseModel):
    # Contenu Scène
    text: str = ""
    character_id: Optional[str] = None
    background_image: Optional[str] = None
    music: Optional[str] = None
    choices: List[ChoiceModel] = Field(default_factory=list)

    # Contenu Logique
    variable_name: Optional[str] = None
    operation: Optional[str] = None
    value: str = "0"

class NodeModel(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    type: NodeType = NodeType.SCENE
    # CHAMP AJOUTÉ : Titre visible dans l'éditeur
    title: str = "Nouvelle Scène"
    position: List[float] = [0.0, 0.0]
    content: NodeContentModel = Field(default_factory=NodeContentModel)
    outputs: List[ConnectionModel] = Field(default_factory=list)

class VariableDefinition(BaseModel):
    type: VariableType
    default_value: Any

class ProjectMetadata(BaseModel):
    name: str = "Nouveau Projet"
    author: str = "Auteur"
    version: str = "1.0.0"
    resolution: List[int] = [1280, 720]

class ProjectModel(BaseModel):
    meta: ProjectMetadata = Field(default_factory=ProjectMetadata)
    variables: Dict[str, VariableDefinition] = Field(default_factory=dict)
    nodes: Dict[str, NodeModel] = Field(default_factory=dict)
    assets: Dict[str, str] = Field(default_factory=dict)
    start_node_id: Optional[str] = None