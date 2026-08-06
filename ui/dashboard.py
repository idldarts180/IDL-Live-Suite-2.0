"""
IDL Live Suite
Dashboard
Version 2.0
"""

import customtkinter as ctk


class Dashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("IDL Live Suite")
        self.geometry("900x500")
        self.resizable(False, False)

        # ----------------------------
        # Title
        # ----------------------------

        title = ctk.CTkLabel(
            self,
            text="🎯 IDL LIVE SUITE",
            font=("Segoe UI", 28, "bold")
        )
        title.pack(pady=20)

        # ----------------------------
        # Main Frame
        # ----------------------------

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ============================
        # PLAYER 1
        # ============================

        self.player1_name = ctk.CTkLabel(
            self.main_frame,
            text="Player 1",
            font=("Segoe UI", 24, "bold")
        )
        self.player1_name.pack(pady=(30, 5))

        self.player1_score = ctk.CTkLabel(
            self.main_frame,
            text="501",
            font=("Segoe UI", 64, "bold")
        )
        self.player1_score.pack()

        # ============================
        # PLAYER 2
        # ============================

        self.player2_name = ctk.CTkLabel(
            self.main_frame,
            text="Player 2",
            font=("Segoe UI", 24, "bold")
        )
        self.player2_name.pack(pady=(30, 5))

        self.player2_score = ctk.CTkLabel(
            self.main_frame,
            text="501",
            font=("Segoe UI", 64, "bold")
        )
        self.player2_score.pack()

        # ----------------------------
        # Status
        # ----------------------------

        self.status = ctk.CTkLabel(
            self,
            text="Waiting for provider...",
            font=("Segoe UI", 16)
        )

        self.status.pack(pady=15)

    # ======================================================

    def update_match(self, match):

        self.player1_name.configure(
            text=match.player1_name
        )

        self.player2_name.configure(
            text=match.player2_name
        )

        self.player1_score.configure(
            text=str(match.player1_score)
        )

        self.player2_score.configure(
            text=str(match.player2_score)
        )

        self.status.configure(
            text=f"🟢 LIVE • {match.provider}"
        )