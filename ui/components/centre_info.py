"""
IDL Live Suite
Centre Info
"""

from ui.theme import *
from ui.layout_manager import LayoutManager

class CentreInfo:

    def __init__(self, canvas):
        self.canvas=canvas
        self.layout=LayoutManager()
        self.legs_item=None
        self.format_item=None

    def draw(self, player1_legs, player2_legs, format_text):
        legs=self.layout.get("legs")
        fmt=self.layout.get("format")

        self.legs_item=self.canvas.create_text(
            legs["x"], legs["y"],
            text=f"{player1_legs} - {player2_legs}",
            fill=GOLD,
            font=("Segoe UI",75,"bold"),
            anchor="center",
            tags="centre"
        )

        self.format_item=self.canvas.create_text(
            fmt["x"], fmt["y"],
            text=format_text,
            fill=WHITE,
            font=("Segoe UI",18,"bold"),
            anchor="center",
            tags="centre"
        )

        return {"legs":self.legs_item,"format":self.format_item}

    def update(self, player1_legs, player2_legs, format_text):
        if self.legs_item:
            self.canvas.itemconfigure(
                self.legs_item,
                text=f"{player1_legs} - {player2_legs}"
            )
        if self.format_item:
            self.canvas.itemconfigure(
                self.format_item,
                text=format_text
            )