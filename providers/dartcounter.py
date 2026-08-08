"""
IDL Live Suite
DartCounter Provider
Version 3.1

Reads live DartCounter match data from the Chrome/Playwright page and
populates the shared Match model used by the broadcast overlay.
"""

import re

from providers.base_provider import BaseProvider
from models.match import Match
from browser.playwright import Browser


class DartCounterProvider(BaseProvider):

    def __init__(self):

        super().__init__()

        self.provider_name = "DartCounter"

        self.match = Match()
        self.match.provider = self.provider_name

        self.browser = Browser(
            profile="browser/dartcounter_profile",
            url="https://app.dartcounter.net/dashboard"
        )

        # DartCounter can be manually scored, so the reliable provider-level
        # signal for a 180 is a submitted visit that reduces the remaining
        # score by exactly 180.
        self._previous_scores = [None, None]

    # ======================================================
    # Connection
    # ======================================================

    def connect(self):

        self.browser.connect()

        print("Connected to DartCounter.")

    # ======================================================

    def wait_for_match(self):

        print("Waiting for DartCounter match...")

    # ======================================================
    # Helpers
    # ======================================================

    def _get_page(self):
        """
        Return the active DartCounter page.

        DartCounter can keep page.url on /dashboard while the visible
        match content is rendered dynamically, so we do not require
        /game/match to appear in page.url.
        """

        try:
            pages = self.browser.context.pages

            # Prefer any tab that visibly contains a match.
            for page in reversed(pages):
                try:
                    body = page.locator("body").inner_text(timeout=1000)

                    if (
                        "3-dart avg." in body
                        and ("BEST OF" in body or "FIRST TO" in body or "RACE TO" in body)
                    ):
                        self.browser.page = page
                        return page
                except Exception:
                    pass

            # Otherwise use the browser's current page.
            if self.browser.page is not None:
                return self.browser.page

            if pages:
                self.browser.page = pages[-1]
                return pages[-1]

        except Exception:
            pass

        return self.browser.page

    # ======================================================

    @staticmethod
    def _clean_lines(text):
        return [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    # ======================================================

    @staticmethod
    def _to_int(value, default=0):
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return default

    # ======================================================

    @staticmethod
    def _to_float(value, default=0.0):
        try:
            cleaned = str(value).strip().replace("%", "")
            return float(cleaned)
        except (TypeError, ValueError):
            return default

    # ======================================================

    def _parse_player_from_average_label(self, lines, avg_index):
        """
        Robust DartCounter player parser.

        DartCounter can insert checkout suggestion text into the player block
        once a player reaches a finish. That means fixed offsets such as
        avg_index - 3 stop being reliable below 170.

        Instead:
        1. Look backwards from the 3-dart-average label.
        2. Find the nearest sensible player-name line.
        3. Read the first numeric value after that name as the remaining score.
        4. Read the following numeric values as sets/legs where applicable.
        """

        window_start = max(0, avg_index - 14)
        block = lines[window_start:avg_index]

        def is_number(value):
            try:
                int(str(value).strip())
                return True
            except (TypeError, ValueError):
                return False

        def is_checkout_token(value):
            value = str(value).strip().upper()

            if value in {"BULL", "DBULL", "BULLSEYE"}:
                return True

            # Dart notation such as T20, D16, S20.
            if re.match(r"^[TDS]\d{1,2}$", value):
                return True

            return False

        blocked_names = {
            "LEGS",
            "SETS",
            "CHECKOUT",
            "CHECKOUT RATE",
            "FIRST 9 AVG.",
            "3-DART AVG.",
            "BEST OF",
            "FIRST TO",
            "RACE TO",
        }

        name_index = None

        # Work backwards so we find the player identity nearest this stats block.
        for local_index in range(len(block) - 1, -1, -1):
            candidate = block[local_index].strip()
            upper = candidate.upper()

            if not candidate:
                continue

            if is_number(candidate):
                continue

            if is_checkout_token(candidate):
                continue

            if upper in blocked_names:
                continue

            if any(
                upper.startswith(prefix)
                for prefix in ("BEST OF ", "FIRST TO ", "RACE TO ")
            ):
                continue

            name_index = local_index
            break

        if name_index is None:
            return None

        name = block[name_index]

        numeric_values = []

        for value in block[name_index + 1:]:
            if is_number(value):
                numeric_values.append(int(value))

        if not numeric_values:
            return None

        # First number after the name is the remaining score.
        score = numeric_values[0]

        if not 0 <= score <= 501:
            return None

        if getattr(self.match, "is_set_play", False):
            sets = numeric_values[1] if len(numeric_values) >= 2 else 0
            legs = numeric_values[2] if len(numeric_values) >= 3 else 0
        else:
            sets = 0
            legs = numeric_values[1] if len(numeric_values) >= 2 else 0

        player = {
            "name": name,
            "score": score,
            "sets": sets,
            "legs": legs,
            "average": 0.0,
            "first9": 0.0,
            "checkout": 0.0,
        }

        if avg_index + 1 < len(lines):
            player["average"] = self._to_float(
                lines[avg_index + 1],
                0.0
            )

        block_end = len(lines)

        for i in range(avg_index + 1, len(lines)):
            if (
                i != avg_index
                and lines[i].lower() == "3-dart avg."
            ):
                block_end = i
                break

        for i in range(avg_index + 1, block_end):
            label = lines[i].lower()

            if label == "first 9 avg." and i + 1 < block_end:
                player["first9"] = self._to_float(
                    lines[i + 1],
                    0.0
                )

            elif label == "checkout rate" and i + 1 < block_end:
                player["checkout"] = self._to_float(
                    lines[i + 1],
                    0.0
                )

        return player

    # ======================================================

    @staticmethod
    def _valid_player_name(value):
        """
        DartCounter briefly reflows parts of its live page after some visits.
        During that transition the old positional parser can momentarily see
        a numeric score/leg value where the player name normally sits.

        Reject those transient frames rather than overwriting the last known
        good player name and score.
        """
        name = str(value).strip()

        if not name:
            return False

        # A genuine player name should not be only a number.
        if name.replace(".", "", 1).isdigit():
            return False

        blocked = {
            "0",
            "1",
            "2",
            "3-DART AVG.",
            "FIRST 9 AVG.",
            "CHECKOUT RATE",
            "LEGS",
            "SETS",
        }

        return name.upper() not in blocked

    def _parse_body_text(self, body_text):

        lines = self._clean_lines(body_text)

        if not lines:
            return False

        # Make sure this really looks like a DartCounter live match.
        if "3-dart avg." not in body_text:
            return False

        # ==========================================
        # Match Format
        # ==========================================

        format_lines = []

        for line in lines[:20]:
            if re.match(
                r"^(BEST OF|FIRST TO|RACE TO)\s+\d+\s+(LEGS?|SETS?)$",
                line,
                flags=re.IGNORECASE
            ):
                format_lines.append(line)

        if format_lines:
            self.match.match_format = " · ".join(format_lines)

        self.match.is_set_play = any(
            "SET" in line.upper()
            for line in format_lines
        )

        # ==========================================
        # Players
        # ==========================================

        average_indexes = [
            index
            for index, line in enumerate(lines)
            if line.lower() == "3-dart avg."
        ]

        players = []

        for avg_index in average_indexes[:2]:
            player = self._parse_player_from_average_label(
                lines,
                avg_index
            )

            if player:
                players.append(player)

        if len(players) < 2:
            return False

        player1 = players[0]
        player2 = players[1]

        # DartCounter can briefly redraw/reorder the score panel when a visit
        # is submitted (especially around large scores such as consecutive
        # 180s). If that transient frame makes a numeric value look like the
        # player name, ignore this refresh completely and keep the last valid
        # Match object. The next 250 ms update will normally contain the
        # settled DOM again.
        if (
            not self._valid_player_name(player1["name"])
            or not self._valid_player_name(player2["name"])
        ):
            return False

        self.match.player1_name = player1["name"]
        self.match.player1_score = player1["score"]
        self.match.player1_legs = player1["legs"]
        self.match.player1_sets = player1.get("sets", 0)
        self.match.player1_average = player1["average"]
        self.match.player1_first9 = player1["first9"]
        self.match.player1_checkout = player1["checkout"]

        self.match.player2_name = player2["name"]
        self.match.player2_score = player2["score"]
        self.match.player2_legs = player2["legs"]
        self.match.player2_sets = player2.get("sets", 0)
        self.match.player2_average = player2["average"]
        self.match.player2_first9 = player2["first9"]
        self.match.player2_checkout = player2["checkout"]

        self._update_180_events(
            self.match.player1_score,
            self.match.player2_score
        )

        return True

    def _update_180_events(self, player1_score, player2_score):
        """
        Detect submitted 180 visits from score deltas.

        This works for manual DartCounter entry as well as automatic scoring:
        a completed 180 visit changes a player's remaining score by 180.
        """
        current_scores = [player1_score, player2_score]

        for index, current in enumerate(current_scores):
            previous = self._previous_scores[index]

            if previous is not None and previous - current == 180:
                if index == 0:
                    self.match.player1_180_event += 1
                    print("DartCounter: Player 1 hit a 180.")
                else:
                    self.match.player2_180_event += 1
                    print("DartCounter: Player 2 hit a 180.")

            self._previous_scores[index] = current

    # ======================================================
    # Live Update
    # ======================================================

    def update(self):

        page = self._get_page()

        if page is None:
            return

        try:
            body_text = page.locator("body").inner_text(
                timeout=3000
            )

            parsed = self._parse_body_text(body_text)

            if not parsed:
                print("DartCounter: live match not detected yet.")

        except Exception as exc:
            print(f"DartCounter update error: {exc}")

    # ======================================================

    def get_match(self):

        return self.match

    # ======================================================

    def close(self):

        self.browser.close()