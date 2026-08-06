"""
IDL Live Suite
Version 0.8.0

vision/ocr.py
"""

import easyocr
import re

reader = easyocr.Reader(["en"], gpu=False)


def read_scores(image_path):

    results = reader.readtext(image_path)

    player1 = None
    player2 = None

    for result in results:

        box = result[0]
        text = result[1]

        numbers = re.findall(r"\d+", text)

        if not numbers:
            continue

        value = int(numbers[0])

        if value > 501:
            continue

        x = sum(point[0] for point in box) / 4
        y = sum(point[1] for point in box) / 4

        # Score height
        if not (500 <= y <= 850):
            continue

        # LEFT SCORE
        if 250 <= x <= 700:
            player1 = value

        # RIGHT SCORE
        elif 900 <= x <= 1500:
            player2 = value

    if player1 is None:
        player1 = 0

    if player2 is None:
        player2 = 0

    return player1, player2