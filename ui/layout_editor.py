"""
IDL Live Suite
Layout Editor
"""

import tkinter as tk


class LayoutEditor:

    def __init__(self, overlay):

        self.overlay = overlay
        self.canvas = overlay.canvas
        self.layout = overlay.layout

        self.enabled = False
        self.selected = None
        self.selected_name = None
        self.outline = None

        self.canvas.bind("<Button-1>", self.click)

        overlay.bind("<Left>", lambda e: self.nudge(-1, 0, e))
        overlay.bind("<Right>", lambda e: self.nudge(1, 0, e))
        overlay.bind("<Up>", lambda e: self.nudge(0, -1, e))
        overlay.bind("<Down>", lambda e: self.nudge(0, 1, e))

        overlay.bind("<Control-s>", self.save)

    # =====================================================

    def toggle(self):

        self.enabled = not self.enabled

        print(
            "Layout Editor:",
            "ON" if self.enabled else "OFF"
        )

        if not self.enabled:

            self.selected = None
            self.selected_name = None

            if self.outline:

                self.canvas.delete(self.outline)
                self.outline = None

    # =====================================================

    def click(self, event):

        if not self.enabled:
            return

        item = self.canvas.find_closest(
            event.x,
            event.y
        )

        if not item:
            return

        self.selected = item[0]
        self.selected_name = None

        # Match the selected canvas item to its layout name
        for name, canvas_item in self.overlay.items.items():

            if canvas_item == self.selected:

                self.selected_name = name
                break

        self.draw_outline()

        if self.selected_name:

            print(f"Selected: {self.selected_name}")

    # =====================================================

    def draw_outline(self):

        if self.outline:

            self.canvas.delete(self.outline)

        if not self.selected:
            return

        bbox = self.canvas.bbox(self.selected)

        if not bbox:
            return

        x1, y1, x2, y2 = bbox

        self.outline = self.canvas.create_rectangle(

            x1 - 4,
            y1 - 4,
            x2 + 4,
            y2 + 4,

            outline="red",

            width=2,

            dash=(4, 2)

        )

    # =====================================================

    def nudge(self, dx, dy, event=None):

        if not self.enabled:
            return

        if not self.selected:
            return

        if event and (event.state & 0x1):

            dx *= 10
            dy *= 10

        self.canvas.move(
            self.selected,
            dx,
            dy
        )

        self.draw_outline()

    # =====================================================

    def save(self, event=None):

        if not self.enabled:
            return

        if not self.selected:
            print("Nothing selected.")
            return

        if not self.selected_name:
            print("Selected object cannot be saved.")
            return

        coords = self.canvas.coords(self.selected)

        if len(coords) < 2:
            print("Invalid coordinates.")
            return

        x = int(coords[0])
        y = int(coords[1])

        self.layout.set(
            self.selected_name,
            x=x,
            y=y
        )

        self.layout.save()

        print(f"{self.selected_name} saved at ({x}, {y})")