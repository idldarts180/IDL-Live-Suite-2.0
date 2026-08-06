from browser.scolia_client import ScoliaClient

client = ScoliaClient()

client.wait_for_match()

page = client.page

print("\nSearching page text...\n")

body = page.locator("body").inner_text()

print(body)

print("\n")

search = input("Type the EXACT player name shown on screen: ")

locator = page.locator(f"text={search}")

print(f"\nFound {locator.count()} matching element(s).\n")

for i in range(locator.count()):

    item = locator.nth(i)

    print("=" * 60)

    print(
        item.evaluate(
            """el => ({
                tag: el.tagName,
                className: el.className,
                html: el.outerHTML
            })"""
        )
    )

input("\nPress ENTER to close...")

client.close()