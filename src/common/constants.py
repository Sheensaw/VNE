from enum import Enum

class NodeType(str, Enum):
    START = "START"
    SCENE = "SCENE"
    SET_VAR = "SET_VAR"

class VariableType(str, Enum):
    BOOL = "bool"
    INT = "int"
    STR = "str"

class VarOperation(str, Enum):
    SET = "="
    ADD = "+"
    SUB = "-"

# NOUVEAU : Types d'actions pour remplacer les macros Twine
class ActionType(str, Enum):
    ADD_ITEM = "Ajouter Objet"
    REMOVE_ITEM = "Retirer Objet"
    NPC_SPAWN = "Spawn PNJ"
    NPC_MOVE = "Déplacer PNJ"
    NPC_STATUS = "Statut PNJ (Suivre/Attendre)"
    PLAY_SOUND = "Jouer Son"