"""
IDL Live Suite
Player Name
Smart single-line / compact stacked name layout
"""

import tkinter.font as tkfont

from ui.theme import *


class PlayerName:

    def __init__(self, canvas):
        self.canvas = canvas

        self.single_line_width = 125
        self.two_line_width = 190

        self.max_font_size = 17
        self.min_font_size = 11

        self.item = None
        self.second_item = None

        self.x = 0
        self.y = 0

    # ======================================================

    @staticmethod
    def _clean_name(name):
        return " ".join(str(name or "").strip().split())

    # ======================================================

    @staticmethod
    def _make_font(size):
        return tkfont.Font(
            family="Segoe UI",
            size=size,
            weight="bold"
        )

    # ======================================================

    def _measure(self, text, size):
        return self._make_font(size).measure(text)

    # ======================================================

    def _best_two_line_split(self, name, size):
        words = name.split()

        if len(words) < 2:
            return None

        font = self._make_font(size)
        candidates = []

        for split_at in range(1, len(words)):
            top = " ".join(words[:split_at])
            bottom = " ".join(words[split_at:])

            top_width = font.measure(top)
            bottom_width = font.measure(bottom)

            candidates.append(
                (
                    max(top_width, bottom_width),
                    abs(top_width - bottom_width),
                    top,
                    bottom
                )
            )

        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][2], candidates[0][3]

    # ======================================================

    def _layout_name(self, name):
        name = self._clean_name(name)

        if not name:
            return ("", None, self.max_font_size)

        if self._measure(name, self.max_font_size) <= self.single_line_width:
            return (name, None, self.max_font_size)

        if len(name.split()) >= 2:
            for size in range(
                self.max_font_size,
                self.min_font_size - 1,
                -1
            ):
                split = self._best_two_line_split(name, size)

                if split is None:
                    continue

                top, bottom = split

                if (
                    self._measure(top, size) <= self.two_line_width
                    and self._measure(bottom, size) <= self.two_line_width
                ):
                    return (top, bottom, size)

        for size in range(
            self.max_font_size - 1,
            7,
            -1
        ):
            if self._measure(name, size) <= self.two_line_width:
                return (name, None, size)

        return (name, None, 8)

    # ======================================================

    def draw(self, x, y, name):
        self.x = x
        self.y = y

        top, bottom, size = self._layout_name(name)

        self.item = self.canvas.create_text(
            x,
            y,
            text=top,
            fill=GOLD,
            font=("Segoe UI", size, "bold"),
            anchor="center",
            tags="player"
        )

        self.second_item = self.canvas.create_text(
            x,
            y,
            text="",
            fill=GOLD,
            font=("Segoe UI", size, "bold"),
            anchor="center",
            tags="player"
        )

        self._apply_layout(top, bottom, size)

        return self.item

    # ======================================================

    def _apply_layout(self, top, bottom, size):
        if self.item is None:
            return

        font = ("Segoe UI", size, "bold")

        if bottom is None:
            self.canvas.itemconfigure(
                self.item,
                text=top,
                font=font
            )
            self.canvas.coords(
                self.item,
                self.x,
                self.y
            )

            if self.second_item is not None:
                self.canvas.itemconfigure(
                    self.second_item,
                    text=""
                )

            return

        # Two separate canvas text items give us precise control over the
        # vertical gap. Keep the pair tightly centred around the original y.
        line_gap = max(20, int(size * 1.22))

        self.canvas.itemconfigure(
            self.item,
            text=top,
            font=font
        )
        self.canvas.coords(
            self.item,
            self.x,
            self.y - (line_gap / 2)
        )

        self.canvas.itemconfigure(
            self.second_item,
            text=bottom,
            font=font
        )
        self.canvas.coords(
            self.second_item,
            self.x,
            self.y + (line_gap / 2)
        )

    # ======================================================

    def update(self, name):
        if self.item is None:
            return

        top, bottom, size = self._layout_name(name)
        self._apply_layout(top, bottom, size)