"""
IDL Live Suite
Centre Info
Version 2.1 - Legs + Sets
"""

from ui.theme import *
from ui.layout_manager import LayoutManager


class CentreInfo:

    def __init__(self, canvas):
        self.canvas = canvas
        self.layout = LayoutManager()

        self.main_score_item = None
        self.secondary_score_item = None
        self.format_item = None

    def draw(
        self,
        player1_legs,
        player2_legs,
        format_text,
        player1_sets=0,
        player2_sets=0,
        is_set_play=False
    ):
        main = self.layout.get("legs")
        fmt = self.layout.get("format")

        # ==========================================
        # Main score
        #
        # Leg play = legs
        # Set play = sets
        # ==========================================

        self.main_score_item = self.canvas.create_text(
            main["x"],
            main["y"],
            text="0 - 0",
            fill=GOLD,
            font=("Segoe UI", 75, "bold"),
            anchor="center",
            tags="centre"
        )

        # ==========================================
        # Secondary score
        #
        # Used for LEGS underneath the set score
        # during set-play matches.
        # ==========================================

        self.secondary_score_item = self.canvas.create_text(
            main["x"],
            main["y"] + 52,
            text="",
            fill=WHITE,
            font=("Segoe UI", 14, "bold"),
            anchor="center",
            tags="centre"
        )

        # ==========================================
        # Match format
        # ==========================================

        self.format_item = self.canvas.create_text(
            fmt["x"],
            fmt["y"],
            text=format_text,
            fill=WHITE,
            font=("Segoe UI", 18, "bold"),
            anchor="center",
            tags="centre"
        )

        self.update(
            player1_legs,
            player2_legs,
            format_text,
            player1_sets,
            player2_sets,
            is_set_play
        )

        return {
            "legs": self.main_score_item,
            "set_legs": self.secondary_score_item,
            "format": self.format_item
        }

    def update(
        self,
        player1_legs,
        player2_legs,
        format_text,
        player1_sets=0,
        player2_sets=0,
        is_set_play=False
    ):
        main = self.layout.get("legs")
        fmt = self.layout.get("format")

        # ==========================================
        # SET PLAY
        # ==========================================

        if is_set_play:

            # Big gold numbers = SETS
            self.canvas.itemconfigure(
                self.main_score_item,
                text=f"{player1_sets} - {player2_sets}"
            )

            self.canvas.coords(
                self.main_score_item,
                main["x"],
                main["y"] - 8
            )

            # Small white numbers underneath = LEGS
            self.canvas.itemconfigure(
                self.secondary_score_item,
                text=f"LEGS  {player1_legs} - {player2_legs}"
            )

            self.canvas.coords(
                self.secondary_score_item,
                main["x"],
                main["y"] + 45
            )

            # Match format underneath.
            #
            # Raised slightly compared with the previous
            # version so it has a clean gap above the
            # gold competition banner.
            self.canvas.itemconfigure(
                self.format_item,
                text=format_text,
                font=("Segoe UI", 14, "bold")
            )

            self.canvas.coords(
                self.format_item,
                fmt["x"],
                fmt["y"] + 7
            )

        # ==========================================
        # NORMAL LEG PLAY
        # ==========================================

        else:

            # Big gold numbers = LEGS
            self.canvas.itemconfigure(
                self.main_score_item,
                text=f"{player1_legs} - {player2_legs}"
            )

            self.canvas.coords(
                self.main_score_item,
                main["x"],
                main["y"]
            )

            # No secondary score needed.
            self.canvas.itemconfigure(
                self.secondary_score_item,
                text=""
            )

            # Restore normal leg-play format position
            # and font size.
            self.canvas.itemconfigure(
                self.format_item,
                text=format_text,
                font=("Segoe UI", 18, "bold")
            )

            self.canvas.coords(
                self.format_item,
                fmt["x"],
                fmt["y"]
            )