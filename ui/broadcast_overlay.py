"""
IDL Live Suite
Broadcast Overlay V3
"""

import tkinter as tk
import json
from pathlib import Path
import customtkinter as ctk

from ui.theme import *
from ui.layout import *

from ui.layout_manager import LayoutManager
from ui.layout_editor import LayoutEditor

from ui.components.shell import Shell
from ui.components.logo_badge import LogoBadge
from ui.components.player_name import PlayerName
from ui.components.score_text import ScoreText
from ui.components.centre_info import CentreInfo
from ui.components.banner import Banner

BANNER_FILE = Path(__file__).resolve().parent/"config"/"banner.json"


class BroadcastOverlay(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("IDL Live Suite")

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.configure(
            fg_color=BACKGROUND
        )

        self.resizable(False, False)

        # ==========================================
        # Canvas
        # ==========================================

        self.canvas = tk.Canvas(

            self,

            width=WINDOW_WIDTH,

            height=WINDOW_HEIGHT,

            bg=BACKGROUND,

            highlightthickness=0

        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        # ==========================================
        # Layout Manager
        # ==========================================

        self.layout = LayoutManager()

        # ==========================================
        # Components
        # ==========================================

        self.shell = Shell(self.canvas)
        self.logo = LogoBadge(self.canvas)
        self.player_name = PlayerName(self.canvas)
        self.score_text = ScoreText(self.canvas)
        self.centre_info = CentreInfo(self.canvas)
        self.banner = Banner(self.canvas)

        # ==========================================

        self.items = {}

        # ==========================================
        # Layout Editor
        # ==========================================

        self.editor = LayoutEditor(self)

        self.bind("<F2>", lambda e: self.editor.toggle())

        self.draw()
        self.refresh_banner()


    def refresh_banner(self):
        """Refresh only the banner text without redrawing the overlay."""
        try:
            if "banner" in self.items:
                self.canvas.itemconfigure(
                    self.items["banner"],
                    text=self.load_banner()
                )
        except Exception:
            pass

        self.after(250, self.refresh_banner)


    def load_banner(self):
        try:
            with open(BANNER_FILE,"r",encoding="utf-8") as f:
                return json.load(f).get("text","")
        except Exception:
            return ""

    # ======================================================

    def draw(self):

        self.canvas.delete("all")

        self.items.clear()

        # =====================================
        # Shell
        # =====================================

        self.shell.draw()

        # =====================================
        # DEVELOPER GRID
        # =====================================

        DEV_GRID = True

        if DEV_GRID:

            # Grid every 50px
            for x in range(0, WINDOW_WIDTH + 1, 50):

                self.canvas.create_line(
                    x, 0,
                    x, WINDOW_HEIGHT,
                    fill="#2d2d2d",
                    dash=(2, 4)
                )

            for y in range(0, WINDOW_HEIGHT + 1, 50):

                self.canvas.create_line(
                    0, y,
                    WINDOW_WIDTH, y,
                    fill="#2d2d2d",
                    dash=(2, 4)
                )

            # Centre Vertical
            self.canvas.create_line(
                WINDOW_WIDTH // 2,
                0,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT,
                fill="red",
                width=2
            )

            # Centre Horizontal
            self.canvas.create_line(
                0,
                WINDOW_HEIGHT // 2,
                WINDOW_WIDTH,
                WINDOW_HEIGHT // 2,
                fill="lime",
                width=2
            )

            # Coordinates
            for x in range(0, WINDOW_WIDTH + 1, 100):

                self.canvas.create_text(
                    x + 10,
                    10,
                    text=str(x),
                    fill="#888888",
                    font=("Segoe UI", 8)
                )

            for y in range(0, WINDOW_HEIGHT + 1, 100):

                self.canvas.create_text(
                    18,
                    y + 10,
                    text=str(y),
                    fill="#888888",
                    font=("Segoe UI", 8)
                )

        # =====================================
        # Logo
        # =====================================

        self.items["logo"] = self.logo.draw()

        # =====================================
        # Layout Positions
        # =====================================

        left_name = self.layout.get("left_name")
        left_score = self.layout.get("left_score")

        right_name = self.layout.get("right_name")
        right_score = self.layout.get("right_score")

        # =====================================
        # Left Player
        # =====================================

        self.items["left_name"] = self.player_name.draw(

            left_name["x"],
            left_name["y"],

            "Taylor"

        )

        self.items["left_score"] = self.score_text.draw(

            left_score["x"],
            left_score["y"],

            501

        )

        # =====================================
        # Right Player
        # =====================================

        self.items["right_name"] = self.player_name.draw(

            right_name["x"],
            right_name["y"],

            "Raging"

        )

        self.items["right_score"] = self.score_text.draw(

            right_score["x"],
            right_score["y"],

            321

        )

        # =====================================
        # Centre
        # =====================================

        centre = self.centre_info.draw(

            player1_legs=0,
            player2_legs=1,

            format_text="Race to 3 Legs"

        )

        self.items["legs"] = centre["legs"]
        self.items["format"] = centre["format"]

        self.items["banner"] = self.banner.draw()


if __name__ == "__main__":

    app = BroadcastOverlay()

    app.mainloop()