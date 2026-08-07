"""
IDL Live Suite
Broadcast Score Circle
"""

import tkinter as tk

from ui.theme import *


class ScoreCircle:

    def __init__(self, canvas):

        self.canvas = canvas

    def draw(self, x, y, player, score, average):

        c = self.canvas

        # Outer Gold Ring
        c.create_oval(
            x-145,
            y-145,
            x+145,
            y+145,
            fill=GOLD,
            outline="",
            tags="score"
        )

        # Dark Ring
        c.create_oval(
            x-136,
            y-136,
            x+136,
            y+136,
            fill="#222222",
            outline="",
            tags="score"
        )

        # Inner Circle
        c.create_oval(
            x-118,
            y-118,
            x+118,
            y+118,
            fill="#141414",
            outline=GOLD,
            width=2,
            tags="score"
        )

        # Player Name
        c.create_text(
            x,
            y-78,
            text=player,
            fill=GOLD,
            font=("Segoe UI",20,"bold"),
            tags="score"
        )

        # Score
        c.create_text(
            x,
            y+5,
            text=str(score),
            fill=WHITE,
            font=("Segoe UI",64,"bold"),
            tags="score"
        )

        # Average
        c.create_text(
            x,
            y+90,
            text=f"Average\n{average:.2f}",
            fill=GOLD,
            justify="center",
            font=("Segoe UI",16),
            tags="score"
        )