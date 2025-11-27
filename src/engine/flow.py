from typing import Optional
from src.common.models import ProjectModel, NodeModel, ActionModel
from src.common.constants import NodeType, VarOperation, ActionType
from src.engine.state import SessionState
from src.engine.scripting import ScriptEngine  # CORRECTION : Import sans .py


class FlowManager:
    """
    Cerveau de la navigation et exécution des actions.
    """

    def __init__(self, project: ProjectModel, state: SessionState):
        self.project = project
        self.state = state
        self.script_engine = ScriptEngine()

    def get_node(self, node_id: str) -> Optional[NodeModel]:
        return self.project.nodes.get(node_id)

    def advance(self, choice_index: int = -1) -> Optional[NodeModel]:
        current_node = self.get_node(self.state.current_node_id)
        if not current_node:
            return None

        next_node_id = None

        if current_node.type == NodeType.SCENE:
            if choice_index >= 0 and choice_index < len(current_node.content.choices):
                choice = current_node.content.choices[choice_index]
                # TODO: Vérifier condition choix ici
                next_node_id = choice.target_node_id
            elif not current_node.content.choices and current_node.outputs:
                next_node_id = current_node.outputs[0].target_node_id

        elif current_node.type == NodeType.SET_VAR:
            self._execute_logic(current_node)
            if current_node.outputs:
                next_node_id = current_node.outputs[0].target_node_id

        if next_node_id:
            self.state.current_node_id = next_node_id
            self.state.push_history(next_node_id)

            next_node = self.get_node(next_node_id)

            # --- EXÉCUTION DES ACTIONS DU NOUVEAU NŒUD ---
            if next_node and next_node.type == NodeType.SCENE:
                for action in next_node.content.actions:
                    self._execute_action(action)

            if next_node and next_node.type == NodeType.SET_VAR:
                return self.advance()

            return next_node

        return None

    def _execute_action(self, action: ActionModel):
        """Exécute une action définie dans l'éditeur."""
        p = action.params
        if action.type == ActionType.ADD_ITEM:
            item_id = p.get("item_id")
            qty = int(p.get("qty", 1))
            if item_id:
                self.state.add_item(item_id, qty)

        elif action.type == ActionType.REMOVE_ITEM:
            item_id = p.get("item_id")
            qty = int(p.get("qty", 1))
            if item_id:
                self.state.remove_item(item_id, qty)

        elif action.type == ActionType.NPC_SPAWN:
            npc_id = p.get("npc_id")
            if npc_id:
                self.state.update_npc(npc_id, {"spawned": True, "location": self.state.current_node_id})

        elif action.type == ActionType.NPC_STATUS:
            npc_id = p.get("npc_id")
            status = p.get("status", "fixed")  # follow / fixed
            if npc_id:
                self.state.update_npc(npc_id, {"status": status})

        # Ajouter d'autres types d'actions ici (Move, Say, etc.)

    def _execute_logic(self, node: NodeModel):
        var_name = node.content.variable_name
        op = node.content.operation
        val_expr = node.content.value

        if not var_name or not op:
            return

        current_val = self.state.get_variable(var_name)
        target_val = self.script_engine.evaluate_expression(val_expr, self.state.variables)

        if isinstance(current_val, int):
            try:
                target_val = int(target_val)
            except:
                pass

        new_val = current_val
        if op == VarOperation.SET:
            new_val = target_val
        elif op == VarOperation.ADD:
            new_val = current_val + target_val
        elif op == VarOperation.SUB:
            new_val = current_val - target_val

        self.state.set_variable(var_name, new_val)