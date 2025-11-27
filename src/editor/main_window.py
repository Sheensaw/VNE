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

        self.scene = NodeScene(self)
        self.view = NodeGraphView(self.scene)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.open_context_menu)

        self.setCentralWidget(self.view)

        self._create_docks()
        self._create_actions()

        self.scene.selectionChanged.connect(self.on_selection_changed)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.scene.update)
        self.refresh_timer.start(200)

    def _create_docks(self):
        self.prop_dock = QDockWidget("Propriétés", self)
        self.prop_panel = PropertiesPanel()
        self.prop_panel.set_project(self.project)
        self.prop_dock.setWidget(self.prop_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.prop_dock)

        self.asset_dock = QDockWidget("Assets", self)
        self.asset_panel = AssetBrowser()
        self.asset_dock.setWidget(self.asset_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.asset_dock)

    def _create_actions(self):
        toolbar = QToolBar("Outils")
        self.addToolBar(toolbar)

        act_save = QAction("Sauvegarder", self)
        act_save.triggered.connect(self.save_project)
        toolbar.addAction(act_save)

        toolbar.addSeparator()

        act_undo = self.undo_stack.createUndoAction(self, "Annuler")
        act_redo = self.undo_stack.createRedoAction(self, "Rétablir")
        toolbar.addAction(act_undo)
        toolbar.addAction(act_redo)

        toolbar.addSeparator()

        act_add_scene = QAction("+ Scène", self)
        act_add_scene.triggered.connect(lambda: self.add_node(NodeType.SCENE))
        toolbar.addAction(act_add_scene)

        act_add_logic = QAction("+ Variable", self)
        act_add_logic.triggered.connect(lambda: self.add_node(NodeType.SET_VAR))
        toolbar.addAction(act_add_logic)

        toolbar.addSeparator()

        btn_run = QPushButton("▶ JOUER")
        btn_run.setCursor(Qt.PointingHandCursor)
        btn_run.setStyleSheet(
            "background-color: #2d5a37; color: white; font-weight: bold; padding: 5px 15px; border-radius: 3px;")
        btn_run.clicked.connect(self.run_test)
        toolbar.addWidget(btn_run)

    def open_context_menu(self, position):
        menu = QMenu()
        action_scene = menu.addAction("Créer Scène ici")
        action_logic = menu.addAction("Créer Variable ici")
        action = menu.exec(self.view.mapToGlobal(position))
        scene_pos = self.view.mapToScene(position)
        coords = [scene_pos.x(), scene_pos.y()]
        if action == action_scene:
            self.add_node(NodeType.SCENE, pos=coords)
        elif action == action_logic:
            self.add_node(NodeType.SET_VAR, pos=coords)

    def add_node(self, type: NodeType, pos=None):
        if pos is None:
            center = self.view.mapToScene(self.view.viewport().rect().center())
            pos = [center.x(), center.y()]

        model = NodeModel(type=type)
        model.position = pos
        count = len([n for n in self.project.nodes.values() if n.type == type])
        if type == NodeType.SCENE:
            model.title = f"Passage {count + 1}"
        elif type == NodeType.SET_VAR:
            model.title = f"Var {count + 1}"
        if not self.project.nodes: self.project.start_node_id = model.id

        self.project.nodes[model.id] = model
        item = NodeItem(model)
        cmd = AddNodeCommand(self.scene, item)
        self.undo_stack.push(cmd)
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
                for item in self.scene.items():
                    if isinstance(item, NodeItem):
                        item.model.position = [item.x(), item.y()]
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.project.model_dump_json(indent=2))
                self.statusBar().showMessage(f"Sauvegardé: {path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def run_test(self):
        temp_path = get_base_path() / "temp_debug.json"
        try:
            # Sauvegarde auto temporaire
            for item in self.scene.items():
                if isinstance(item, NodeItem):
                    item.model.position = [item.x(), item.y()]
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(self.project.model_dump_json(indent=2))

            main_player = get_base_path() / "main_player.py"
            cmd = [sys.executable, str(main_player), "--project", str(temp_path)]

            # OPTION CRITIQUE : Ouvre une nouvelle console sur Windows pour voir les erreurs
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NEW_CONSOLE

            print(f"🚀 Lancement: {cmd}")
            subprocess.Popen(cmd, cwd=get_base_path(), creationflags=creationflags)

        except Exception as e:
            print(f"❌ Erreur Lancement: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de lancer le jeu :\n{e}")