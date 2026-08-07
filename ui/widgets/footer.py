"""
IDL Live Suite
Footer Widget
Version 3.0
"""

import customtkinter as ctk


class Footer(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="#1A1A1A",
            corner_radius=0,
            height=40
        )

        self.pack_propagate(False)

        self.status = ctk.CTkLabel(
            self,
            text="🟢 LIVE",
            font=("Segoe UI", 16, "bold"),
            text_color="#4CAF50"
        )

        self.status.pack(
            side="left",
            padx=20
        )

        self.provider = ctk.CTkLabel(
            self,
            text="SCOLIA",
            font=("Segoe UI", 14),
            text_color="#BBBBBB"
        )

        self.provider.pack(
            side="right",
            padx=20
        )

    def update_footer(self, provider):

        self.provider.configure(
            text=provider.upper()
        )