from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()

context = playwright.chromium.launch_persistent_context(
    user_data_dir="browser/dartcounter_profile",
    headless=False
)

if context.pages:
    page = context.pages[0]
else:
    page = context.new_page()

page.goto(
    "https://app.dartcounter.net/dashboard",
    wait_until="domcontentloaded"
)

print("=" * 50)
print("DARTCOUNTER TEST")
print("=" * 50)
print()
print("Log into DartCounter if required.")
print("Open your LIVE match.")
input("\nWhen your live match is visible press ENTER...")

print("\nCurrent URL:")
print(page.url)

print("\nSearching page...\n")

print("=" * 80)
print(page.locator("body").inner_text())
print("=" * 80)

input("\nPress ENTER to close...")

context.close()
playwright.stop()