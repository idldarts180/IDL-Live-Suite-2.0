"""
IDL Live Suite
Player Name
"""

import tkinter.font as tkfont
from ui.theme import *


class PlayerName:

    def __init__(self, canvas):
        self.canvas = canvas
        self.max_width = 250
        self.item = None

    def _font_size(self, name):
        size = 20

        while size >= 14:
            font = tkfont.Font(
                family="Segoe UI",
                size=size,
                weight="bold"
            )

            if font.measure(name) <= self.max_width:
                return size

            size -= 1

        return 14

    def draw(self, x, y, name):
        size = self._font_size(name)

        self.item = self.canvas.create_text(
            x,
            y,
            text=name,
            fill=GOLD,
            font=("Segoe UI", size, "bold"),
            anchor="center",
            tags="player"
        )

        return self.item

    def update(self, name):
        if self.item is None:
            return

        size = self._font_size(name)

        self.canvas.itemconfigure(
            self.item,
            text=name,
            font=("Segoe UI", size, "bold")
        )