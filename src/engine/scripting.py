from simpleeval import SimpleEval
from typing import Dict, Any
import random


class ScriptEngine:
    """
    Moteur d'évaluation sécurisé pour les conditions.
    """

    def __init__(self):
        functions = {
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "random": random.random,
            "randint": random.randint
        }
        self.evaluator = SimpleEval(functions=functions)

    def evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        if not condition or not condition.strip():
            return True

        self.evaluator.names = variables
        try:
            return bool(self.evaluator.eval(condition))
        except Exception as e:
            print(f"Erreur condition '{condition}': {e}")
            return False

    def evaluate_expression(self, expression: str, variables: Dict[str, Any]) -> Any:
        self.evaluator.names = variables
        try:
            return self.evaluator.eval(expression)
        except Exception as e:
            print(f"Erreur expression '{expression}': {e}")
            return 0