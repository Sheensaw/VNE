from enum import Enum

class NodeType(str, Enum):
    """Types de noeuds disponibles dans le graphe."""
    START = "START"         # Point d'entrée
    SCENE = "SCENE"         # Un passage narratif (Texte + Choix)
    SET_VAR = "SET_VAR"     # Logique invisible (Variables)

class VariableType(str, Enum):
    BOOL = "bool"
    INT = "int"
    STR = "str"

class VarOperation(str, Enum):
    SET = "="
    ADD = "+"
    SUB = "-"