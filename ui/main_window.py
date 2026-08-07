"""
IDL Live Suite
Main Window
"""

import json
import subprocess
from pathlib import Path
import customtkinter as ctk

# main_window.py lives inside ui/
UI_DIR = Path(__file__).resolve().parent
CONFIG = UI_DIR / "config" / "banner.json"


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("IDL Live Suite")
        self.geometry("900x650")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")

        ctk.CTkLabel(
            self,
            text="IDL LIVE SUITE",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=(20, 10))

        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="Banner Text",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.banner = ctk.CTkEntry(frame, height=40)
        self.banner.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            frame,
            text="Apply Banner",
            command=self.save_banner
        ).pack(pady=(0, 15))

        ctk.CTkButton(
            self,
            text="Open Overlay",
            command=self.open_overlay,
            height=40
        ).pack(fill="x", padx=20)

        self.status = ctk.CTkLabel(self, text="Status: Ready")
        self.status.pack(side="bottom", pady=20)

        self.load_banner()

    def load_banner(self):
        CONFIG.parent.mkdir(exist_ok=True)

        if not CONFIG.exists():
            CONFIG.write_text(
                json.dumps({"text": ""}, indent=4),
                encoding="utf-8"
            )

        data = json.loads(CONFIG.read_text(encoding="utf-8"))

        self.banner.delete(0, "end")
        self.banner.insert(0, data.get("text", ""))

    def save_banner(self):
        CONFIG.parent.mkdir(exist_ok=True)

        data = {"text": self.banner.get()}

        CONFIG.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )

        self.status.configure(text="Status: Banner saved")

    def open_overlay(self):
        subprocess.Popen(
            ["python", "-m", "ui.broadcast_overlay"],
            cwd=UI_DIR.parent
        )
        self.status.configure(text="Status: Overlay opened")


if __name__ == "__main__":
    MainWindow().mainloop()