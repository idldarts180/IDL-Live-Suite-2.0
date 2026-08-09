"""
IDL Live Suite
Logo Badge
"""

from PIL import Image, ImageTk

from ui.layout_manager import LayoutManager
from ui.app_paths import LOGOS_DIR


class LogoBadge:

    def __init__(self, canvas):

        self.canvas = canvas

        self.layout = LayoutManager()

        image_path = LOGOS_DIR / "idl.png"

        self.image = Image.open(image_path)

        self.image.thumbnail(
            (100, 100),
            Image.LANCZOS
        )

        self.photo = ImageTk.PhotoImage(self.image)

    # ======================================================

    def draw(self):

        logo = self.layout.get("logo")

        item = self.canvas.create_image(
            logo["x"],
            logo["y"],
            image=self.photo,
            anchor="center",
            tags="logo"
        )

        return item