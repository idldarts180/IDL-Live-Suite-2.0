"""
IDL Live Suite
Developer Guides
"""

from ui.theme import *


class DevGuides:

    def __init__(self, canvas):

        self.canvas = canvas

        self.enabled = True

    # =====================================================

    def draw(self, positions):

        if not self.enabled:
            return

        # ==========================================
        # Window Centre
        # ==========================================

        self.canvas.create_line(

            600,
            0,

            600,
            420,

            fill="#ff3b3b",

            width=2,

            dash=(6, 3)

        )

        self.canvas.create_line(

            0,
            210,

            1200,
            210,

            fill="#00ff66",

            width=2,

            dash=(6, 3)

        )

        # ==========================================
        # Object Guides
        # ==========================================

        colours = {

            "left_name": "#00d9ff",
            "left_score": "#00d9ff",

            "right_name": "#00d9ff",
            "right_score": "#00d9ff",

            "legs": "#ffd400",
            "format": "#ffffff",

            "logo": "#ff66ff"

        }

        for name, pos in positions.items():

            colour = colours.get(
                name,
                "#666666"
            )

            self.canvas.create_line(

                pos["x"],
                0,

                pos["x"],
                420,

                fill=colour,

                dash=(2, 2)

            )

            self.canvas.create_line(

                0,
                pos["y"],

                1200,
                pos["y"],

                fill=colour,

                dash=(2, 2)

            )

            self.canvas.create_text(

                pos["x"] + 8,
                pos["y"] - 8,

                text=name,

                fill=colour,

                font=("Segoe UI", 8, "bold"),

                anchor="sw"

            )