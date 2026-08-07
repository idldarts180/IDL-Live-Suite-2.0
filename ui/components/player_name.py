"""
IDL Live Suite
Player Name
"""

import tkinter.font as tkfont

from ui.theme import *


class PlayerName:

    def __init__(self, canvas):

        self.canvas = canvas

        # Maximum width the name is allowed to occupy
        self.max_width = 230

    # ======================================================

    def draw(self, x, y, name):

        # Start large
        size = 20

        while size >= 14:

            font = tkfont.Font(
                family="Segoe UI",
                size=size,
                weight="bold"
            )

            width = font.measure(name)

            if width <= self.max_width:
                break

            size -= 1

        item = self.canvas.create_text(

            x,
            y,

            text=name,

            fill=GOLD,

            font=("Segoe UI", size, "bold"),

            anchor="center",

            tags="player"

        )

        return item