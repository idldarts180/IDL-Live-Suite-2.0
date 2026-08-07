"""
IDL Live Suite
Broadcast Overlay
Version 3.0
"""

import customtkinter as ctk

from ui.widgets.score_circle import ScoreCircle
from ui.widgets.centre_panel import CentrePanel
from models.match import Match


class Overlay(ctk.CTk):

    def __init__(self):

        super().__init__()

        ctk.set_appearance_mode("dark")

        self.title("IDL Broadcast Overlay")

        self.geometry("980x340")

        self.configure(
            fg_color="#101010"
        )

        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self.left = ScoreCircle(self)

        self.left.grid(
            row=0,
            column=0,
            padx=15,
            pady=25
        )

        self.centre = CentrePanel(self)

        self.centre.grid(
            row=0,
            column=1,
            padx=10
        )

        self.right = ScoreCircle(self)

        self.right.grid(
            row=0,
            column=2,
            padx=15,
            pady=25
        )

    def update_match(self, match):

        self.left.update_player(
            match.player1_name,
            match.player1_score
        )

        self.right.update_player(
            match.player2_name,
            match.player2_score
        )

        self.centre.update_match(
            match.player1_legs,
            match.player2_legs,
            match.match_format,
            match.competition
        )


if __name__ == "__main__":

    match = Match()

    app = Overlay()

    app.update_match(match)

    app.mainloop()