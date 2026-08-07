"""
IDL Live Suite
Main Window
"""

import json
import subprocess
import sys
from pathlib import Path

import customtkinter as ctk


# main_window.py lives inside ui/
UI_DIR = Path(__file__).resolve().parent
PROJECT_DIR = UI_DIR.parent
CONFIG = UI_DIR / "config" / "banner.json"


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("IDL Live Suite")
        self.geometry("900x650")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")

        self.overlay_process = None

        # ==========================================
        # Title
        # ==========================================

        ctk.CTkLabel(
            self,
            text="IDL LIVE SUITE",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=(20, 10))

        # ==========================================
        # Match Banner
        # ==========================================

        banner_frame = ctk.CTkFrame(self)
        banner_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            banner_frame,
            text="Match Banner",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.banner = ctk.CTkEntry(
            banner_frame,
            height=40,
            placeholder_text="e.g. IDL World Championship - Round 3"
        )
        self.banner.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkButton(
            banner_frame,
            text="Apply Banner",
            command=self.save_banner,
            height=36
        ).pack(pady=(0, 15))

        # ==========================================
        # Scolia
        # ==========================================

        scolia_frame = ctk.CTkFrame(self)
        scolia_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            scolia_frame,
            text="Scolia",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            scolia_frame,
            text=(
                "Open the live overlay to start the existing Scolia browser "
                "connection and live scoring."
            ),
            font=("Segoe UI", 13)
        ).pack(anchor="w", padx=15, pady=(0, 10))

        self.scolia_status = ctk.CTkLabel(
            scolia_frame,
            text="Status: Ready"
        )
        self.scolia_status.pack(anchor="w", padx=15, pady=(0, 10))

        ctk.CTkButton(
            scolia_frame,
            text="Open Scolia Live Overlay",
            command=self.open_overlay,
            height=42
        ).pack(fill="x", padx=15, pady=(0, 15))

        # ==========================================
        # Broadcast
        # ==========================================

        broadcast_frame = ctk.CTkFrame(self)
        broadcast_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            broadcast_frame,
            text="Broadcast",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkButton(
            broadcast_frame,
            text="Open Overlay",
            command=self.open_overlay,
            height=42
        ).pack(fill="x", padx=15, pady=(5, 15))

        # ==========================================
        # Overall Status
        # ==========================================

        self.status = ctk.CTkLabel(
            self,
            text="Status: Ready"
        )
        self.status.pack(side="bottom", pady=20)

        self.load_banner()

    # ======================================================
    # Banner
    # ======================================================

    def load_banner(self):
        CONFIG.parent.mkdir(parents=True, exist_ok=True)

        if not CONFIG.exists():
            CONFIG.write_text(
                json.dumps({"text": ""}, indent=4),
                encoding="utf-8"
            )

        try:
            data = json.loads(
                CONFIG.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            data = {"text": ""}

        self.banner.delete(0, "end")
        self.banner.insert(0, data.get("text", ""))

    def save_banner(self):
        CONFIG.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "text": self.banner.get().strip()
        }

        CONFIG.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )

        self.status.configure(
            text="Status: Banner saved"
        )

    # ======================================================
    # Overlay / Scolia
    # ======================================================

    def open_overlay(self):
        """
        The broadcast overlay owns the MatchController and therefore owns
        the single Scolia Playwright/browser connection.

        Keeping that connection in one process avoids launching competing
        persistent Chrome sessions against the same browser profile.
        """

        if (
            self.overlay_process is not None
            and self.overlay_process.poll() is None
        ):
            self.status.configure(
                text="Status: Overlay is already open"
            )
            self.scolia_status.configure(
                text="Status: Scolia overlay running"
            )
            return

        try:
            self.overlay_process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "ui.broadcast_overlay"
                ],
                cwd=PROJECT_DIR
            )

            self.status.configure(
                text="Status: Overlay opened"
            )

            self.scolia_status.configure(
                text="Status: Connecting through live overlay..."
            )

            self.after(1500, self.check_overlay)

        except Exception as exc:
            self.status.configure(
                text=f"Status: Could not open overlay - {exc}"
            )

            self.scolia_status.configure(
                text="Status: Connection failed"
            )

    def check_overlay(self):
        if self.overlay_process is None:
            return

        return_code = self.overlay_process.poll()

        if return_code is None:
            self.scolia_status.configure(
                text="Status: Scolia / overlay running"
            )
            self.status.configure(
                text="Status: Live overlay running"
            )
        else:
            self.scolia_status.configure(
                text=f"Status: Overlay stopped (code {return_code})"
            )
            self.status.configure(
                text="Status: Overlay closed"
            )


if __name__ == "__main__":
    MainWindow().mainloop()