"""
IDL Live Suite
Scolia Inspector
Version 3.0
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

    print("\n" + "=" * 80)
    print("PLAYER NAMES")
    print("=" * 80)

    try:

        names = page.locator("div.styles_nickname__uBJfP")

        print(f"Found {names.count()} names\n")

        for i in range(names.count()):

            print(f"{i}: {names.nth(i).inner_text()}")

    except Exception as e:

        print(e)

    print("\n" + "=" * 80)
    print("PLAYER SCORES")
    print("=" * 80)

    try:

        scores = page.locator("span.styles_counter__ZHHHQ")

        print(f"Found {scores.count()} scores\n")

        for i in range(scores.count()):

            print(f"{i}: {scores.nth(i).inner_text()}")

    except Exception as e:

        print(e)

    print("\n" + "=" * 80)
    print("REALTIME STAT VALUES")
    print("=" * 80)

    try:

        values = page.locator("span[data-cy^='realtimeStatsValue_']")

        print(f"Found {values.count()} values\n")

        for i in range(values.count()):

            print(f"{i}: {values.nth(i).inner_text()}")

    except Exception as e:

        print(e)

    print("\n" + "=" * 80)
    print("LEGS HTML")
    print("=" * 80)

    try:

        legs = page.locator("text=LEGS")

        print(f"Found {legs.count()} LEGS labels\n")

        for i in range(legs.count()):

            print("=" * 80)
            print(f"LEGS #{i}")
            print("=" * 80)

            try:

                html = legs.nth(i).evaluate(
                    "(e) => e.parentElement.outerHTML"
                )

                print(html)

            except Exception as err:

                print(err)

            print()

    except Exception as e:

        print(e)

    input("\nPress ENTER to close...")

    provider.close()


if __name__ == "__main__":

    main()