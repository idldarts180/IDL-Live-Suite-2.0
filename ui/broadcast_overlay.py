"""
IDL Live Suite
Broadcast Overlay V4

Persistent, data-driven broadcast overlay.
Uses MatchController for live match data without redrawing canvas items.
"""

import tkinter as tk
import sys
import customtkinter as ctk

from ui.theme import *
from ui.layout import *

from ui.layout_manager import LayoutManager
from ui.layout_editor import LayoutEditor

from ui.components.shell import Shell
from ui.components.logo_badge import LogoBadge
from ui.components.player_name import PlayerName
from ui.components.score_text import ScoreText
from ui.components.average_text import AverageText
from ui.components.checkout_text import CheckoutText
from ui.components.celebration_180 import Celebration180
from ui.checkout_engine import get_checkout
from ui.components.centre_info import CentreInfo
from ui.components.banner import Banner

from controllers.match_controller import MatchController


class BroadcastOverlay(ctk.CTk):

    def __init__(self, provider_name="scolia"):
        super().__init__()

        self.provider_name = provider_name.lower().strip()

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

        self.left_average = AverageText(self.canvas)
        self.right_average = AverageText(self.canvas)

        self.left_checkout = CheckoutText(self.canvas)
        self.right_checkout = CheckoutText(self.canvas)

        self.left_180 = Celebration180(self.canvas)
        self.right_180 = Celebration180(self.canvas)

        self.centre_info = CentreInfo(self.canvas)
        self.banner = Banner(self.canvas)

        # ==========================================
        # Match Controller
        # ==========================================

        self.controller = MatchController(self.provider_name)
        self.provider_connected = False

        # ==========================================
        # Canvas Item Registry
        # Used by the F2 layout editor
        # ==========================================

        self.items = {}

        # Track provider event counters so each 180 celebration fires once.
        self._last_180_events = [0, 0]
        self._celebrating_180 = [False, False]

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

        # Start the selected provider connection after the window appears.
        self.after(100, self.connect_provider)

        # Clean up browser when overlay closes.
        self.protocol("WM_DELETE_WINDOW", self.close_overlay)

    # ======================================================
    # Live Provider
    # ======================================================

    def connect_provider(self):
        """
        Connect the selected provider through MatchController.
        If connection fails, keep the overlay open and show waiting state.
        """

        try:
            self.controller.connect()
            self.provider_connected = True
            print(f"{self.controller.provider.provider_name} connected to broadcast overlay.")

            self.update_match()

        except Exception as exc:
            self.provider_connected = False
            print(f"{self.provider_name} connection error: {exc}")

            # Retry after 2 seconds rather than crashing the overlay.
            self.after(2000, self.connect_provider)

    # ======================================================

    def update_match(self):
        """
        Pull the latest Match object and update existing canvas items only.
        Nothing is redrawn, so F2 selection/positioning stays intact.
        """

        if not self.provider_connected:
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

    def _start_180_celebration(self, player_index):
        """
        Temporarily replace the player's remaining score with the gold
        180 visual, pulse it, then reveal the updated remaining score.
        """

        if self._celebrating_180[player_index]:
            return

        self._celebrating_180[player_index] = True

        if player_index == 0:
            score_item = self.items["left_score"]
            visual = self.left_180
        else:
            score_item = self.items["right_score"]
            visual = self.right_180

        # Hide score, show 180, give it a short punch animation.
        self.canvas.itemconfigure(score_item, state="hidden")
        visual.show()

        self.after(90, visual.set_large)
        self.after(220, visual.set_normal)

        # Hold long enough to register visually, then reveal new score.
        self.after(
            1500,
            lambda index=player_index: self._finish_180_celebration(index)
        )

    def _finish_180_celebration(self, player_index):
        if player_index == 0:
            score_item = self.items["left_score"]
            visual = self.left_180
        else:
            score_item = self.items["right_score"]
            visual = self.right_180

        visual.hide()
        self.canvas.itemconfigure(score_item, state="normal")
        self._celebrating_180[player_index] = False

    def _check_180_events(self, match):
        current_events = [
            getattr(match, "player1_180_event", 0),
            getattr(match, "player2_180_event", 0),
        ]

        for index, event_value in enumerate(current_events):
            if event_value > self._last_180_events[index]:
                self._last_180_events[index] = event_value
                self._start_180_celebration(index)
            elif event_value < self._last_180_events[index]:
                # Defensive reset if a provider/model is restarted.
                self._last_180_events[index] = event_value

    def set_match(self, match):
        """
        Apply a Match model to the persistent overlay components.
        """

        self._check_180_events(match)

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

        player1_average = getattr(match, "player1_average", 0.0)
        player2_average = getattr(match, "player2_average", 0.0)

        player1_checkout_route = get_checkout(
            getattr(match, "player1_score", 501),
            getattr(match, "player1_darts_remaining", 3)
        )

        player2_checkout_route = get_checkout(
            getattr(match, "player2_score", 501),
            getattr(match, "player2_darts_remaining", 3)
        )

        # Use the same line for 3DA and checkout information.
        # If a checkout is available, temporarily hide the average.
        # As soon as the checkout disappears, restore the live 3DA.
        if player1_checkout_route:
            self.canvas.itemconfigure(
                self.items["left_average"],
                text=""
            )
            self.left_checkout.update(player1_checkout_route)
        else:
            self.left_checkout.update("")
            self.left_average.update(player1_average)

        if player2_checkout_route:
            self.canvas.itemconfigure(
                self.items["right_average"],
                text=""
            )
            self.right_checkout.update(player2_checkout_route)
        else:
            self.right_checkout.update("")
            self.right_average.update(player2_average)

        player1_legs = getattr(match, "player1_legs", 0)
        player2_legs = getattr(match, "player2_legs", 0)

        match_format = getattr(
            match,
            "match_format",
            ""
        )

        # Fallback until the selected provider has supplied a format.
        if not match_format:
            first_to = getattr(match, "first_to", None)

            if first_to:
                match_format = f"Race to {first_to} Legs"
            else:
                match_format = "Waiting for match"

        self.centre_info.update(
            player1_legs,
            player2_legs,
            match_format,
            getattr(match, "player1_sets", 0),
            getattr(match, "player2_sets", 0),
            getattr(match, "is_set_play", False)
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

        left_average_pos = self.layout.get("left_average")
        right_average_pos = self.layout.get("right_average")
        left_checkout_pos = self.layout.get("left_checkout")
        right_checkout_pos = self.layout.get("right_checkout")

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
        # 180 Celebration Visuals
        # =====================================

        self.items["left_180"] = self.left_180.draw(
            left_score_pos["x"],
            left_score_pos["y"]
        )

        self.items["right_180"] = self.right_180.draw(
            right_score_pos["x"],
            right_score_pos["y"]
        )

        # =====================================
        # 3-Dart Averages
        # =====================================

        self.items["left_average"] = self.left_average.draw(
            left_average_pos["x"],
            left_average_pos["y"],
            0.0
        )

        self.items["right_average"] = self.right_average.draw(
            right_average_pos["x"],
            right_average_pos["y"],
            0.0
        )

        self.items["left_checkout"] = self.left_checkout.draw(
            left_checkout_pos["x"], left_checkout_pos["y"], ""
        )
        self.items["right_checkout"] = self.right_checkout.draw(
            right_checkout_pos["x"], right_checkout_pos["y"], ""
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
    provider = "scolia"

    if len(sys.argv) > 1:
        provider = sys.argv[1].lower().strip()

    if provider not in ("scolia", "dartcounter"):
        print(f"Unknown provider '{provider}', defaulting to Scolia.")
        provider = "scolia"

    print(f"Starting IDL Live Suite overlay with {provider}.")

    app = BroadcastOverlay(provider)
    app.mainloop()