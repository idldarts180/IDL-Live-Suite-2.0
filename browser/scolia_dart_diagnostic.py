"""
IDL Live Suite
Scolia Dart-by-Dart Diagnostic
Version 1.0

Purpose:
Capture what changes in Scolia after dart 1, dart 2 and dart 3
so the overlay can make checkout suggestions dart-aware.
"""

from playwright.sync_api import sync_playwright

SCOLIA_URL = "https://game.scoliadarts.com/game"
PROFILE_DIR = "browser/profile"


def clean_lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def print_changed_lines(before, after, label):
    before_lines = clean_lines(before)
    after_lines = clean_lines(after)

    print("\n" + "=" * 90)
    print(label)
    print("=" * 90)

    print("\nLINES ADDED / CHANGED:")
    for line in after_lines:
        if line not in before_lines:
            print(" +", line)

    print("\nLINES REMOVED:")
    for line in before_lines:
        if line not in after_lines:
            print(" -", line)


def candidate_elements(page):
    js = r"""
    () => {
        const selectors = [
            '[data-cy]',
            '[class*="dart" i]',
            '[class*="throw" i]',
            '[class*="visit" i]',
            '[class*="score" i]',
            '[id*="dart" i]',
            '[id*="throw" i]',
            '[id*="visit" i]',
            '[id*="score" i]'
        ];

        const seen = new Set();
        const out = [];

        for (const selector of selectors) {
            for (const el of document.querySelectorAll(selector)) {
                if (seen.has(el)) continue;
                seen.add(el);

                const text = (el.innerText || el.textContent || '').trim();
                const cls = typeof el.className === 'string' ? el.className : '';
                const id = el.id || '';
                const dataCy = el.getAttribute('data-cy') || '';

                if (!text && !cls && !id && !dataCy) continue;

                out.push({
                    tag: el.tagName,
                    id,
                    className: cls,
                    dataCy,
                    text: text.slice(0, 250)
                });
            }
        }

        return out.slice(0, 250);
    }
    """
    return page.evaluate(js)


def print_candidates(page, label):
    print("\n" + "-" * 90)
    print(f"{label} - CANDIDATE DART / THROW / VISIT / SCORE ELEMENTS")
    print("-" * 90)

    try:
        items = candidate_elements(page)
        for i, item in enumerate(items):
            print(
                f"[{i}] <{item['tag']}> "
                f"id={item['id']!r} "
                f"data-cy={item['dataCy']!r} "
                f"class={item['className']!r}"
            )
            if item["text"]:
                print("    TEXT:", item["text"].replace("\n", " | "))
    except Exception as exc:
        print("Could not inspect candidate elements:", exc)


def read_body(page):
    try:
        return page.locator("body").inner_text(timeout=5000)
    except Exception as exc:
        return f"<body read failed: {exc}>"


def main():
    print("\nSCOLIA DART-BY-DART DIAGNOSTIC\n")

    playwright = sync_playwright().start()

    context = playwright.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False
    )

    if context.pages:
        page = context.pages[0]
    else:
        page = context.new_page()

    page.goto(SCOLIA_URL, wait_until="domcontentloaded")

    print("Open a 501 Scolia game.")
    print("Get to the start of a fresh visit with 3 darts available.")
    input("\nWhen ready BEFORE throwing dart 1, press ENTER...")

    baseline = read_body(page)
    print_candidates(page, "BEFORE DART 1")

    input("\nTHROW DART 1, wait for Scolia to register it, then press ENTER...")
    dart1 = read_body(page)
    print_changed_lines(baseline, dart1, "AFTER DART 1")
    print_candidates(page, "AFTER DART 1")

    input("\nTHROW DART 2, wait for Scolia to register it, then press ENTER...")
    dart2 = read_body(page)
    print_changed_lines(dart1, dart2, "AFTER DART 2")
    print_candidates(page, "AFTER DART 2")

    input("\nTHROW DART 3, wait for Scolia to register it, then press ENTER...")
    dart3 = read_body(page)
    print_changed_lines(dart2, dart3, "AFTER DART 3")
    print_candidates(page, "AFTER DART 3")

    input("\nWhen the NEXT player's/new visit is visible, press ENTER...")
    next_visit = read_body(page)
    print_changed_lines(dart3, next_visit, "NEXT VISIT / TURN CHANGE")
    print_candidates(page, "NEXT VISIT / TURN CHANGE")

    print("\nDiagnostic complete.")
    input("Press ENTER to close...")

    context.close()
    playwright.stop()


if __name__ == "__main__":
    main()