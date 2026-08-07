"""
IDL Live Suite
Dashboard
Version 3.0
"""

import customtkinter as ctk

from ui.widgets.header import Header
from ui.widgets.player_card import PlayerCard
from ui.widgets.footer import Footer


class Dashboard(ctk.CTk):

    def __init__(self):

        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("IDL Live Suite")

        self.geometry("1000x700")

        self.minsize(900, 650)

        self.configure(fg_color="#121212")

        # ==========================================
        # Header
        # ==========================================

        self.header = Header(self)
        self.header.pack(fill="x")

        # ==========================================
        # Main Content
        # ==========================================

        self.content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # ==========================================
        # Player 1
        # ==========================================

        self.player1 = PlayerCard(self.content)

        self.player1.pack(
            fill="x",
            pady=(0, 20)
        )

        # ==========================================
        # Player 2
        # ==========================================

        self.player2 = PlayerCard(self.content)

        self.player2.pack(
            fill="x"
        )

        # ==========================================
        # Footer
        # ==========================================

        self.footer = Footer(self)

        self.footer.pack(
            fill="x",
            side="bottom"
        )

    # ==================================================

    def update_match(self, match):

        self.header.update_provider(
            match.provider
        )

        self.footer.update_footer(
            match.provider
        )

        self.player1.update_player(

            match.player1_name,

            match.player1_score,

            match.player1_average,

            match.player1_first9,

            match.player1_checkout

        )

        self.player2.update_player(

            match.player2_name,

            match.player2_score,

            match.player2_average,

            match.player2_first9,

            match.player2_checkout

        )