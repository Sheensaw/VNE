from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFrame,
                               QLabel, QScrollArea, QPushButton, QHBoxLayout, QListWidget)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QKeyEvent
from src.engine.core import GameEngine
from src.engine.ui.widgets import TypewriterLabel, ChoiceButton, SceneView
from src.common.models import NodeModel
from src.common.constants import NodeType
from src.common.paths import get_assets_path
import os


class GameWindow(QMainWindow):
    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Velkarum Engine")
        self.resize(1280, 800)

        self.setStyleSheet("""
            QMainWindow { background-color: #121216; }
            QFrame#mainContainer { background-color: rgba(18, 18, 22, 0.95); border: 1px solid #3a3a3a; border-radius: 10px; }
            QLabel { color: #f0f0f0; font-family: 'Segoe UI', sans-serif; }
            QPushButton#invBtn { background-color: #444; color: white; border: 1px solid #666; padding: 5px 10px; }
            QListWidget { background-color: #222; color: white; border: 1px solid #555; }
        """)

        self.engine.nodeChanged.connect(self.on_node_changed)
        self.engine.gameEnded.connect(self.close)
        self._setup_ui()

    def _setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Fond
        self.scene_view = SceneView(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.scene_view)

        # Wrapper principal
        wrapper_layout = QVBoxLayout()
        wrapper_layout.setContentsMargins(20, 20, 20, 20)

        # --- BARRE SUPÉRIEURE (HUD) ---
        hud_layout = QHBoxLayout()
        self.loc_label = QLabel("LIEU INCONNU")
        self.loc_label.setStyleSheet("color: #b1a270; font-weight: bold; font-size: 16px;")

        self.inv_btn = QPushButton("Inventaire")
        self.inv_btn.setObjectName("invBtn")
        self.inv_btn.setCheckable(True)
        self.inv_btn.clicked.connect(self.toggle_inventory)

        hud_layout.addWidget(self.loc_label)
        hud_layout.addStretch()
        hud_layout.addWidget(self.inv_btn)
        wrapper_layout.addLayout(hud_layout)

        # --- ZONE DE JEU ---
        game_area = QHBoxLayout()

        # Texte (Gauche/Centre)
        self.text_container = QFrame()
        self.text_container.setObjectName("mainContainer")
        self.text_container.setSizePolicy(self.text_container.sizePolicy().Horizontal,
                                          self.text_container.sizePolicy().Expanding)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(20)

        # Texte narratif
        self.text_label = TypewriterLabel()
        self.text_label.setStyleSheet("font-size: 18px; line-height: 1.6; color: #e0e0e0;")
        self.scroll_layout.addWidget(self.text_label)
        self.scroll_layout.addStretch()

        # Choix (Bas du texte)
        self.choices_layout = QVBoxLayout()
        self.scroll_layout.addLayout(self.choices_layout)

        self.scroll_area.setWidget(self.scroll_content)

        cont_layout = QVBoxLayout(self.text_container)
        cont_layout.addWidget(self.scroll_area)

        game_area.addWidget(self.text_container, 2)  # Ratio 2

        # --- INVENTAIRE (Droite, Masqué par défaut) ---
        self.inv_panel = QFrame()
        self.inv_panel.setObjectName("mainContainer")
        self.inv_panel.hide()
        inv_layout = QVBoxLayout(self.inv_panel)
        inv_layout.addWidget(QLabel("SAC À DOS"))
        self.inv_list = QListWidget()
        inv_layout.addWidget(self.inv_list)

        game_area.addWidget(self.inv_panel, 1)  # Ratio 1

        wrapper_layout.addLayout(game_area)
        self.scene_view.setLayout(wrapper_layout)
        self.scene_view.mousePressEvent = self.on_scene_click

    def toggle_inventory(self):
        if self.inv_btn.isChecked():
            self.inv_panel.show()
            self.refresh_inventory()
        else:
            self.inv_panel.hide()

    def refresh_inventory(self):
        self.inv_list.clear()
        for item_id, qty in self.engine.state.inventory.items():
            self.inv_list.addItem(f"{item_id} (x{qty})")

    @Slot(object)
    def on_node_changed(self, node: NodeModel):
        if node.content.background_image:
            bg_path = get_assets_path() / node.content.background_image
            if os.path.exists(bg_path):
                self.scene_view.setPixmap(QPixmap(str(bg_path)))

        if node.type == NodeType.SCENE:
            self.loc_label.setText(node.title.upper())
            self.text_label.show_text(node.content.text)
            self._build_choices(node)

            # Rafraîchir inventaire si ouvert (car des items ont pu être ajoutés)
            if self.inv_panel.isVisible():
                self.refresh_inventory()

    def _build_choices(self, node: NodeModel):
        while self.choices_layout.count():
            item = self.choices_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if node.content.choices:
            for i, choice in enumerate(node.content.choices):
                btn = ChoiceButton(choice.text, i)
                btn.setStyleSheet("""
                    QPushButton { background-color: rgba(255, 255, 255, 0.05); border: 1px solid #555; color: #b1a270; padding: 12px; text-align: left; }
                    QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); border-color: #b1a270; color: white; }
                """)
                btn.clicked.connect(lambda checked=False, idx=i: self.engine.select_choice(idx))
                self.choices_layout.addWidget(btn)
        elif node.outputs:
            lbl = QLabel("▼")
            lbl.setAlignment(Qt.AlignCenter)
            self.choices_layout.addWidget(lbl)

    def on_scene_click(self, event):
        if self.text_label.is_animating():
            self.text_label.complete()
        else:
            current = self.engine.flow.get_node(self.engine.state.current_node_id)
            if current and not current.content.choices:
                self.engine.next_dialogue()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Space, Qt.Key_Return):
            self.on_scene_click(None)