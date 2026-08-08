"""
IDL Live Suite
Result Celebration Visuals
LEG WIN / SET WIN / WINNER
"""

from pathlib import Path

from PIL import Image, ImageTk


PROJECT_DIR = Path(__file__).resolve().parents[2]
EFFECTS_DIR = PROJECT_DIR / "assets" / "effects"


class ResultCelebration:

    FILES = {
        "leg": EFFECTS_DIR / "leg_win.png",
        "set": EFFECTS_DIR / "set_win.png",
        "winner": EFFECTS_DIR / "winner.png",
    }

    # Maximum display boxes inside one player circle.
    NORMAL_BOX = {
        "leg": (142, 128),
        "set": (142, 128),
        "winner": (150, 105),
    }

    LARGE_BOX = {
        "leg": (154, 139),
        "set": (154, 139),
        "winner": (164, 115),
    }

    def __init__(self, canvas):
        self.canvas = canvas
        self.item = None
        self.images = {}

        for kind, path in self.FILES.items():
            source = Image.open(path).convert("RGBA")

            self.images[(kind, "normal")] = ImageTk.PhotoImage(
                self._fit(source, *self.NORMAL_BOX[kind])
            )

            self.images[(kind, "large")] = ImageTk.PhotoImage(
                self._fit(source, *self.LARGE_BOX[kind])
            )

    @staticmethod
    def _fit(image, max_width, max_height):
        copy = image.copy()
        copy.thumbnail(
            (max_width, max_height),
            Image.Resampling.LANCZOS
        )
        return copy

    def draw(self, x, y):
        self.item = self.canvas.create_image(
            x,
            y,
            image=self.images[("leg", "normal")],
            anchor="center",
            state="hidden",
            tags="result_celebration"
        )
        return self.item

    def show(self, kind):
        if self.item is None:
            return

        self.canvas.itemconfigure(
            self.item,
            image=self.images[(kind, "normal")],
            state="normal"
        )
        self.canvas.tag_raise(self.item)

    def set_large(self, kind):
        if self.item is None:
            return

        self.canvas.itemconfigure(
            self.item,
            image=self.images[(kind, "large")]
        )

    def set_normal(self, kind):
        if self.item is None:
            return

        self.canvas.itemconfigure(
            self.item,
            image=self.images[(kind, "normal")]
        )

    def hide(self):
        if self.item is not None:
            self.canvas.itemconfigure(
                self.item,
                state="hidden"
            )