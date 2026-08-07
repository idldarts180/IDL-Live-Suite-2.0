"""
IDL Live Suite
Score Circle Widget
Version 2.0
"""

import customtkinter as ctk


class ScoreCircle(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="transparent"
        )

        # ==========================
        # Player Name
        # ==========================

        self.player_name = ctk.CTkLabel(
            self,
            text="PLAYER",
            font=("Segoe UI", 20, "bold"),
            text_color="white"
        )

        self.player_name.pack(
            pady=(0, 12)
        )

        # ==========================
        # Score Circle
        # ==========================

        self.circle = ctk.CTkFrame(
            self,
            width=220,
            height=220,
            fg_color="#151515",
            border_width=8,
            border_color="#D4AF37",
            corner_radius=110
        )

        self.circle.pack()

        self.circle.pack_propagate(False)

        # ==========================
        # Score
        # ==========================

        self.score = ctk.CTkLabel(
            self.circle,
            text="501",
            font=("Segoe UI", 72, "bold"),
            text_color="white"
        )

        self.score.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

    def update_player(self, name, score):

        self.player_name.configure(
            text=name
        )

        self.score.configure(
            text=str(score)
        )