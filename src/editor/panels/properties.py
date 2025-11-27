from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout,
                               QLineEdit, QTextEdit, QComboBox, QGroupBox,
                               QPushButton, QScrollArea, QFrame, QSpinBox, QHBoxLayout)
from PySide6.QtCore import Qt, QTimer
from src.common.models import NodeModel, ChoiceModel, ProjectModel, ActionModel
from src.common.constants import NodeType, VarOperation, ActionType


class PropertiesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node: NodeModel = None
        self.project_ref: ProjectModel = None

        # STYLE CSS PRO & SOMBRE
        # Note: On utilise [class="..."] pour cibler les propriétés dynamiques Qt
        self.setStyleSheet("""
            QWidget { background-color: #252526; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 13px; }

            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                background-color: #3c3c3c; border: 1px solid #555; border-radius: 4px; padding: 5px; color: #f0f0f0;
            }
            QLineEdit:focus, QTextEdit:focus { border: 1px solid #007acc; background-color: #1e1e1e; }

            QLabel { color: #bbbbbb; font-weight: 500; }

            /* Groupes */
            QGroupBox { 
                border: 1px solid #444; border-radius: 6px; margin-top: 20px; padding-top: 15px; font-weight: bold; color: #007acc; background-color: #2d2d30;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; top: -7px; background-color: #252526; }

            /* Boutons par défaut */
            QPushButton { background-color: #3e3e42; color: white; border: 1px solid #555; padding: 6px 12px; border-radius: 3px; }
            QPushButton:hover { background-color: #505050; border-color: #007acc; }

            /* Boutons Spéciaux (Via propriété dynamique) */
            QPushButton[class="add-btn"] { background-color: #0e639c; border: none; font-weight: bold; margin-top: 5px; }
            QPushButton[class="add-btn"]:hover { background-color: #1177bb; }

            QPushButton[class="del-btn"] { background-color: #802020; border: none; color: #ffcccc; font-weight: bold; }
            QPushButton[class="del-btn"]:hover { background-color: #a03030; }

            QScrollBar:vertical { background: #252526; width: 10px; }
            QScrollBar::handle:vertical { background: #424242; border-radius: 5px; }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.main_layout.addWidget(self.scroll)

        self.container = QWidget()
        self.scroll.setWidget(self.container)

        # Layout principal vertical
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # En-tête (Type de Nœud)
        self.header_label = QLabel("AUCUNE SÉLECTION")
        self.header_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #569cd6; padding: 5px; border-bottom: 2px solid #3e3e42;")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.header_label)

        # Formulaire dynamique
        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)
        self.layout.addWidget(self.form_widget)

    def set_project(self, project: ProjectModel):
        self.project_ref = project

    def load_node(self, node: NodeModel):
        """Reconstruit toute l'interface pour le nœud donné."""
        self.current_node = node
        self._clear_layout(self.form_layout)

        if node is None:
            self.header_label.setText("SÉLECTIONNEZ UN NŒUD")
            return

        self.header_label.setText(f"ÉDITION : {node.type.value.upper()}")

        # --- 1. BLOC IDENTITÉ (Titre) ---
        id_group = QGroupBox("Identité")
        id_layout = QFormLayout(id_group)

        current_title = getattr(self.current_node, 'title', self.current_node.id[:8])
        self.name_edit = QLineEdit(current_title)
        self.name_edit.setPlaceholderText("Nom unique (ex: Village_Entree)")
        self.name_edit.textChanged.connect(self._update_title)

        id_layout.addRow("Titre du Passage:", self.name_edit)
        self.form_layout.addWidget(id_group)

        # Focus automatique ergonomique
        QTimer.singleShot(50, self._focus_name_field)

        # --- 2. CONTENU SPÉCIFIQUE ---
        if node.type == NodeType.SCENE:
            self._build_scene_ui()
        elif node.type == NodeType.SET_VAR:
            self._build_logic_ui()

    def _focus_name_field(self):
        if hasattr(self, 'name_edit') and self.name_edit.isVisible():
            self.name_edit.setFocus()
            self.name_edit.selectAll()

    def _update_title(self, text):
        if self.current_node:
            self.current_node.title = text

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    # =========================================================================
    #  UI SCÈNE (TEXTE, ACTIONS, CHOIX)
    # =========================================================================
    def _build_scene_ui(self):
        # --- A. NARRATION ---
        narr_group = QGroupBox("Narration")
        narr_layout = QFormLayout(narr_group)

        self.text_edit = QTextEdit(self.current_node.content.text)
        self.text_edit.setPlaceholderText("Écrivez l'histoire ici...")
        self.text_edit.setMinimumHeight(100)
        self.text_edit.textChanged.connect(
            lambda: setattr(self.current_node.content, 'text', self.text_edit.toPlainText()))

        self.bg_edit = QLineEdit(self.current_node.content.background_image or "")
        self.bg_edit.setPlaceholderText("assets/images/fond.png")
        self.bg_edit.textChanged.connect(lambda t: setattr(self.current_node.content, 'background_image', t))

        narr_layout.addRow("Texte:", self.text_edit)
        narr_layout.addRow("Image de fond:", self.bg_edit)
        self.form_layout.addWidget(narr_group)

        # --- B. ÉVÉNEMENTS (ACTIONS) ---
        evt_group = QGroupBox("Événements (On Enter)")
        evt_layout = QVBoxLayout(evt_group)

        # Liste des actions existantes
        for i, action in enumerate(self.current_node.content.actions):
            self._add_action_block(evt_layout, i, action)

        # Bouton Ajouter
        add_act_btn = QPushButton("+ Ajouter un Événement")
        add_act_btn.setProperty("class", "add-btn")  # CORRECTION
        add_act_btn.setCursor(Qt.PointingHandCursor)
        add_act_btn.clicked.connect(self._add_action)
        evt_layout.addWidget(add_act_btn)

        self.form_layout.addWidget(evt_group)

        # --- C. NAVIGATION (CHOIX) ---
        choice_group = QGroupBox("Navigation & Choix")
        choice_layout = QVBoxLayout(choice_group)

        # Liste des choix existants
        for i, choice in enumerate(self.current_node.content.choices):
            self._add_choice_block(choice_layout, i, choice)

        # Bouton Ajouter
        add_ch_btn = QPushButton("+ Ajouter un Choix")
        add_ch_btn.setProperty("class", "add-btn")  # CORRECTION
        add_ch_btn.setCursor(Qt.PointingHandCursor)
        add_ch_btn.clicked.connect(self._add_choice)
        choice_layout.addWidget(add_ch_btn)

        self.form_layout.addWidget(choice_group)

    # --- BLOC ACTION INDIVIDUEL ---
    def _add_action_block(self, parent_layout, index, action: ActionModel):
        # Conteneur visuel pour une action
        frame = QFrame()
        frame.setStyleSheet("background-color: #333337; border-radius: 4px; border: 1px solid #454545;")
        layout = QFormLayout(frame)

        # Header avec bouton supprimer
        header_layout = QHBoxLayout()
        lbl = QLabel(f"<b>Action #{index + 1}</b>")
        del_btn = QPushButton("Supprimer")
        del_btn.setProperty("class", "del-btn")  # CORRECTION
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setFixedWidth(80)
        del_btn.clicked.connect(lambda _, i=index: self._delete_action(i))

        header_layout.addWidget(lbl)
        header_layout.addStretch()
        header_layout.addWidget(del_btn)
        layout.addRow(header_layout)

        # Type d'action
        type_combo = QComboBox()
        type_combo.addItems([t.value for t in ActionType])
        type_combo.setCurrentText(action.type.value)
        type_combo.currentTextChanged.connect(lambda t, i=index: self._update_action_type(i, t))
        layout.addRow("Type:", type_combo)

        # Paramètres contextuels
        if action.type in [ActionType.ADD_ITEM, ActionType.REMOVE_ITEM]:
            item_id_edit = QLineEdit(str(action.params.get("item_id", "")))
            item_id_edit.setPlaceholderText("ID de l'objet (ex: sword)")
            item_id_edit.textChanged.connect(lambda t, i=index: self._update_action_param(i, "item_id", t))

            qty_spin = QSpinBox()
            qty_spin.setRange(1, 999)
            qty_spin.setValue(int(action.params.get("qty", 1)))
            qty_spin.valueChanged.connect(lambda v, i=index: self._update_action_param(i, "qty", v))

            layout.addRow("ID Objet:", item_id_edit)
            layout.addRow("Quantité:", qty_spin)

        elif action.type in [ActionType.NPC_SPAWN, ActionType.NPC_STATUS]:
            npc_edit = QLineEdit(str(action.params.get("npc_id", "")))
            npc_edit.setPlaceholderText("ID du PNJ (ex: Cyndra)")
            npc_edit.textChanged.connect(lambda t, i=index: self._update_action_param(i, "npc_id", t))
            layout.addRow("ID PNJ:", npc_edit)

            if action.type == ActionType.NPC_STATUS:
                status_combo = QComboBox()
                status_combo.addItems(["fixed", "follow", "dead"])
                status_combo.setCurrentText(str(action.params.get("status", "fixed")))
                status_combo.currentTextChanged.connect(lambda t, i=index: self._update_action_param(i, "status", t))
                layout.addRow("Statut:", status_combo)

        parent_layout.addWidget(frame)

    # --- BLOC CHOIX INDIVIDUEL ---
    def _add_choice_block(self, parent_layout, index, choice: ChoiceModel):
        frame = QFrame()
        frame.setStyleSheet("background-color: #333337; border-radius: 4px; border: 1px solid #454545;")
        layout = QFormLayout(frame)

        # Header
        header_layout = QHBoxLayout()
        lbl = QLabel(f"<b>Option #{index + 1}</b>")
        del_btn = QPushButton("X")
        del_btn.setProperty("class", "del-btn")  # CORRECTION
        del_btn.setFixedSize(30, 25)
        del_btn.clicked.connect(lambda _, i=index: self._delete_choice(i))

        header_layout.addWidget(lbl)
        header_layout.addStretch()
        header_layout.addWidget(del_btn)
        layout.addRow(header_layout)

        # Texte
        txt_edit = QLineEdit(choice.text)
        txt_edit.setPlaceholderText("Ce que voit le joueur...")
        txt_edit.textChanged.connect(lambda t, i=index: setattr(self.current_node.content.choices[i], 'text', t))
        layout.addRow("Texte:", txt_edit)

        # Cible (Smart Combo)
        target_combo = QComboBox()
        target_combo.addItem("--- (Fin / Rien) ---", None)

        if self.project_ref:
            for nid, node in self.project_ref.nodes.items():
                if nid != self.current_node.id:
                    # Affichage: Titre + (ID court)
                    label = f"{node.title} ({nid[:4]})"
                    target_combo.addItem(label, nid)

        # Sélectionner la valeur actuelle
        idx = target_combo.findData(choice.target_node_id)
        if idx >= 0: target_combo.setCurrentIndex(idx)

        target_combo.currentIndexChanged.connect(
            lambda _, c=target_combo, i=index: setattr(self.current_node.content.choices[i], 'target_node_id',
                                                       c.currentData()))
        layout.addRow("Vers:", target_combo)

        parent_layout.addWidget(frame)

    # --- LOGIQUE DE MISE À JOUR DU MODÈLE ---

    def _add_action(self):
        self.current_node.content.actions.append(ActionModel())
        self.load_node(self.current_node)  # Refresh complet pour afficher

    def _delete_action(self, index):
        if 0 <= index < len(self.current_node.content.actions):
            self.current_node.content.actions.pop(index)
            self.load_node(self.current_node)

    def _update_action_type(self, index, type_str):
        for at in ActionType:
            if at.value == type_str:
                self.current_node.content.actions[index].type = at
                # On recharge pour afficher les bons champs de paramètres
                self.load_node(self.current_node)
                break

    def _update_action_param(self, index, key, value):
        self.current_node.content.actions[index].params[key] = value

    def _add_choice(self):
        self.current_node.content.choices.append(ChoiceModel(text="Nouveau choix"))
        self.load_node(self.current_node)

    def _delete_choice(self, index):
        if 0 <= index < len(self.current_node.content.choices):
            self.current_node.content.choices.pop(index)
            self.load_node(self.current_node)

    # --- UI LOGIQUE (SET VAR) ---
    def _build_logic_ui(self):
        group = QGroupBox("Opération sur Variable")
        layout = QFormLayout(group)

        var_edit = QLineEdit(self.current_node.content.variable_name or "")
        var_edit.setPlaceholderText("Nom variable (ex: gold)")
        var_edit.textChanged.connect(lambda t: setattr(self.current_node.content, 'variable_name', t))
        layout.addRow("Variable:", var_edit)

        op_combo = QComboBox()
        op_combo.addItems([e.value for e in VarOperation])
        if self.current_node.content.operation:
            op_combo.setCurrentText(self.current_node.content.operation)
        op_combo.currentTextChanged.connect(lambda t: setattr(self.current_node.content, 'operation', t))
        layout.addRow("Opération:", op_combo)

        val_edit = QLineEdit(str(self.current_node.content.value))
        val_edit.setPlaceholderText("Valeur (ex: 10)")
        val_edit.textChanged.connect(lambda t: setattr(self.current_node.content, 'value', t))
        layout.addRow("Valeur:", val_edit)

        self.form_layout.addWidget(group)