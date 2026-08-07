"""
IDL Live Suite
Player Card Widget
Version 3.0
"""

import customtkinter as ctk


class PlayerCard(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="#242424",
            corner_radius=12,
            border_width=1,
            border_color="#3A3A3A"
        )

        # -------------------------
        # Player Name
        # -------------------------

        self.player_name = ctk.CTkLabel(
            self,
            text="PLAYER",
            font=("Segoe UI", 24, "bold"),
            anchor="w"
        )

        self.player_name.grid(
            row=0,
            column=0,
            padx=20,
            pady=(15, 5),
            sticky="w"
        )

        # -------------------------
        # Score
        # -------------------------

        self.score = ctk.CTkLabel(
            self,
            text="501",
            font=("Segoe UI", 48, "bold"),
            text_color="#d4af37"
        )

        self.score.grid(
            row=0,
            column=1,
            padx=20,
            pady=(10, 5),
            sticky="e"
        )

        # -------------------------
        # Average
        # -------------------------

        self.average = ctk.CTkLabel(
            self,
            text="Avg: 0.00",
            font=("Segoe UI", 18)
        )

        self.average.grid(
            row=1,
            column=0,
            padx=20,
            sticky="w"
        )

        # -------------------------
        # First 9
        # -------------------------

        self.first9 = ctk.CTkLabel(
            self,
            text="First 9: 0.00",
            font=("Segoe UI", 18)
        )

        self.first9.grid(
            row=2,
            column=0,
            padx=20,
            sticky="w"
        )

        # -------------------------
        # Checkout
        # -------------------------

        self.checkout = ctk.CTkLabel(
            self,
            text="Checkout: 0%",
            font=("Segoe UI", 18)
        )

        self.checkout.grid(
            row=3,
            column=0,
            padx=20,
            pady=(0, 15),
            sticky="w"
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

    def update_player(
        self,
        name,
        score,
        average,
        first9,
        checkout
    ):

        self.player_name.configure(text=name)

        self.score.configure(text=str(score))

        self.average.configure(
            text=f"Avg: {average:.2f}"
        )

        self.first9.configure(
            text=f"First 9: {first9:.2f}"
        )

        self.checkout.configure(
            text=f"Checkout: {checkout:.0f}%"
        )