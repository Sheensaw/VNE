from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QBrush, QColor, QPen, QPainter, QFont, QFontMetrics, QLinearGradient
from PySide6.QtCore import Qt, QRectF
from src.common.constants import NodeType
from src.common.models import NodeModel


class NodeItem(QGraphicsItem):
    def __init__(self, model: NodeModel):
        super().__init__()
        self.model = model
        self.width = 240  # Plus large pour la lisibilité
        self.height = 160  # Plus haut pour le contenu

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.setPos(self.model.position[0], self.model.position[1])

        # Couleurs inspirées du thème Dark/Twine
        if self.model.type == NodeType.SCENE:
            self.header_color = QColor("#2c3e50")  # Bleu nuit
            self.body_color = QColor("#1e1e1e")  # Gris très sombre
            self.border_color = QColor("#34495e")
        elif self.model.type == NodeType.SET_VAR:
            self.header_color = QColor("#27ae60")  # Vert
            self.body_color = QColor("#1e1e1e")
            self.border_color = QColor("#2ecc71")
        else:
            self.header_color = QColor("#444")
            self.body_color = QColor("#111")
            self.border_color = QColor("#7f8c8d")

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        rect = self.boundingRect()

        # 1. Ombre portée (Performance correcte)
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect.translated(4, 4), 8, 8)

        # 2. Corps du nœud
        painter.setBrush(QBrush(self.body_color))

        # Bordure de sélection (Or) ou Normale
        if self.isSelected():
            painter.setPen(QPen(QColor("#f1c40f"), 2))  # Jaune Or
        else:
            painter.setPen(QPen(self.border_color, 1))

        painter.drawRoundedRect(rect, 8, 8)

        # 3. En-tête (Gradient)
        header_rect = QRectF(0, 0, self.width, 32)
        grad = QLinearGradient(0, 0, 0, 32)
        grad.setColorAt(0, self.header_color.lighter(120))
        grad.setColorAt(1, self.header_color)
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(header_rect, 8, 8)
        # Couvrir le bas de l'arrondi pour faire une barre droite
        painter.drawRect(0, 24, self.width, 8)

        # 4. Titre (Nom de la Scène)
        painter.setPen(QColor("#ecf0f1"))  # Blanc cassé
        font_title = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(font_title)

        display_title = getattr(self.model, 'title', self.model.id[:8])
        if self.model.type == NodeType.START:
            display_title = f"★ {display_title}"

        painter.drawText(header_rect, Qt.AlignCenter, display_title)

        # 5. Contenu (Aperçu Texte + Choix)
        content_rect = QRectF(12, 40, self.width - 24, self.height - 50)
        font_content = QFont("Consolas", 9)
        painter.setFont(font_content)

        if self.model.type == NodeType.SCENE:
            # Aperçu du texte narratif (Gris clair)
            painter.setPen(QColor("#bdc3c7"))
            preview_text = self.model.content.text[:40].replace('\n', ' ')
            if len(self.model.content.text) > 40: preview_text += "..."
            painter.drawText(content_rect.x(), content_rect.y() + 12, preview_text)

            # Ligne de séparation
            painter.setPen(QPen(QColor("#333"), 1))
            painter.drawLine(10, 65, self.width - 10, 65)

            # Liste des Choix (Liens)
            painter.setPen(QColor("#3498db"))  # Bleu lien
            y_offset = 60
            choices = self.model.content.choices

            for i, choice in enumerate(choices[:3]):  # Max 3 affichés
                choice_txt = f"[[ {choice.text} ]]"
                # Tronquer si trop long
                metrics = QFontMetrics(font_content)
                choice_txt = metrics.elidedText(choice_txt, Qt.ElideRight, self.width - 30)

                painter.drawText(content_rect.x(), content_rect.y() + y_offset, choice_txt)
                y_offset += 18

            # Indicateur si plus de choix
            if len(choices) > 3:
                painter.setPen(QColor("#555"))
                painter.drawText(content_rect.x(), content_rect.y() + y_offset, f"... (+{len(choices) - 3})")

        elif self.model.type == NodeType.SET_VAR:
            painter.setPen(QColor("#2ecc71"))
            # Legacy var display
            txt = f"{self.model.content.variable_name} {self.model.content.operation} {self.model.content.value}"
            painter.drawText(content_rect, Qt.AlignCenter, txt)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.model.position = [value.x(), value.y()]
        return super().itemChange(change, value)