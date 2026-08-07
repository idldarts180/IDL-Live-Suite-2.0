"""
IDL Live Suite
Average Text
"""

from ui.theme import *


class AverageText:

    def __init__(self, canvas):
        self.canvas = canvas
        self.item = None

    def draw(self, x, y, average):
        self.item = self.canvas.create_text(
            x,
            y,
            text=f"3DA {float(average):.2f}",
            fill=WHITE,
            font=("Segoe UI", 12, "bold"),
            anchor="center",
            tags="average"
        )

        return self.item

    def update(self, average):
        if self.item is None:
            return

        try:
            value = float(average)
        except (TypeError, ValueError):
            value = 0.0

        self.canvas.itemconfigure(
            self.item,
            text=f"3DA {value:.2f}"
        )