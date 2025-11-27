import sys
import os
from pathlib import Path

def get_base_path() -> Path:
    """
    Retourne le chemin racine de l'application.
    Gère la distinction entre l'environnement de développement
    et l'exécutable PyInstaller (dossier temporaire _MEI).
    """
    if getattr(sys, 'frozen', False):
        # Si on est dans un exe PyInstaller
        return Path(sys._MEIPASS)
    else:
        # Si on est en développement (basé sur l'emplacement de ce fichier)
        # Ce fichier est dans src/common/, donc la racine est deux niveaux au-dessus
        return Path(__file__).parent.parent.parent

def get_assets_path() -> Path:
    """Retourne le chemin vers le dossier assets."""
    return get_base_path() / "assets"

def get_project_path(project_file_path: str) -> Path:
    """Retourne le dossier contenant le fichier projet."""
    return Path(project_file_path).parent