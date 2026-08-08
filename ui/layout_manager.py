"""
IDL Live Suite
Layout Manager
"""

import json

from ui.app_paths import (
    LAYOUT_FILE,
    ensure_runtime_files
)


class LayoutManager:

    def __init__(self):
        ensure_runtime_files()

        self.file = LAYOUT_FILE
        self.data = {}

        self.load()

    def load(self):
        with open(
            self.file,
            "r",
            encoding="utf-8"
        ) as f:
            self.data = json.load(f)

    def save(self):
        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.file,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                self.data,
                f,
                indent=4
            )

    def get(self, name):
        return self.data[name]

    def set(
        self,
        name,
        x=None,
        y=None
    ):
        if x is not None:
            self.data[name]["x"] = x

        if y is not None:
            self.data[name]["y"] = y