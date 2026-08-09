"""
IDL Live Suite
Broadcast Overlay V4

Persistent, data-driven broadcast overlay.
Uses MatchController for live match data without redrawing canvas items.
"""

import tkinter as tk
import sys
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
from ui.components.average_text import AverageText
from ui.components.checkout_text import CheckoutText
from ui.components.celebration_180 import Celebration180
from ui.components.result_celebration import ResultCelebration
from ui.checkout_engine import get_checkout
from ui.app_paths import ICONS_DIR
from ui.components.centre_info import CentreInfo
from ui.components.banner import Banner

from controllers.match_controller import MatchController


APP_ICON = ICONS_DIR / "idl_live_suite.ico"


class BroadcastOverlay(ctk.CTk):

    def __init__(self, provider_name="scolia"):
        super().__init__()

        if APP_ICON.exists():
            try:
                self.iconbitmap(str(APP_ICON))
            except Exception:
                pass

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

        self.left_result = ResultCelebration(self.canvas)
        self.right_result = ResultCelebration(self.canvas)

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

        # Match-progress celebrations are provider-independent. Both
        # Scolia and DartCounter already populate legs/sets in Match.
        self._last_progress = None
        self._result_celebrating = [False, False]
        self._result_finish_jobs = [None, None]
        self._pending_leg_jobs = [None, None]

        # Keep the match-winning targets once we have read them. Some
        # platforms briefly clear/change their format text as the match ends,
        # which previously meant the final WINNER event could lose the target.
        self._cached_leg_target = None
        self._cached_set_target = None
        self._winner_fired = [False, False]
        self._last_match_winner_event = 0

        # Once a match winner is known, keep the overlay on the true final
        # result even if Scolia/DartCounter immediately leave the live scoring
        # screen and continue returning stale pre-finish values.
        self._final_result = None

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

        if (
            self._celebrating_180[player_index]
            or self._result_celebrating[player_index]
        ):
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

        if not self._result_celebrating[player_index]:
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

    @staticmethod
    def _target_from_format(format_text, unit):
        """
        Return the number of legs/sets needed to win the match.

        Examples:
            RACE TO 3 LEGS  -> 3
            FIRST TO 4 LEGS -> 4
            BEST OF 5 LEGS  -> 3
            BEST OF 3 SETS  -> 2
        """
        import re

        text = str(format_text).upper()
        unit_pattern = "SETS?" if unit == "sets" else "LEGS?"

        direct = re.search(
            rf"(?:RACE TO|FIRST TO)\s+(\d+)\s+{unit_pattern}",
            text
        )

        if direct:
            return int(direct.group(1))

        best_of = re.search(
            rf"BEST OF\s+(\d+)\s+{unit_pattern}",
            text
        )

        if best_of:
            total = int(best_of.group(1))
            return (total // 2) + 1

        return None

    def _cancel_pending_leg(self, player_index):
        job = self._pending_leg_jobs[player_index]

        if job is not None:
            try:
                self.after_cancel(job)
            except Exception:
                pass

            self._pending_leg_jobs[player_index] = None

    def _schedule_leg_win(self, player_index):
        """
        In set play, briefly wait before showing LEG WIN.

        Some providers update the leg and set score in separate DOM refreshes.
        The short delay gives SET WIN / WINNER a chance to replace the pending
        leg celebration instead of showing two graphics for the same dart.
        """
        self._cancel_pending_leg(player_index)

        self._pending_leg_jobs[player_index] = self.after(
            400,
            lambda index=player_index: self._fire_pending_leg(index)
        )

    def _fire_pending_leg(self, player_index):
        self._pending_leg_jobs[player_index] = None
        self._start_result_celebration(player_index, "leg")

    def _hide_player_text(self, player_index):
        if player_index == 0:
            keys = (
                "left_name",
                "left_score",
                "left_average",
                "left_checkout",
            )
        else:
            keys = (
                "right_name",
                "right_score",
                "right_average",
                "right_checkout",
            )

        for key in keys:
            item = self.items.get(key)
            if item is not None:
                self.canvas.itemconfigure(item, state="hidden")

    def _restore_player_text(self, player_index):
        if player_index == 0:
            keys = (
                "left_name",
                "left_score",
                "left_average",
                "left_checkout",
            )
        else:
            keys = (
                "right_name",
                "right_score",
                "right_average",
                "right_checkout",
            )

        for key in keys:
            item = self.items.get(key)
            if item is not None:
                self.canvas.itemconfigure(item, state="normal")

    def _start_result_celebration(self, player_index, kind):
        """
        Celebration priority:
            WINNER > SET WIN > LEG WIN

        The graphic temporarily takes over the whole player circle, then the
        normal name / score / 3DA-or-checkout stack returns.
        """
        priorities = {
            "leg": 1,
            "set": 2,
            "winner": 3,
        }

        durations = {
            "leg": 1500,
            "set": 2000,
            "winner": 3000,
        }

        self._cancel_pending_leg(player_index)

        if player_index == 0:
            visual = self.left_result
        else:
            visual = self.right_result

        current = getattr(
            self,
            "_active_result_kind_" + str(player_index),
            None
        )

        # Do not let a lower-priority event replace a stronger one.
        if (
            current is not None
            and priorities.get(current, 0) > priorities.get(kind, 0)
        ):
            return

        old_job = self._result_finish_jobs[player_index]

        if old_job is not None:
            try:
                self.after_cancel(old_job)
            except Exception:
                pass

        setattr(
            self,
            "_active_result_kind_" + str(player_index),
            kind
        )

        self._result_celebrating[player_index] = True

        # A result event supersedes a score-level 180 visual if one somehow
        # overlaps during a provider refresh.
        if player_index == 0:
            self.left_180.hide()
        else:
            self.right_180.hide()

        self._hide_player_text(player_index)

        visual.show(kind)

        self.after(
            90,
            lambda v=visual, k=kind: v.set_large(k)
        )

        self.after(
            220,
            lambda v=visual, k=kind: v.set_normal(k)
        )

        self._result_finish_jobs[player_index] = self.after(
            durations[kind],
            lambda index=player_index: self._finish_result_celebration(index)
        )

    def _finish_result_celebration(self, player_index):
        if player_index == 0:
            visual = self.left_result
        else:
            visual = self.right_result

        visual.hide()
        self._restore_player_text(player_index)

        self._result_finish_jobs[player_index] = None
        self._result_celebrating[player_index] = False

        setattr(
            self,
            "_active_result_kind_" + str(player_index),
            None
        )

    def _reset_final_result_if_new_match(self, match):
        """
        Release the final-result lock only when the provider explicitly says
        that a live scoring screen is active again.

        DartCounter now marks match.match_active=True after it has successfully
        parsed a live scoring screen. That makes Rematch/new-game detection
        reliable without confusing the completed result screen for a new match.
        """
        if self._final_result is None:
            return

        if not bool(getattr(match, "match_active", False)):
            return

        scores = [
            int(getattr(match, "player1_score", 501) or 0),
            int(getattr(match, "player2_score", 501) or 0),
        ]

        # A real new live game has both players back in play. Do not require
        # legs/sets to be exactly 0 here because DartCounter can populate those
        # a fraction of a second later than the score panel.
        if not (scores[0] > 0 and scores[1] > 0):
            return

        self._final_result = None
        self._winner_fired = [False, False]
        self._last_progress = None
        self._cached_leg_target = None
        self._cached_set_target = None

        # Consume the provider's current winner-event counter so the previous
        # game's WINNER event cannot replay in the new match.
        self._last_match_winner_event = int(
            getattr(match, "match_winner_event", 0) or 0
        )

        print("Overlay: new live match detected - final result lock cleared.")

    def _lock_final_result(self, match, winner_index):
        """
        Freeze the overlay on the correct completed-match state.

        Both providers can leave their scoring screen before the last DOM
        refresh contains the final zero and final leg/set count. Once we know
        the winner, the overlay itself is the safest place to preserve the
        finished score.
        """
        if self._final_result is not None:
            return

        format_text = getattr(match, "match_format", "") or ""

        parsed_leg_target = self._target_from_format(
            format_text,
            "legs"
        )
        parsed_set_target = self._target_from_format(
            format_text,
            "sets"
        )

        if parsed_leg_target is not None:
            self._cached_leg_target = parsed_leg_target

        if parsed_set_target is not None:
            self._cached_set_target = parsed_set_target

        leg_target = self._cached_leg_target
        set_target = self._cached_set_target

        # Some providers clear/reset is_set_play on the final navigation.
        # Keep set-play mode if we already cached a set target earlier in the
        # match, or if the surviving format text still says SET/SETS.
        is_set_play = bool(
            getattr(match, "is_set_play", False)
            or self._cached_set_target is not None
            or "SET" in format_text.upper()
        )

        scores = [
            int(getattr(match, "player1_score", 501) or 0),
            int(getattr(match, "player2_score", 501) or 0),
        ]

        legs = [
            int(getattr(match, "player1_legs", 0) or 0),
            int(getattr(match, "player2_legs", 0) or 0),
        ]

        sets = [
            int(getattr(match, "player1_sets", 0) or 0),
            int(getattr(match, "player2_sets", 0) or 0),
        ]

        # Winning checkout always finishes on zero.
        scores[winner_index] = 0

        if is_set_play:
            if set_target is not None:
                sets[winner_index] = max(
                    sets[winner_index],
                    set_target
                )

            # Show the completed deciding set rather than the stale
            # pre-finish leg count when a leg target is known.
            if leg_target is not None:
                legs[winner_index] = max(
                    legs[winner_index],
                    leg_target
                )
        else:
            if leg_target is not None:
                legs[winner_index] = max(
                    legs[winner_index],
                    leg_target
                )

        self._final_result = {
            "winner_index": winner_index,
            "player1_name": getattr(
                match,
                "player1_name",
                "Player 1"
            ),
            "player2_name": getattr(
                match,
                "player2_name",
                "Player 2"
            ),
            "player1_score": scores[0],
            "player2_score": scores[1],
            "player1_average": getattr(
                match,
                "player1_average",
                0.0
            ),
            "player2_average": getattr(
                match,
                "player2_average",
                0.0
            ),
            "player1_legs": legs[0],
            "player2_legs": legs[1],
            "player1_sets": sets[0],
            "player2_sets": sets[1],
            "is_set_play": is_set_play,
            "match_format": format_text,
        }

    def _check_result_events(self, match):
        """
        Detect LEG WIN, SET WIN and MATCH WIN from the shared Match model.

        This is intentionally in the overlay rather than in either provider,
        so Scolia and DartCounter behave identically.
        """
        # Provider-level winner event. DartCounter needs this because it
        # navigates away from the score screen before its final leg/score
        # counters can be read.
        explicit_winner_event = int(
            getattr(match, "match_winner_event", 0) or 0
        )

        if explicit_winner_event > self._last_match_winner_event:
            self._last_match_winner_event = explicit_winner_event

            winner_index = getattr(
                match,
                "match_winner_player",
                None
            )

            if winner_index in (0, 1):
                self._winner_fired[winner_index] = True
                self._lock_final_result(
                    match,
                    winner_index
                )
                self._start_result_celebration(
                    winner_index,
                    "winner"
                )

        legs = [
            int(getattr(match, "player1_legs", 0) or 0),
            int(getattr(match, "player2_legs", 0) or 0),
        ]

        sets = [
            int(getattr(match, "player1_sets", 0) or 0),
            int(getattr(match, "player2_sets", 0) or 0),
        ]

        scores = [
            int(getattr(match, "player1_score", 501) or 0),
            int(getattr(match, "player2_score", 501) or 0),
        ]

        is_set_play = bool(
            getattr(match, "is_set_play", False)
        )

        format_text = getattr(match, "match_format", "")

        current = (
            legs[0],
            legs[1],
            sets[0],
            sets[1],
            is_set_play,
        )

        # Seed on first valid update. This prevents celebrations firing when
        # the overlay is opened halfway through an already-running match.
        if self._last_progress is None:
            self._last_progress = current
            return

        previous = self._last_progress

        prev_legs = [previous[0], previous[1]]
        prev_sets = [previous[2], previous[3]]

        parsed_set_target = self._target_from_format(
            format_text,
            "sets"
        )

        parsed_leg_target = self._target_from_format(
            format_text,
            "legs"
        )

        # Cache valid targets for the lifetime of the match. The final
        # DartCounter/Scolia refresh can remove the format text at exactly the
        # moment the winning leg/set is awarded, so relying only on the current
        # DOM caused LEG WIN / SET WIN to work but WINNER to be missed.
        if parsed_set_target is not None:
            self._cached_set_target = parsed_set_target

        if parsed_leg_target is not None:
            self._cached_leg_target = parsed_leg_target

        set_target = self._cached_set_target
        leg_target = self._cached_leg_target

        # IMPORTANT:
        # On the final dart, DartCounter/Scolia can leave the live-match page
        # before the final leg/set counter reaches the overlay. That means
        # waiting only for "legs increased" or "sets increased" can miss the
        # match winner completely.
        #
        # We can safely infer the match-winning dart while score == 0:
        # - leg play: player was already one leg from the match target
        # - set play: player was already one set from the match target AND
        #   one leg from the set target
        #
        # This happens before the provider has a chance to leave/reset the
        # match screen, so WINNER is not lost on the final refresh.
        for player_index in (0, 1):
            if self._winner_fired[player_index]:
                continue

            inferred_winner = False

            if scores[player_index] == 0:
                if not is_set_play:
                    inferred_winner = (
                        leg_target is not None
                        and legs[player_index] >= leg_target - 1
                    )
                else:
                    inferred_winner = (
                        set_target is not None
                        and leg_target is not None
                        and sets[player_index] >= set_target - 1
                        and legs[player_index] >= leg_target - 1
                    )

            if inferred_winner:
                self._winner_fired[player_index] = True
                self._lock_final_result(
                    match,
                    player_index
                )
                self._start_result_celebration(
                    player_index,
                    "winner"
                )

        for player_index in (0, 1):
            set_increased = sets[player_index] > prev_sets[player_index]
            leg_increased = legs[player_index] > prev_legs[player_index]

            if is_set_play:
                # Match winner beats every other celebration.
                if (
                    set_increased
                    and set_target is not None
                    and sets[player_index] >= set_target
                ):
                    if not self._winner_fired[player_index]:
                        self._winner_fired[player_index] = True
                        self._lock_final_result(
                            match,
                            player_index
                        )
                        self._start_result_celebration(
                            player_index,
                            "winner"
                        )

                # A set win supersedes a leg win on the same finishing dart.
                elif set_increased:
                    self._start_result_celebration(
                        player_index,
                        "set"
                    )

                elif leg_increased:
                    self._schedule_leg_win(player_index)

            else:
                # Leg-play match winner.
                if (
                    leg_increased
                    and leg_target is not None
                    and legs[player_index] >= leg_target
                ):
                    if not self._winner_fired[player_index]:
                        self._winner_fired[player_index] = True
                        self._lock_final_result(
                            match,
                            player_index
                        )
                        self._start_result_celebration(
                            player_index,
                            "winner"
                        )

                elif leg_increased:
                    self._start_result_celebration(
                        player_index,
                        "leg"
                    )

        self._last_progress = current

    def set_match(self, match):
        """
        Apply a Match model to the persistent overlay components.

        After a winner is known, use the overlay's locked final result instead
        of stale provider values returned after the scoring page disappears.
        """

        self._reset_final_result_if_new_match(match)

        self._check_result_events(match)
        self._check_180_events(match)

        final = self._final_result

        if final is not None:
            player1_name = final["player1_name"]
            player2_name = final["player2_name"]

            player1_score = final["player1_score"]
            player2_score = final["player2_score"]

            player1_average = final["player1_average"]
            player2_average = final["player2_average"]

            player1_legs = final["player1_legs"]
            player2_legs = final["player2_legs"]

            player1_sets = final["player1_sets"]
            player2_sets = final["player2_sets"]

            is_set_play = final["is_set_play"]
            match_format = final["match_format"]

            # No checkout route is relevant after the match is complete.
            player1_checkout_route = ""
            player2_checkout_route = ""

        else:
            player1_name = getattr(
                match,
                "player1_name",
                "Player 1"
            )
            player2_name = getattr(
                match,
                "player2_name",
                "Player 2"
            )

            player1_score = getattr(
                match,
                "player1_score",
                501
            )
            player2_score = getattr(
                match,
                "player2_score",
                501
            )

            player1_average = getattr(
                match,
                "player1_average",
                0.0
            )
            player2_average = getattr(
                match,
                "player2_average",
                0.0
            )

            player1_legs = getattr(
                match,
                "player1_legs",
                0
            )
            player2_legs = getattr(
                match,
                "player2_legs",
                0
            )

            player1_sets = getattr(
                match,
                "player1_sets",
                0
            )
            player2_sets = getattr(
                match,
                "player2_sets",
                0
            )

            is_set_play = getattr(
                match,
                "is_set_play",
                False
            )

            match_format = getattr(
                match,
                "match_format",
                ""
            )

            player1_checkout_route = get_checkout(
                player1_score,
                getattr(
                    match,
                    "player1_darts_remaining",
                    3
                )
            )

            player2_checkout_route = get_checkout(
                player2_score,
                getattr(
                    match,
                    "player2_darts_remaining",
                    3
                )
            )

        self.left_name.update(player1_name)
        self.right_name.update(player2_name)

        self.left_score.update(player1_score)
        self.right_score.update(player2_score)

        # Use the same line for 3DA and checkout information.
        if player1_checkout_route:
            self.canvas.itemconfigure(
                self.items["left_average"],
                text=""
            )
            self.left_checkout.update(
                player1_checkout_route
            )
        else:
            self.left_checkout.update("")
            self.left_average.update(
                player1_average
            )

        if player2_checkout_route:
            self.canvas.itemconfigure(
                self.items["right_average"],
                text=""
            )
            self.right_checkout.update(
                player2_checkout_route
            )
        else:
            self.right_checkout.update("")
            self.right_average.update(
                player2_average
            )

        if not match_format:
            first_to = getattr(
                match,
                "first_to",
                None
            )

            if first_to:
                match_format = (
                    f"Race to {first_to} Legs"
                )
            else:
                match_format = "Waiting for match"

        self.centre_info.update(
            player1_legs,
            player2_legs,
            match_format,
            player1_sets,
            player2_sets,
            is_set_play
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
        # Result Celebration Visuals
        # =====================================

        self.items["left_result"] = self.left_result.draw(
            left_score_pos["x"],
            left_score_pos["y"]
        )

        self.items["right_result"] = self.right_result.draw(
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