"""
IDL Live Suite
Centre Info
"""

from ui.theme import *
from ui.layout_manager import LayoutManager


class CentreInfo:

    def __init__(self, canvas):

        self.canvas = canvas

        self.layout = LayoutManager()

    # ======================================================

    def draw(
        self,
        player1_legs,
        player2_legs,
        format_text
    ):

        legs = self.layout.get("legs")
        format_pos = self.layout.get("format")

        # ==========================================
        # Legs
        # ==========================================

        legs_item = self.canvas.create_text(

            legs["x"],
            legs["y"],

            text=f"{player1_legs} - {player2_legs}",

            fill=GOLD,

            font=("Segoe UI", 75, "bold"),

            anchor="center",

            tags="centre"

        )

        # ==========================================
        # Match Format
        # ==========================================

        format_item = self.canvas.create_text(

            format_pos["x"],
            format_pos["y"],

            text=format_text,

            fill=WHITE,

            font=("Segoe UI", 18, "bold"),

            anchor="center",

            tags="centre"

        )

        return {
            "legs": legs_item,
            "format": format_item
        }