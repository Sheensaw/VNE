from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout,
                               QLineEdit, QTextEdit, QComboBox, QGroupBox,
                               QPushButton, QScrollArea)
from PySide6.QtCore import Qt, QTimer
from src.common.models import NodeModel, ChoiceModel, ProjectModel
from src.common.constants import NodeType, VarOperation


class PropertiesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node: NodeModel = None
        self.project_ref: ProjectModel = None

        # --- STYLE GLOBAL DU PANNEAU ---
        self.setStyleSheet("""
            QWidget { 
                background-color: #2b2b2b; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #383838;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #5c4b8b;
                background-color: #404040;
            }
            QLabel { color: #aaaaaa; }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #4a4a4a;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover { background-color: #555; }
        """)

        # Layout Principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area pour gérer les petits écrans ou nombreux choix
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.main_layout.addWidget(self.scroll)

        # Widget Conteneur dans le Scroll
        self.container = QWidget()
        self.scroll.setWidget(self.container)

        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(15)  # Espacement aéré

        # Header (Type de noeud)
        self.header_label = QLabel("Aucune sélection")
        self.header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #5c4b8b; padding: 10px;")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.header_label)

        # Formulaire
        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self.layout.addWidget(self.form_widget)

    def set_project(self, project: ProjectModel):
        self.project_ref = project

    def load_node(self, node: NodeModel):
        self.current_node = node
        self._clear_layout(self.form_layout)

        if node is None:
            self.header_label.setText("Aucune sélection")
            return

        self.header_label.setText(f"{node.type.value.upper()}")

        # --- CHAMP NOM (FOCUS AUTOMATIQUE) ---
        lbl_name = QLabel("Nom:")
        lbl_name.setStyleSheet("color: white; font-weight: bold;")
        self.form_layout.addRow(lbl_name)

        current_title = getattr(self.current_node, 'title', self.current_node.id[:8])
        self.name_edit = QLineEdit(current_title)
        self.name_edit.textChanged.connect(self._update_title)
        self.form_layout.addRow(self.name_edit)

        # FOCUS LOGIC : On met le focus sur le nom pour éditer tout de suite
        # On utilise QTimer pour laisser le temps au widget de s'afficher
        QTimer.singleShot(50, self._focus_name_field)

        # Séparateur visuel
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #444;")
        self.form_layout.addRow(line)

        if node.type == NodeType.SCENE:
            self._build_scene_form()
        elif node.type == NodeType.SET_VAR:
            self._build_logic_form()

    def _focus_name_field(self):
        """Place le curseur dans le champ nom et sélectionne tout."""
        if hasattr(self, 'name_edit'):
            self.name_edit.setFocus()
            self.name_edit.selectAll()

    def _update_title(self, text):
        if self.current_node:
            self.current_node.title = text

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    # --- Formulaire SCENE ---
    def _build_scene_form(self):
        # Texte
        lbl_txt = QLabel("Récit:")
        self.text_edit = QTextEdit(self.current_node.content.text)
        self.text_edit.setPlaceholderText("Il était une fois...")
        self.text_edit.setFixedHeight(100)
        self.text_edit.textChanged.connect(
            lambda: setattr(self.current_node.content, 'text', self.text_edit.toPlainText())
        )
        self.form_layout.addRow(lbl_txt, self.text_edit)

        # Image
        self.bg_edit = QLineEdit(self.current_node.content.background_image or "")
        self.bg_edit.setPlaceholderText("assets/bg.png")
        self.bg_edit.textChanged.connect(
            lambda t: setattr(self.current_node.content, 'background_image', t)
        )
        self.form_layout.addRow("Image:", self.bg_edit)

        # Choix Header
        lbl_choices = QLabel("CHOIX")
        lbl_choices.setStyleSheet("font-weight: bold; color: #BBB; margin-top: 10px;")
        self.form_layout.addRow(lbl_choices)

        add_btn = QPushButton("+ Ajouter Option")
        add_btn.setStyleSheet("background-color: #2d5a37; color: white; font-weight: bold;")
        add_btn.clicked.connect(self._add_choice)
        self.form_layout.addRow(add_btn)

        for i, choice in enumerate(self.current_node.content.choices):
            self._add_choice_ui(i, choice)

    def _add_choice_ui(self, index, choice: ChoiceModel):
        group = QGroupBox(f"Option #{index + 1}")
        g_layout = QFormLayout()

        # Texte Bouton
        txt_edit = QLineEdit(choice.text)
        txt_edit.setPlaceholderText("Texte du bouton...")
        txt_edit.textChanged.connect(
            lambda t, idx=index: self._update_choice(idx, "text", t)
        )
        g_layout.addRow("Titre:", txt_edit)

        # Cible (ComboBox)
        target_combo = QComboBox()
        target_combo.addItem("--- (Fin) ---", None)

        current_idx = 0
        if self.project_ref:
            combo_idx = 1
            for nid, node in self.project_ref.nodes.items():
                # On évite de se lier à soi-même pour la clarté (optionnel)
                if nid == self.current_node.id: continue

                title = getattr(node, 'title', nid[:8])
                display = f"{title} ({nid[:4]})"
                target_combo.addItem(display, nid)

                if choice.target_node_id == nid:
                    current_idx = combo_idx
                combo_idx += 1

        target_combo.setCurrentIndex(current_idx)
        target_combo.currentIndexChanged.connect(
            lambda idx, c=target_combo, i=index: self._on_target_selected(i, c)
        )
        g_layout.addRow("Vers:", target_combo)

        group.setLayout(g_layout)
        self.form_layout.addRow(group)

    def _on_target_selected(self, choice_index, combo):
        target_id = combo.currentData()
        if 0 <= choice_index < len(self.current_node.content.choices):
            self.current_node.content.choices[choice_index].target_node_id = target_id

    def _add_choice(self):
        new_choice = ChoiceModel(text="Continuer")
        self.current_node.content.choices.append(new_choice)
        self.load_node(self.current_node)  # Refresh

    def _update_choice(self, index, field, value):
        if 0 <= index < len(self.current_node.content.choices):
            setattr(self.current_node.content.choices[index], field, value)

    def _build_logic_form(self):
        var_edit = QLineEdit(self.current_node.content.variable_name or "")
        var_edit.setPlaceholderText("ex: score_confiance")
        var_edit.textChanged.connect(lambda t: setattr(self.current_node.content, 'variable_name', t))
        self.form_layout.addRow("Variable:", var_edit)

        op_combo = QComboBox()
        op_combo.addItems([e.value for e in VarOperation])
        if self.current_node.content.operation:
            op_combo.setCurrentText(self.current_node.content.operation)
        op_combo.currentTextChanged.connect(lambda t: setattr(self.current_node.content, 'operation', t))
        self.form_layout.addRow("Opération:", op_combo)

        val_edit = QLineEdit(str(self.current_node.content.value))
        val_edit.setPlaceholderText("Valeur ou Formule")
        val_edit.textChanged.connect(lambda t: setattr(self.current_node.content, 'value', t))
        self.form_layout.addRow("Valeur:", val_edit)