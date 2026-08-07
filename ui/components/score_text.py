"""
IDL Live Suite
Score Text
"""

from ui.theme import *


class ScoreText:

    def __init__(self, canvas):

        self.canvas = canvas

    # ======================================================

    def draw(self, x, y, score):

        item = self.canvas.create_text(

            x,
            y,

            text=str(score),

            fill=WHITE,

            font=("Segoe UI", 56, "bold"),

            anchor="center",

            tags="score"

        )

        return item