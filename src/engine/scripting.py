from simpleeval import SimpleEval
from typing import Dict, Any
import random
import math


class ScriptEngine:
    """
    Moteur d'évaluation pour les conditions et les scripts légers.
    Permet d'exécuter la logique du jeu (Stats, Inventaire) sans `eval()` dangereux.
    """

    def __init__(self):
        self.functions = {
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "random": random.random,
            "randint": random.randint,
            "ceil": math.ceil,
            "floor": math.floor,
            "int": int,
            "str": str,
            "len": len
        }
        self.evaluator = SimpleEval(functions=self.functions)

    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Évalue une condition (ex: 'health > 0 and hasKey == True')."""
        if not condition or not condition.strip():
            return True

        self.evaluator.names = context
        try:
            return bool(self.evaluator.eval(condition))
        except Exception as e:
            print(f"[Script] Erreur condition '{condition}': {e}")
            return False

    def evaluate_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """Évalue une expression (ex: 'gold + 10')."""
        if not expression: return None

        self.evaluator.names = context
        try:
            return self.evaluator.eval(str(expression))
        except Exception as e:
            print(f"[Script] Erreur expression '{expression}': {e}")
            return 0

    def execute_script(self, script: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute un script simple ligne par ligne (pseudo-code).
        Supporte: var = val, var += val, var -= val
        """
        if not script: return context

        lines = script.split(';')
        for line in lines:
            line = line.strip()
            if not line: continue

            try:
                # Parsing très basique pour l'exemple (à étendre pour un vrai langage)
                if "+=" in line:
                    k, v = line.split("+=")
                    val = self.evaluate_expression(v.strip(), context)
                    context[k.strip()] = context.get(k.strip(), 0) + val
                elif "-=" in line:
                    k, v = line.split("-=")
                    val = self.evaluate_expression(v.strip(), context)
                    context[k.strip()] = context.get(k.strip(), 0) - val
                elif "=" in line:
                    k, v = line.split("=")
                    val = self.evaluate_expression(v.strip(), context)
                    context[k.strip()] = val
            except Exception as e:
                print(f"[Script] Erreur exécution ligne '{line}': {e}")

        return context