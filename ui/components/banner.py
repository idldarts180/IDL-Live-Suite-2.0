"""
IDL Live Suite
Banner Component
"""

import json

from ui.app_paths import (
    BANNER_FILE,
    ensure_runtime_files
)
from ui.layout_manager import LayoutManager


class Banner:

    def __init__(self, canvas):
        ensure_runtime_files()

        self.canvas = canvas
        self.layout = LayoutManager()
        self.item = None

    def load_text(self):
        try:
            with open(
                BANNER_FILE,
                "r",
                encoding="utf-8"
            ) as f:
                return json.load(f).get(
                    "text",
                    ""
                )
        except Exception:
            return ""

    def draw(self):
        pos = self.layout.get("banner")

        self.item = self.canvas.create_text(
            pos["x"],
            pos["y"],
            text=self.load_text(),
            fill="black",
            font=("Segoe UI", 16, "bold"),
            anchor="center",
            width=420,
            tags="banner"
        )

        return self.item

    def refresh(self):
        if self.item:
            self.canvas.itemconfigure(
                self.item,
                text=self.load_text()
            )