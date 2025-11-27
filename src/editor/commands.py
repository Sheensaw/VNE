from PySide6.QtGui import QUndoCommand
from src.editor.graph.scene import NodeScene
from src.editor.graph.nodes import NodeItem
from src.common.models import NodeModel


class AddNodeCommand(QUndoCommand):
    def __init__(self, scene, node_item: NodeItem):
        super().__init__()
        self.scene = scene
        self.node_item = node_item

        # CORRECTION : On accède à 'node_item.model.type' et non 'node_item.type'
        # node_item.type est une méthode native de QGraphicsItem (conflit de nom)
        # node_item.model.type est votre Enum (NodeType) défini dans Pydantic
        node_type_name = self.node_item.model.type.value
        self.setText(f"Ajouter Noeud {node_type_name}")

    def redo(self):
        self.scene.addItem(self.node_item)

    def undo(self):
        self.scene.removeItem(self.node_item)


class MoveNodeCommand(QUndoCommand):
    def __init__(self, node_item: NodeItem, old_pos, new_pos):
        super().__init__("Déplacer Noeud")
        self.node_item = node_item
        self.old_pos = old_pos
        self.new_pos = new_pos

    def redo(self):
        self.node_item.setPos(self.new_pos)
        # Mise à jour des données du modèle pour la sauvegarde
        self.node_item.model.position = [self.new_pos.x(), self.new_pos.y()]

    def undo(self):
        self.node_item.setPos(self.old_pos)
        # Restauration des données du modèle
        self.node_item.model.position = [self.old_pos.x(), self.old_pos.y()]