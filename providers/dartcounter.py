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

        if avg_index < 3:
            return None

        player = {
            "name": lines[avg_index - 3],
            "score": self._to_int(lines[avg_index - 2], 501),
            "legs": self._to_int(lines[avg_index - 1], 0),
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

        for line in lines[:12]:
            if re.match(
                r"^(BEST OF|FIRST TO|RACE TO)\s+\d+\s+LEGS?$",
                line,
                flags=re.IGNORECASE
            ):
                self.match.match_format = line
                break

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

        self.match.player1_name = player1["name"]
        self.match.player1_score = player1["score"]
        self.match.player1_legs = player1["legs"]
        self.match.player1_average = player1["average"]
        self.match.player1_first9 = player1["first9"]
        self.match.player1_checkout = player1["checkout"]

        self.match.player2_name = player2["name"]
        self.match.player2_score = player2["score"]
        self.match.player2_legs = player2["legs"]
        self.match.player2_average = player2["average"]
        self.match.player2_first9 = player2["first9"]
        self.match.player2_checkout = player2["checkout"]

        return True

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