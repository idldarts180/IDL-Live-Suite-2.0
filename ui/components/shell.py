"""
IDL Live Suite
Broadcast Shell
"""

import os
from PIL import Image, ImageTk


class Shell:

    def __init__(self, canvas):

        self.canvas = canvas

        image_path = os.path.join(
            "assets",
            "overlays",
            "broadcast_shell.png"
        )

        # Load the image at its ACTUAL size
        self.image = Image.open(image_path)

        self.photo = ImageTk.PhotoImage(self.image)

    def draw(self):

        # Centre a 1080x400 shell inside a 1200x420 window
        self.canvas.create_image(
            60,   # (1200 - 1080) / 2
            10,   # (420 - 400) / 2
            anchor="nw",
            image=self.photo,
            tags="shell"
        )