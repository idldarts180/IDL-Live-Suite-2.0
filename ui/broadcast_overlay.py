"""
IDL Live Suite
Broadcast Overlay V4

Persistent, data-driven broadcast overlay.
Uses MatchController for live match data without redrawing canvas items.
"""

import tkinter as tk
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

from controllers.match_controller import MatchController


class BroadcastOverlay(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("IDL Live Suite")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color=BACKGROUND)
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
        # Layout
        # ==========================================

        self.layout = LayoutManager()

        # ==========================================
        # Components
        # ==========================================

        self.shell = Shell(self.canvas)
        self.logo = LogoBadge(self.canvas)

        # Independent instances are important:
        # each player/score owns its own persistent canvas item.
        self.left_name = PlayerName(self.canvas)
        self.right_name = PlayerName(self.canvas)

        self.left_score = ScoreText(self.canvas)
        self.right_score = ScoreText(self.canvas)

        self.centre_info = CentreInfo(self.canvas)
        self.banner = Banner(self.canvas)

        # ==========================================
        # Match Controller
        # ==========================================

        self.controller = MatchController()
        self.scolia_connected = False

        # ==========================================
        # Canvas Item Registry
        # Used by the F2 layout editor
        # ==========================================

        self.items = {}

        # ==========================================
        # Layout Editor
        # ==========================================

        self.editor = LayoutEditor(self)
        self.bind("<F2>", lambda event: self.editor.toggle())

        # ==========================================
        # Initial Draw
        # ==========================================

        self.draw()

        # Keep banner text live without redrawing overlay.
        self.refresh_banner()

        # Start Scolia connection after the window has appeared.
        self.after(100, self.connect_scolia)

        # Clean up browser when overlay closes.
        self.protocol("WM_DELETE_WINDOW", self.close_overlay)

    # ======================================================
    # Scolia
    # ======================================================

    def connect_scolia(self):
        """
        Connect the existing MatchController/ScoliaProvider.
        If connection fails, keep the overlay open and show waiting state.
        """

        try:
            self.controller.connect()
            self.scolia_connected = True
            print("Scolia connected to broadcast overlay.")

            self.update_match()

        except Exception as exc:
            self.scolia_connected = False
            print(f"Scolia connection error: {exc}")

            # Retry after 2 seconds rather than crashing the overlay.
            self.after(2000, self.connect_scolia)

    # ======================================================

    def update_match(self):
        """
        Pull the latest Match object and update existing canvas items only.
        Nothing is redrawn, so F2 selection/positioning stays intact.
        """

        if not self.scolia_connected:
            return

        try:
            match = self.controller.update()

            if match is not None:
                self.set_match(match)

        except Exception as exc:
            print(f"Overlay update error: {exc}")

        # Four updates per second is plenty for darts scoring.
        self.after(250, self.update_match)

    # ======================================================

    def set_match(self, match):
        """
        Apply a Match model to the persistent overlay components.
        """

        self.left_name.update(
            getattr(match, "player1_name", "Player 1")
        )

        self.right_name.update(
            getattr(match, "player2_name", "Player 2")
        )

        self.left_score.update(
            getattr(match, "player1_score", 501)
        )

        self.right_score.update(
            getattr(match, "player2_score", 501)
        )

        player1_legs = getattr(match, "player1_legs", 0)
        player2_legs = getattr(match, "player2_legs", 0)

        match_format = getattr(
            match,
            "match_format",
            ""
        )

        # Fallback until Scolia has supplied a format.
        if not match_format:
            first_to = getattr(match, "first_to", None)

            if first_to:
                match_format = f"Race to {first_to} Legs"
            else:
                match_format = "Waiting for match"

        self.centre_info.update(
            player1_legs,
            player2_legs,
            match_format
        )

    # ======================================================
    # Banner
    # ======================================================

    def refresh_banner(self):
        """
        Refresh only the banner text.
        This deliberately does not call draw().
        """

        try:
            self.banner.refresh()
        except Exception as exc:
            print(f"Banner refresh error: {exc}")

        self.after(250, self.refresh_banner)

    # ======================================================
    # Draw
    # ======================================================

    def draw(self):
        """
        Create all canvas items once.
        Live data changes are handled by update methods afterwards.
        """

        # =====================================
        # Shell
        # =====================================

        self.shell.draw()

        # =====================================
        # Developer Grid
        # =====================================

        DEV_GRID = False

        if DEV_GRID:

            # Grid every 50px
            for x in range(0, WINDOW_WIDTH + 1, 50):
                self.canvas.create_line(
                    x,
                    0,
                    x,
                    WINDOW_HEIGHT,
                    fill="#2d2d2d",
                    dash=(2, 4)
                )

            for y in range(0, WINDOW_HEIGHT + 1, 50):
                self.canvas.create_line(
                    0,
                    y,
                    WINDOW_WIDTH,
                    y,
                    fill="#2d2d2d",
                    dash=(2, 4)
                )

            # Centre vertical
            self.canvas.create_line(
                WINDOW_WIDTH // 2,
                0,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT,
                fill="red",
                width=2
            )

            # Centre horizontal
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

        left_name_pos = self.layout.get("left_name")
        right_name_pos = self.layout.get("right_name")

        left_score_pos = self.layout.get("left_score")
        right_score_pos = self.layout.get("right_score")

        # =====================================
        # Player Names
        # =====================================

        self.items["left_name"] = self.left_name.draw(
            left_name_pos["x"],
            left_name_pos["y"],
            "Waiting..."
        )

        self.items["right_name"] = self.right_name.draw(
            right_name_pos["x"],
            right_name_pos["y"],
            "Waiting..."
        )

        # =====================================
        # Scores
        # =====================================

        self.items["left_score"] = self.left_score.draw(
            left_score_pos["x"],
            left_score_pos["y"],
            501
        )

        self.items["right_score"] = self.right_score.draw(
            right_score_pos["x"],
            right_score_pos["y"],
            501
        )

        # =====================================
        # Centre Info
        # =====================================

        centre_items = self.centre_info.draw(
            player1_legs=0,
            player2_legs=0,
            format_text="Waiting for match"
        )

        self.items["legs"] = centre_items["legs"]
        self.items["format"] = centre_items["format"]

        # =====================================
        # Banner
        # =====================================

        self.items["banner"] = self.banner.draw()

    # ======================================================
    # Shutdown
    # ======================================================

    def close_overlay(self):
        try:
            self.controller.close()
        except Exception:
            pass

        self.destroy()


if __name__ == "__main__":
    app = BroadcastOverlay()
    app.mainloop()