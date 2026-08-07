"""
IDL Live Suite
Logo Badge
"""

import os
from PIL import Image, ImageTk

from ui.layout_manager import LayoutManager


class LogoBadge:

    def __init__(self, canvas):

        self.canvas = canvas

        self.layout = LayoutManager()

        image_path = os.path.join(
            "assets",
            "logos",
            "idl.png"
        )

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