from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QBrush, QColor, QPen, QPainter, QFont, QFontMetrics
from PySide6.QtCore import Qt, QRectF
from src.common.constants import NodeType
from src.common.models import NodeModel


class NodeItem(QGraphicsItem):
    def __init__(self, model: NodeModel):
        super().__init__()
        self.model = model
        self.width = 220
        self.height = 140

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.setPos(self.model.position[0], self.model.position[1])

        # Couleurs
        if self.model.type == NodeType.SCENE:
            self.header_color = QColor("#5c4b8b")  # Violet
            self.body_color = QColor("#2a2a2a")
        elif self.model.type == NodeType.SET_VAR:
            self.header_color = QColor("#3b9b56")  # Vert
            self.body_color = QColor("#222")
        else:
            self.header_color = QColor("#444")
            self.body_color = QColor("#111")

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        rect = self.boundingRect()

        # 1. Ombre
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect.translated(4, 4), 6, 6)

        # 2. Corps
        painter.setBrush(QBrush(self.body_color))
        if self.isSelected():
            painter.setPen(QPen(QColor("#FFF"), 2))
        else:
            painter.setPen(QPen(QColor("#111"), 1))
        painter.drawRoundedRect(rect, 6, 6)

        # 3. En-tête
        header_rect = QRectF(0, 0, self.width, 35)
        painter.setBrush(QBrush(self.header_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(header_rect, 6, 6)
        painter.drawRect(0, 30, self.width, 5)  # Bas carré

        # 4. Titre (Nom de la scène)
        painter.setPen(QColor("#FFF"))
        font_title = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(font_title)

        # Fallback si 'title' n'existe pas encore
        display_title = getattr(self.model, 'title', self.model.id[:8])
        if self.model.type == NodeType.START:
            display_title = f"★ {display_title}"

        painter.drawText(header_rect, Qt.AlignCenter, display_title)

        # 5. Contenu (Preview)
        content_rect = QRectF(10, 45, self.width - 20, self.height - 55)
        font_content = QFont("Segoe UI", 9)
        painter.setFont(font_content)

        if self.model.type == NodeType.SCENE:
            # Aperçu du texte
            painter.setPen(QColor("#EEE"))
            preview_text = self.model.content.text[:30].replace('\n', ' ')
            if len(self.model.content.text) > 30: preview_text += "..."
            painter.drawText(content_rect.x(), content_rect.y() + 10, preview_text)

            # Aperçu des choix (Liste)
            painter.setPen(QColor("#AAA"))
            y_offset = 35
            for i, choice in enumerate(self.model.content.choices[:3]):  # Max 3 choix affichés
                choice_txt = f"[{i + 1}] {choice.text}"
                metrics = QFontMetrics(font_content)
                choice_txt = metrics.elidedText(choice_txt, Qt.ElideRight, self.width - 30)

                painter.drawText(content_rect.x(), content_rect.y() + y_offset, choice_txt)
                y_offset += 18

            if len(self.model.content.choices) > 3:
                painter.drawText(content_rect.x(), content_rect.y() + y_offset, "...")

        elif self.model.type == NodeType.SET_VAR:
            painter.setPen(QColor("#CCC"))
            txt = f"{self.model.content.variable_name} {self.model.content.operation} {self.model.content.value}"
            painter.drawText(content_rect, Qt.AlignCenter, txt)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.model.position = [value.x(), value.y()]
        return super().itemChange(change, value)