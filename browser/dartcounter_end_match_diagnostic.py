"""
IDL Live Suite
DartCounter End-of-Match Diagnostic
"""

import time
from browser.playwright import Browser


def snapshot(page, label):
    print("\n" + "=" * 100)
    print(label)
    print("=" * 100)

    try:
        print("URL:", page.url)
    except Exception:
        pass

    try:
        print("TITLE:", page.title())
    except Exception:
        pass

    try:
        body = page.locator("body").inner_text(timeout=3000)
    except Exception as exc:
        print("Could not read body:", exc)
        return ""

    print("\nBODY TEXT:\n")
    print(body)
    return body


def main():
    print("\nDARTCOUNTER END-OF-MATCH DIAGNOSTIC\n")

    browser = Browser(
        profile="browser/dartcounter_profile",
        url="https://app.dartcounter.net/dashboard"
    )

    browser.connect()

    page = browser.page

    print(
        "Start a very short DartCounter match (Race to 1 is ideal).\n"
        "Get one player onto a checkout, but DO NOT finish the match yet."
    )

    input("\nWhen you are ready BEFORE the match-winning visit, press ENTER...")

    before = snapshot(page, "BEFORE MATCH WIN")

    print(
        "\nNow finish the match. Do not click anything after the winning score.\n"
        "The script will watch the page for 8 seconds."
    )

    input("Press ENTER immediately before entering/throwing the winning score...")

    last_body = before
    last_url = page.url

    for i in range(80):
        time.sleep(0.1)

        try:
            current_url = page.url
        except Exception:
            current_url = ""

        try:
            current_body = page.locator("body").inner_text(timeout=1000)
        except Exception:
            current_body = ""

        if current_url != last_url or current_body != last_body:
            print("\n" + "-" * 100)
            print(f"CHANGE DETECTED at {i / 10:.1f}s")
            print("-" * 100)
            print("URL:", current_url)
            print("\nBODY TEXT:\n")
            print(current_body)

            last_url = current_url
            last_body = current_body

    snapshot(page, "FINAL PAGE AFTER MATCH")

    input("\nPress ENTER to close...")
    browser.close()


if __name__ == "__main__":
    main()