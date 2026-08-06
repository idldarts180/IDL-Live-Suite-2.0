"""
IDL Live Suite
Version 1.0.0

capture/capture.py
"""

import os

import mss
from PIL import Image
import win32gui


CAPTURE_FOLDER = "capture"
LATEST_IMAGE = os.path.join(CAPTURE_FOLDER, "latest.png")

WINDOW_TITLE = "Scolia Web Client"


def find_scolia_window():

    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)

    if hwnd == 0:
        return None

    return hwnd


def get_client_rect(hwnd):

    left, top, right, bottom = win32gui.GetClientRect(hwnd)

    x1, y1 = win32gui.ClientToScreen(hwnd, (left, top))
    x2, y2 = win32gui.ClientToScreen(hwnd, (right, bottom))

    return {
        "left": x1,
        "top": y1,
        "width": x2 - x1,
        "height": y2 - y1,
    }


def capture_screen():

    os.makedirs(CAPTURE_FOLDER, exist_ok=True)

    hwnd = find_scolia_window()

    if hwnd is None:
        print("❌ Scolia Web Client not found.")
        return False

    rect = get_client_rect(hwnd)

    with mss.mss() as sct:

        img = sct.grab(rect)

        image = Image.frombytes(
            "RGB",
            img.size,
            img.rgb
        )

        image.save(LATEST_IMAGE)

    print(f"✅ Saved {LATEST_IMAGE}")

    return True


if __name__ == "__main__":
    capture_screen()