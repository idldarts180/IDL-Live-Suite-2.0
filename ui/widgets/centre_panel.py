"""
IDL Live Suite
Centre Panel Widget
Version 3.0
"""

import customtkinter as ctk
from PIL import Image


class CentrePanel(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="transparent"
        )

        # =====================================
        # Logo
        # =====================================

        logo = ctk.CTkImage(
            light_image=Image.open("assets/logos/idl.png"),
            dark_image=Image.open("assets/logos/idl.png"),
            size=(120, 120)
        )

        self.logo = ctk.CTkLabel(
            self,
            image=logo,
            text=""
        )

        self.logo.image = logo

        self.logo.pack(
            pady=(0, 15)
        )

        # =====================================
        # Match Score
        # =====================================

        self.match_score = ctk.CTkLabel(
            self,
            text="0 - 0",
            font=("Segoe UI", 40, "bold"),
            text_color="#D4AF37"
        )

        self.match_score.pack()

        # =====================================
        # Match Format
        # =====================================

        self.match_format = ctk.CTkLabel(
            self,
            text="501 • Race To 3 Legs • D-Out",
            font=("Segoe UI", 16),
            text_color="white"
        )

        self.match_format.pack(
            pady=(8, 20)
        )

        # =====================================
        # Competition Banner
        # =====================================

        self.banner = ctk.CTkFrame(
            self,
            fg_color="#D4AF37",
            corner_radius=12
        )

        self.banner.pack(
            fill="x",
            padx=10
        )

        self.competition = ctk.CTkLabel(
            self.banner,
            text="IDL EXHIBITION",
            font=("Segoe UI", 16, "bold"),
            text_color="black"
        )

        self.competition.pack(
            padx=20,
            pady=8
        )

    def update_match(
        self,
        left_legs,
        right_legs,
        match_format,
        competition
    ):

        self.match_score.configure(
            text=f"{left_legs} - {right_legs}"
        )

        self.match_format.configure(
            text=match_format
        )

        self.competition.configure(
            text=competition.upper()
        )