"""
IDL Live Suite
Header Widget
Version 3.0
"""

import customtkinter as ctk


class Header(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="#1A1A1A",
            corner_radius=0,
            height=70
        )

        self.pack_propagate(False)

        # -------------------------
        # Left - Title
        # -------------------------

        self.title = ctk.CTkLabel(
            self,
            text="🎯 IDL LIVE SUITE",
            font=("Segoe UI", 24, "bold"),
            text_color="white"
        )

        self.title.pack(
            side="left",
            padx=20
        )

        # -------------------------
        # Right - Provider
        # -------------------------

        self.provider = ctk.CTkLabel(
            self,
            text="SCOLIA",
            font=("Segoe UI", 18, "bold"),
            text_color="#d4af37"
        )

        self.provider.pack(
            side="right",
            padx=20
        )

    def update_provider(self, provider):

        self.provider.configure(
            text=provider.upper()
        )