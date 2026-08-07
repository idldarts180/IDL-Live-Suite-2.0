"""
IDL Live Suite
DartCounter Diagnostic Test
Version 2.0

Purpose:
- Open DartCounter using the existing persistent browser profile
- Inspect the main page and all frames
- Print visible text and useful diagnostics
"""

from playwright.sync_api import sync_playwright


DARTCOUNTER_URL = "https://app.dartcounter.net/dashboard"
PROFILE_DIR = "browser/dartcounter_profile"


def print_block(title, text):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    if text is None:
        print("<None>")
        return

    text = str(text).strip()

    if not text:
        print("<No visible text>")
    else:
        print(text)


def main():
    print("\nDARTCOUNTER DIAGNOSTIC TEST\n")

    playwright = sync_playwright().start()

    context = playwright.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False
    )

    if context.pages:
        page = context.pages[0]
    else:
        page = context.new_page()

    page.goto(
        DARTCOUNTER_URL,
        wait_until="domcontentloaded"
    )

    print("Log into DartCounter if required.")
    print("Open your LIVE match.")
    input("\nWhen the live match is fully visible, press ENTER...")

    print("\nCurrent URL:")
    print(page.url)

    # ======================================================
    # Main page
    # ======================================================

    try:
        body_text = page.locator("body").inner_text(timeout=5000)
    except Exception as exc:
        body_text = f"<Could not read body: {exc}>"

    print_block("MAIN PAGE BODY TEXT", body_text)

    # ======================================================
    # Frames
    # ======================================================

    print("\n" + "=" * 80)
    print(f"FRAME COUNT: {len(page.frames)}")
    print("=" * 80)

    for index, frame in enumerate(page.frames):
        print("\n" + "-" * 80)
        print(f"FRAME {index}")
        print("-" * 80)

        try:
            print("Name:", frame.name or "<no name>")
        except Exception:
            print("Name: <unavailable>")

        try:
            print("URL:", frame.url)
        except Exception:
            print("URL: <unavailable>")

        try:
            frame_text = frame.locator("body").inner_text(timeout=5000)
        except Exception as exc:
            frame_text = f"<Could not read frame body: {exc}>"

        print_block(f"FRAME {index} BODY TEXT", frame_text)

    # ======================================================
    # Element diagnostics
    # ======================================================

    selectors = [
        "iframe",
        "canvas",
        "button",
        "input",
        "[role='button']",
        "[class*='score']",
        "[class*='Score']",
        "[class*='player']",
        "[class*='Player']",
        "[class*='name']",
        "[class*='Name']",
        "[class*='counter']",
        "[class*='Counter']",
    ]

    print("\n" + "=" * 80)
    print("ELEMENT COUNTS")
    print("=" * 80)

    for selector in selectors:
        try:
            count = page.locator(selector).count()
            print(f"{selector}: {count}")
        except Exception as exc:
            print(f"{selector}: ERROR - {exc}")

    # ======================================================
    # HTML sample
    # ======================================================

    try:
        html = page.content()
        print_block(
            "MAIN PAGE HTML - FIRST 12000 CHARACTERS",
            html[:12000]
        )
    except Exception as exc:
        print_block(
            "MAIN PAGE HTML",
            f"<Could not read HTML: {exc}>"
        )

    input("\nPress ENTER to close...")

    try:
        context.close()
    except Exception:
        pass

    try:
        playwright.stop()
    except Exception:
        pass


if __name__ == "__main__":
    main()