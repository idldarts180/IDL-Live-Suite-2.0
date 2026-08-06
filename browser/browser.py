"""
IDL Live Suite
Browser Engine v1.0
"""

from playwright.sync_api import sync_playwright


def main():

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir="browser/profile",
            headless=False
        )

        page = context.new_page()

        page.goto("https://game.scoliadarts.com/game")

        print("=" * 40)
        print("IDL LIVE SUITE")
        print("=" * 40)
        print()
        print("Log into Scolia if required.")
        print("This should only be needed the first time.")
        print()

        input("When you can see your match press ENTER...")

        print()
        print("Current page:")
        print(page.url)

        input("\nPress ENTER to close...")

        context.close()


if __name__ == "__main__":
    main()