"""IDL Live Suite - Checkout Text"""

try:
    from ui.theme import GOLD
except ImportError:
    GOLD = "#C8A44D"


class CheckoutText:

    def __init__(self, canvas):
        self.canvas = canvas
        self.item = None

    def draw(self, x, y, route=""):
        self.item = self.canvas.create_text(
            x,
            y,
            text=route,
            fill=GOLD,
            font=("Segoe UI", 12, "bold"),
            anchor="center",
            tags="checkout"
        )
        return self.item

    def update(self, route):
        if self.item is not None:
            self.canvas.itemconfigure(
                self.item,
                text=route or ""
            )