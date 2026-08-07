"""
IDL Live Suite
Score Text
"""

from ui.theme import *


class ScoreText:

    def __init__(self, canvas):
        self.canvas = canvas
        self.item = None

    def draw(self, x, y, score):
        self.item = self.canvas.create_text(
            x,
            y,
            text=str(score),
            fill=WHITE,
            font=("Segoe UI", 48, "bold"),
            anchor="center",
            tags="score"
        )

        return self.item

    def update(self, score):
        if self.item is None:
            return

        self.canvas.itemconfigure(
            self.item,
            text=str(score)
        )