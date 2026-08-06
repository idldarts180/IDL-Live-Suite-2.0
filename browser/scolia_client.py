"""
IDL Live Suite
Scolia Client
Version 1.2
"""

from playwright.sync_api import sync_playwright


class ScoliaClient:

    def __init__(self):

        self.playwright = None
        self.context = None
        self.page = None

        self.connect()

    def connect(self):

        self.playwright = sync_playwright().start()

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir="browser/profile",
            headless=False
        )

        # Reuse existing tab if one exists
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        # Always open Scolia
        self.page.goto(
            "https://game.scoliadarts.com/game",
            wait_until="domcontentloaded"
        )

        print("Connected to Scolia.")

    def wait_for_match(self):

        input("\nOpen your Scolia match then press ENTER...")

    def get_match_data(self):

        data = {
            "player1_name": "Player 1",
            "player2_name": "Player 2",
            "player1_score": 501,
            "player2_score": 501
        }

        # ---------------------------------
        # PLAYER NAMES
        # ---------------------------------

        try:

            names = self.page.locator("div.styles_nickname__uBJfP")

            if names.count() >= 2:

                data["player1_name"] = names.nth(0).inner_text().strip()
                data["player2_name"] = names.nth(1).inner_text().strip()

            else:
                print(f"WARNING: Found {names.count()} player names.")

        except Exception as e:

            print("Name Error:", e)

        # ---------------------------------
        # PLAYER SCORES
        # ---------------------------------

        try:

            scores = self.page.locator("span.styles_counter__ZHHHQ")

            if scores.count() >= 2:

                data["player1_score"] = int(
                    scores.nth(0).inner_text().strip()
                )

                data["player2_score"] = int(
                    scores.nth(1).inner_text().strip()
                )

            else:
                print(f"WARNING: Found {scores.count()} scores.")

        except Exception as e:

            print("Score Error:", e)

        return data

    def close(self):

        try:
            self.context.close()
        except:
            pass

        try:
            self.playwright.stop()
        except:
            pass


if __name__ == "__main__":

    client = ScoliaClient()

    client.wait_for_match()

    print()

    try:

        while True:

            match = client.get_match_data()

            print(match)

            command = input(
                "\nPress ENTER to refresh or type q to quit: "
            )

            if command.lower() == "q":
                break

    except KeyboardInterrupt:
        pass

    client.close()