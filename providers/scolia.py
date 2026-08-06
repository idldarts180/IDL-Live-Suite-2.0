"""
IDL Live Suite
Scolia Provider
Version 2.0
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

        self.browser = Browser(
            profile="browser/profile",
            url="https://game.scoliadarts.com/game"
        )

    def connect(self):

        self.browser.connect()

        print("Connected to Scolia.")

    def wait_for_match(self):

        input("\nOpen your Scolia match then press ENTER...")

    def update(self):

        page = self.browser.page

        try:

            names = page.locator("div.styles_nickname__uBJfP")

            if names.count() >= 2:

                self.match.player1_name = names.nth(0).inner_text().strip()
                self.match.player2_name = names.nth(1).inner_text().strip()

        except Exception:
            pass

        try:

            scores = page.locator("span.styles_counter__ZHHHQ")

            if scores.count() >= 2:

                self.match.player1_score = int(
                    scores.nth(0).inner_text().strip()
                )

                self.match.player2_score = int(
                    scores.nth(1).inner_text().strip()
                )

        except Exception:
            pass

    def get_match(self):

        return self.match

    def close(self):

        self.browser.close()