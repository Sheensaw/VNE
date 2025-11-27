import sys
import json
import subprocess
import os
from PySide6.QtWidgets import (QMainWindow, QDockWidget, QToolBar, QFileDialog,
                               QMessageBox, QApplication, QPushButton, QMenu)
from PySide6.QtGui import QAction, QUndoStack
from PySide6.QtCore import Qt, QTimer

from src.editor.graph.scene import NodeScene
from src.editor.graph.view import NodeGraphView
from src.editor.graph.nodes import NodeItem
from src.editor.panels.properties import PropertiesPanel
from src.editor.panels.assets import AssetBrowser
from src.editor.commands import AddNodeCommand
from src.common.models import ProjectModel, NodeModel
from src.common.constants import NodeType
from src.common.paths import get_base_path


class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Velkarum Editor")
        self.resize(1600, 900)

        self.project = ProjectModel()
        self.undo_stack = QUndoStack(self)

        # 1. Scène & Vue Graphique
        self.scene = NodeScene(self)
        self.view = NodeGraphView(self.scene)

        # Menu Contextuel (Clic Droit sur le fond)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.open_context_menu)

        self.setCentralWidget(self.view)

        # 2. Docks & Actions
        self._create_docks()
        self._create_actions()

        # Connexion Sélection -> Propriétés
        self.scene.selectionChanged.connect(self.on_selection_changed)

        # 3. Rafraîchissement Visuel (Pour mettre à jour les titres sur les nœuds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.scene.update)
        self.refresh_timer.start(200)  # 5 FPS pour l'UI update

    def _create_docks(self):
        # Droite : Propriétés
        self.prop_dock = QDockWidget("Propriétés", self)
        self.prop_panel = PropertiesPanel()
        self.prop_panel.set_project(self.project)  # Lien vital pour les listes déroulantes
        self.prop_dock.setWidget(self.prop_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.prop_dock)

        # Gauche : Assets
        self.asset_dock = QDockWidget("Assets", self)
        self.asset_panel = AssetBrowser()
        self.asset_dock.setWidget(self.asset_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.asset_dock)

    def _create_actions(self):
        toolbar = QToolBar("Outils")
        self.addToolBar(toolbar)

        # Sauvegarde
        act_save = QAction("Sauvegarder", self)
        act_save.triggered.connect(self.save_project)
        toolbar.addAction(act_save)

        toolbar.addSeparator()

        # Undo/Redo
        act_undo = self.undo_stack.createUndoAction(self, "Annuler")
        act_redo = self.undo_stack.createRedoAction(self, "Rétablir")
        toolbar.addAction(act_undo)
        toolbar.addAction(act_redo)

        toolbar.addSeparator()

        # Création Nœuds
        act_add_scene = QAction("+ Scène", self)
        act_add_scene.setStatusTip("Ajouter un nouveau passage narratif")
        act_add_scene.triggered.connect(lambda: self.add_node(NodeType.SCENE))
        toolbar.addAction(act_add_scene)

        act_add_logic = QAction("+ Variable", self)
        act_add_logic.setStatusTip("Ajouter un bloc de logique")
        act_add_logic.triggered.connect(lambda: self.add_node(NodeType.SET_VAR))
        toolbar.addAction(act_add_logic)

        toolbar.addSeparator()

        # Bouton PLAY vert
        btn_run = QPushButton("▶ JOUER")
        btn_run.setCursor(Qt.PointingHandCursor)
        btn_run.setStyleSheet("""
            background-color: #2d5a37; 
            color: white; 
            font-weight: bold; 
            padding: 5px 15px; 
            border-radius: 3px;
        """)
        btn_run.clicked.connect(self.run_test)
        toolbar.addWidget(btn_run)

    def open_context_menu(self, position):
        """Affiche le menu clic droit sur le graphe."""
        menu = QMenu()
        action_scene = menu.addAction("Créer Scène ici")
        action_logic = menu.addAction("Créer Variable ici")

        action = menu.exec(self.view.mapToGlobal(position))

        # Conversion coord écran -> coord scène
        scene_pos = self.view.mapToScene(position)
        coords = [scene_pos.x(), scene_pos.y()]

        if action == action_scene:
            self.add_node(NodeType.SCENE, pos=coords)
        elif action == action_logic:
            self.add_node(NodeType.SET_VAR, pos=coords)

    def add_node(self, type: NodeType, pos=None):
        if pos is None:
            # Au centre de la vue
            center = self.view.mapToScene(self.view.viewport().rect().center())
            pos = [center.x(), center.y()]

        model = NodeModel(type=type)
        model.position = pos

        # Nommage auto intelligent
        count = len([n for n in self.project.nodes.values() if n.type == type])
        if type == NodeType.SCENE:
            model.title = f"Passage {count + 1}"
        elif type == NodeType.SET_VAR:
            model.title = f"Var {count + 1}"

        # Si c'est le premier, c'est le Start
        if not self.project.nodes:
            self.project.start_node_id = model.id

        self.project.nodes[model.id] = model
        item = NodeItem(model)

        cmd = AddNodeCommand(self.scene, item)
        self.undo_stack.push(cmd)

        # SÉLECTION AUTOMATIQUE (Active le panneau propriétés)
        self.scene.clearSelection()
        item.setSelected(True)

    def on_selection_changed(self):
        items = self.scene.selectedItems()
        if items and isinstance(items[0], NodeItem):
            self.prop_panel.load_node(items[0].model)
        else:
            self.prop_panel.load_node(None)

    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder", "games/demo/story.json", "JSON (*.json)")
        if path:
            try:
                # Sync positions
                for item in self.scene.items():
                    if isinstance(item, NodeItem):
                        item.model.position = [item.x(), item.y()]

                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.project.model_dump_json(indent=2))
                self.statusBar().showMessage(f"Sauvegardé: {path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def run_test(self):
        """Lance le jeu et affiche les erreurs console s'il y en a."""
        temp_path = get_base_path() / "temp_debug.json"

        try:
            # 1. Sauvegarder l'état actuel
            for item in self.scene.items():
                if isinstance(item, NodeItem):
                    item.model.position = [item.x(), item.y()]

            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(self.project.model_dump_json(indent=2))

            # 2. Préparer la commande
            main_player = get_base_path() / "main_player.py"
            python_exe = sys.executable  # Utilise le même python que l'éditeur

            cmd = [python_exe, str(main_player), "--project", str(temp_path)]

            print(f"🚀 Lancement du jeu : {' '.join(cmd)}")

            # 3. Lancement sans bloquer l'éditeur
            # En cas de crash immédiat, Popen peut ne rien dire.
            # On peut rediriger stderr si besoin, mais ici on lance juste.
            subprocess.Popen(cmd, cwd=get_base_path())

            self.statusBar().showMessage("Jeu lancé...", 3000)

        except Exception as e:
            print(f"❌ Erreur de lancement : {e}")
            QMessageBox.critical(self, "Erreur Lancement", f"Impossible de lancer le jeu :\n{e}")