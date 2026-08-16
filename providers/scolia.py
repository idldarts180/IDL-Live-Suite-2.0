"""
IDL Live Suite
Scolia Provider
Version 2.4 - Aborted match session reset
"""

from providers.base_provider import BaseProvider
from models.match import Match
from browser.playwright import Browser


class ScoliaProvider(BaseProvider):

    def __init__(self):
        super().__init__()

        self.provider_name = "Scolia"

        self.match = Match()
        self.match.provider = self.provider_name

        self.match.player1_darts_remaining = 0
        self.match.player2_darts_remaining = 0

        # Shared live-session state used by the broadcast overlay.
        self.match.match_active = False
        self.match.match_session_event = 0
        self.match.match_winner_event = getattr(
            self.match, "match_winner_event", 0
        )
        self.match.match_winner_player = None

        self.browser = Browser(
            profile="browser/profile",
            url="https://game.scoliadarts.com/game"
        )

        # A player becomes armed for a new 180 only after Scolia shows
        # fewer than three populated darts for that player's current visit.
        self._player_180_armed = [False, False]

        # Scolia can briefly redraw its live DOM. Require several consecutive
        # missing-live frames before calling the match aborted/left.
        self._non_live_updates = 0

    def connect(self):
        self.browser.connect()
        print("Connected to Scolia.")

    def wait_for_match(self):
        input("\nOpen your Scolia match then press ENTER...")

    def _mark_match_aborted_or_left(self):
        if not bool(getattr(self.match, "match_active", False)):
            return

        print(
            "Scolia: live match left/aborted - "
            "waiting for a new match."
        )

        self.match.match_active = False
        self.match.match_winner_player = None

        self.match.player1_darts_remaining = 0
        self.match.player2_darts_remaining = 0

        self._player_180_armed = [False, False]
        self._non_live_updates = 0

    def _note_non_live_update(self):
        if not bool(getattr(self.match, "match_active", False)):
            return

        self._non_live_updates += 1

        if self._non_live_updates >= 4:
            self._mark_match_aborted_or_left()

    def _update_darts_remaining(self, page):
        """
        Detect darts remaining independently for each player.
        """
        try:
            player_areas = page.locator(
                "div.styles_scoresAndHistoryContainerMultiple__j8x8N"
            )

            self.match.player1_darts_remaining = 0
            self.match.player2_darts_remaining = 0

            if player_areas.count() >= 2:
                p1_suggestions = player_areas.nth(0).locator(
                    "div.styles_throwSuggestion__L7zhL"
                ).count()

                p2_suggestions = player_areas.nth(1).locator(
                    "div.styles_throwSuggestion__L7zhL"
                ).count()

                self.match.player1_darts_remaining = max(
                    0, min(3, p1_suggestions)
                )

                self.match.player2_darts_remaining = max(
                    0, min(3, p2_suggestions)
                )

        except Exception:
            self.match.player1_darts_remaining = 0
            self.match.player2_darts_remaining = 0

    @staticmethod
    def _is_t20_throw(text):
        parts = [
            part.strip().upper()
            for part in str(text).replace("\r", "\n").split("\n")
            if part.strip()
        ]

        return "T20" in parts

    def _update_180_events(self, page):
        try:
            for player_index in (0, 1):
                throws = page.locator(
                    f"li[data-cy='throwsItem_{player_index}']"
                )

                texts = []

                for i in range(min(3, throws.count())):
                    texts.append(
                        throws.nth(i).inner_text().strip()
                    )

                populated = [
                    text for text in texts if text
                ]

                if len(populated) < 3:
                    self._player_180_armed[player_index] = True
                    continue

                if not self._player_180_armed[player_index]:
                    continue

                self._player_180_armed[player_index] = False

                if all(
                    self._is_t20_throw(text)
                    for text in populated[:3]
                ):
                    if player_index == 0:
                        self.match.player1_180_event += 1
                        print("Scolia: Player 1 hit a 180.")
                    else:
                        self.match.player2_180_event += 1
                        print("Scolia: Player 2 hit a 180.")

        except Exception as exc:
            print(f"Scolia 180 detection error: {exc}")

    def _update_match_scores(self, page):
        try:
            score_blocks = page.locator(
                "div.styles_score__AKlWV"
            )

            labelled_values = []

            for i in range(score_blocks.count()):
                block = score_blocks.nth(i)
                text = block.inner_text().strip().upper()

                values = block.locator(
                    "div.styles_value__Aj9KV"
                )

                if values.count() < 1:
                    continue

                try:
                    value = int(values.nth(0).inner_text().strip())
                except (TypeError, ValueError):
                    continue

                if "SETS" in text:
                    labelled_values.append(("SETS", value))
                elif "LEGS" in text:
                    labelled_values.append(("LEGS", value))

            sets = [v for label, v in labelled_values if label == "SETS"]
            legs = [v for label, v in labelled_values if label == "LEGS"]

            if len(sets) >= 2:
                self.match.player1_sets = sets[0]
                self.match.player2_sets = sets[1]
                self.match.is_set_play = True
            else:
                self.match.player1_sets = 0
                self.match.player2_sets = 0
                self.match.is_set_play = False

            if len(legs) >= 2:
                self.match.player1_legs = legs[0]
                self.match.player2_legs = legs[1]

        except Exception:
            pass

    def update(self):
        page = self.browser.page

        if page is None:
            self._note_non_live_update()
            return

        try:
            names = page.locator(
                "div.styles_nickname__uBJfP"
            )

            scores = page.locator(
                "span.styles_counter__ZHHHQ"
            )

            live_match_visible = (
                names.count() >= 2
                and scores.count() >= 2
            )

        except Exception:
            live_match_visible = False

        if not live_match_visible:
            self._note_non_live_update()
            return

        # A genuine live match is visible again.
        was_inactive = not bool(
            getattr(self.match, "match_active", False)
        )

        self._non_live_updates = 0
        self.match.match_active = True
        self.match.match_winner_player = None

        if was_inactive:
            self.match.match_session_event += 1

            # Do not let completed throw slots from the previous game trigger
            # a celebration in the new one.
            self._player_180_armed = [False, False]

            print(
                "Scolia: new live match session -> "
                f"{self.match.match_session_event}"
            )

        try:
            self.match.player1_name = names.nth(0).inner_text().strip()
            self.match.player2_name = names.nth(1).inner_text().strip()
        except Exception:
            pass

        try:
            self.match.player1_score = int(
                scores.nth(0).inner_text()
            )

            self.match.player2_score = int(
                scores.nth(1).inner_text()
            )
        except Exception:
            pass

        self._update_darts_remaining(page)
        self._update_180_events(page)

        try:
            stats = page.locator(
                "span[data-cy^='realtimeStatsValue_']"
            )

            if stats.count() >= 6:
                self.match.player1_average = float(
                    stats.nth(0).inner_text()
                )

                self.match.player1_first9 = float(
                    stats.nth(1).inner_text()
                )

                self.match.player1_checkout = float(
                    stats.nth(2).inner_text().replace("%", "")
                )

                self.match.player2_average = float(
                    stats.nth(3).inner_text()
                )

                self.match.player2_first9 = float(
                    stats.nth(4).inner_text()
                )

                self.match.player2_checkout = float(
                    stats.nth(5).inner_text().replace("%", "")
                )

        except Exception:
            pass

        try:
            self.match.match_format = page.locator(
                "div.styles_topbarRole__RsZ-3"
            ).inner_text()

        except Exception:
            pass

        self._update_match_scores(page)

    def get_match(self):
        return self.match

    def close(self):
        self.browser.close()