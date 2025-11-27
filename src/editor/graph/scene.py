from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import Qt, QLineF
import math


class NodeScene(QGraphicsScene):
    """
    La scène qui contient tous les noeuds.
    Gère le dessin de la grille de fond (Grid).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QColor("#181818")))
        self.grid_size = 20
        self.grid_color_light = QColor("#222")
        self.grid_color_dark = QColor("#111")

        # Taille virtuelle immense
        self.setSceneRect(-50000, -50000, 100000, 100000)

    def drawBackground(self, painter, rect):
        """Dessine une grille infinie performante."""
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        # Lignes fines
        lines_light = []
        lines_dark = []

        for x in range(first_left, right, self.grid_size):
            line = QLineF(x, top, x, bottom)
            if x % (self.grid_size * 5) == 0:
                lines_dark.append(line)
            else:
                lines_light.append(line)

        for y in range(first_top, bottom, self.grid_size):
            line = QLineF(left, y, right, y)
            if y % (self.grid_size * 5) == 0:
                lines_dark.append(line)
            else:
                lines_light.append(line)

        # Dessin
        painter.setPen(QPen(self.grid_color_light, 1))
        painter.drawLines(lines_light)

        painter.setPen(QPen(self.grid_color_dark, 2))
        painter.drawLines(lines_dark)