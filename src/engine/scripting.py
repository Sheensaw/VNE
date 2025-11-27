from simpleeval import SimpleEval
from typing import Dict, Any
import random
import math

class ScriptEngine:
    def __init__(self):
        self.functions = {
            "min": min, "max": max, "abs": abs, "round": round,
            "random": random.random, "randint": random.randint,
            "int": int, "str": str, "len": len
        }
        self.evaluator = SimpleEval(functions=self.functions)

    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        if not condition or not condition.strip(): return True
        self.evaluator.names = context
        try:
            return bool(self.evaluator.eval(condition))
        except Exception as e:
            print(f"[Script] Erreur condition '{condition}': {e}")
            return False

    def evaluate_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        if not expression: return 0
        self.evaluator.names = context
        try:
            return self.evaluator.eval(str(expression))
        except Exception as e:
            print(f"[Script] Erreur expression '{expression}': {e}")
            return 0