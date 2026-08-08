"""
IDL Live Suite
180 Celebration Visual
"""

from pathlib import Path

from PIL import Image, ImageTk


PROJECT_DIR = Path(__file__).resolve().parents[2]
IMAGE_FILE = PROJECT_DIR / "assets" / "effects" / "180.png"


class Celebration180:

    def __init__(self, canvas):
        self.canvas = canvas
        self.item = None

        source = Image.open(IMAGE_FILE).convert("RGBA")

        # Three frames give the graphic a quick broadcast-style punch:
        # normal -> slightly larger -> normal.
        self.images = {
            "normal": ImageTk.PhotoImage(
                source.resize((150, 104), Image.Resampling.LANCZOS)
            ),
            "large": ImageTk.PhotoImage(
                source.resize((166, 115), Image.Resampling.LANCZOS)
            ),
        }

    def draw(self, x, y):
        self.item = self.canvas.create_image(
            x,
            y,
            image=self.images["normal"],
            anchor="center",
            state="hidden",
            tags="celebration180"
        )

        return self.item

    def show(self):
        if self.item is None:
            return

        self.canvas.itemconfigure(
            self.item,
            image=self.images["normal"],
            state="normal"
        )

        # Keep celebration above the regular score text.
        self.canvas.tag_raise(self.item)

    def set_large(self):
        if self.item is None:
            return

        self.canvas.itemconfigure(
            self.item,
            image=self.images["large"]
        )

    def set_normal(self):
        if self.item is None:
            return

        self.canvas.itemconfigure(
            self.item,
            image=self.images["normal"]
        )

    def hide(self):
        if self.item is None:
            return

        self.canvas.itemconfigure(
            self.item,
            state="hidden"
        )