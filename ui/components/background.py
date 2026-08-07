"""
IDL Live Suite
Broadcast Background
"""

import tkinter as tk

from ui.theme import *


class BroadcastBackground:

    def __init__(self, canvas):

        self.canvas = canvas

    # ======================================================

    def draw(self):

        c = self.canvas

        # Clear everything
        c.delete("background")

        # ==================================================
        # Main Body
        # ==================================================

        c.create_rectangle(

            260,
            120,
            940,
            315,

            fill=PANEL,

            outline=BORDER,

            width=3,

            tags="background"

        )

        # ==================================================
        # Left Circle
        # ==================================================

        c.create_oval(

            80,
            70,
            380,
            370,

            fill=PANEL,

            outline=BORDER,

            width=3,

            tags="background"

        )

        # ==================================================
        # Right Circle
        # ==================================================

        c.create_oval(

            820,
            70,
            1120,
            370,

            fill=PANEL,

            outline=BORDER,

            width=3,

            tags="background"

        )

        # ==================================================
        # Logo Badge
        # ==================================================

        c.create_oval(

            495,
            0,
            705,
            180,

            fill=PANEL,

            outline=BORDER,

            width=3,

            tags="background"

        )

        # ==================================================
        # Competition Banner
        # ==================================================

        c.create_rectangle(

            350,
            305,
            850,
            355,

            fill=GOLD,

            outline=GOLD,

            tags="background"

        )