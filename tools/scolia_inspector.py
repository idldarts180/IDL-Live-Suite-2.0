"""
IDL Live Suite
Scolia Inspector
Version 2.0
"""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.append(str(Path(__file__).resolve().parent.parent))

from providers.scolia import ScoliaProvider


def main():

    provider = ScoliaProvider()

    provider.connect()

    provider.wait_for_match()

    page = provider.browser.page

    print("\n" + "=" * 70)
    print("PLAYER NAMES")
    print("=" * 70)

    names = page.locator("div.styles_nickname__uBJfP")

    print(f"Found {names.count()} names\n")

    for i in range(names.count()):

        print(f"{i}: {names.nth(i).inner_text()}")

    print("\n" + "=" * 70)
    print("PLAYER SCORES")
    print("=" * 70)

    scores = page.locator("span.styles_counter__ZHHHQ")

    print(f"Found {scores.count()} scores\n")

    for i in range(scores.count()):

        print(f"{i}: {scores.nth(i).inner_text()}")

    print("\n" + "=" * 70)
    print("REALTIME STAT VALUES")
    print("=" * 70)

    stats = page.locator("span[data-cy^='realtimeStatsValue']")

    print(f"Found {stats.count()} values\n")

    for i in range(stats.count()):

        print(f"{i}: {stats.nth(i).inner_text()}")

    print("\nPress ENTER to close...")

    input()

    provider.close()


if __name__ == "__main__":

    main()