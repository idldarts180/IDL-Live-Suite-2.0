import json
import os


class LayoutManager:

    def __init__(self):

        self.file = os.path.join(
            "ui",
            "config",
            "layout.json"
        )

        self.load()

    def load(self):

        with open(self.file, "r") as f:

            self.data = json.load(f)

    def save(self):

        with open(self.file, "w") as f:

            json.dump(
                self.data,
                f,
                indent=4
            )

    def get(self, name):

        return self.data[name]

    def set(self, name, x=None, y=None):

        if x is not None:
            self.data[name]["x"] = x

        if y is not None:
            self.data[name]["y"] = y