from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPainterPath, QPen, QColor, QPainter
from PySide6.QtCore import Qt, QPointF


class ConnectionItem(QGraphicsPathItem):
    """
    Représente le lien visuel (câble) entre deux noeuds.
    Utilise une courbe de Bézier cubique.
    """

    def __init__(self, start_pos: QPointF, end_pos: QPointF, parent=None):
        super().__init__(parent)
        self.start_pos = start_pos
        self.end_pos = end_pos

        self.setZValue(-1)  # Toujours derrière les noeuds
        self.setPen(QPen(QColor("#AAA"), 2, Qt.SolidLine))
        self.update_path()

    def update_positions(self, start_pos: QPointF, end_pos: QPointF):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.update_path()

    def update_path(self):
        """Recalcule la courbe de Bézier."""
        path = QPainterPath()
        path.moveTo(self.start_pos)

        # Calcul des points de contrôle pour la tangence
        dx = self.end_pos.x() - self.start_pos.x()
        dy = self.end_pos.y() - self.start_pos.y()

        ctrl1 = QPointF(self.start_pos.x() + dx * 0.5, self.start_pos.y())
        ctrl2 = QPointF(self.end_pos.x() - dx * 0.5, self.end_pos.y())

        path.cubicTo(ctrl1, ctrl2, self.end_pos)
        self.setPath(path)

    def paint(self, painter, option, widget=None):
        """Dessin optimisé."""
        painter.setRenderHint(QPainter.Antialiasing)
        super().paint(painter, option, widget)