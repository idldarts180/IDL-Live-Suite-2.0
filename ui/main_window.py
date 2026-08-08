"""
IDL Live Suite
Main Window
Version 3.0 - Branded Control Centre
"""

import json
import subprocess
import sys
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from ui.app_paths import (
    BANNER_FILE,
    LOGOS_DIR,
    ICONS_DIR,
    ensure_runtime_files
)


UI_DIR = Path(__file__).resolve().parent
PROJECT_DIR = UI_DIR.parent

IDL_LOGO = LOGOS_DIR / "idl.png"
SCOLIA_LOGO = LOGOS_DIR / "scolia.png"
DARTCOUNTER_LOGO = LOGOS_DIR / "dartcounter.png"
APP_ICON = ICONS_DIR / "idl_live_suite.ico"

APP_BG = "#0B0B0B"
PANEL_BG = "#141414"
PANEL_ALT = "#181818"
BORDER = "#2A2A2A"
GOLD = "#a5893c"
GOLD_HOVER = "#8f7633"
WHITE = "#F5F5F5"
MUTED = "#9C9C9C"
READY = "#AFAFAF"
CONNECTING = "#D2A83A"
LIVE = "#55C271"
ERROR = "#E25C5C"
SCOLIA_GREEN = "#35B86B"
DARTCOUNTER_RED = "#FF5638"


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        if APP_ICON.exists():
            try:
                self.iconbitmap(str(APP_ICON))
            except Exception:
                pass

        ensure_runtime_files()

        self.title("IDL Live Suite")
        self.geometry("1040x780")
        self.resizable(False, False)
        self.configure(fg_color=APP_BG)
        ctk.set_appearance_mode("dark")

        self.overlay_process = None
        self.active_provider = None

        self.idl_logo_image = None
        self.scolia_logo_image = None
        self.dartcounter_logo_image = None

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=28, pady=22)

        self._build_header()
        self._build_banner()
        self._build_providers()
        self._build_status_bar()

        self.load_banner()

    # ======================================================
    # UI BUILDERS
    # ======================================================

    def _build_header(self):
        frame = ctk.CTkFrame(
            self.main,
            fg_color=PANEL_BG,
            corner_radius=18,
            border_width=1,
            border_color=BORDER,
            height=150
        )
        frame.pack(fill="x")
        frame.pack_propagate(False)

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=22, pady=16)

        if IDL_LOGO.exists():
            try:
                image = Image.open(IDL_LOGO).convert("RGBA")
                max_w, max_h = 118, 118
                ratio = min(max_w / image.width, max_h / image.height)
                logo_size = (
                    max(1, int(image.width * ratio)),
                    max(1, int(image.height * ratio))
                )

                self.idl_logo_image = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=logo_size
                )
                ctk.CTkLabel(
                    inner,
                    text="",
                    image=self.idl_logo_image
                ).pack(side="left", padx=(0, 18))
            except Exception:
                pass

        text = ctk.CTkFrame(inner, fg_color="transparent")
        text.pack(side="left", fill="y", expand=True)

        ctk.CTkLabel(
            text,
            text="IDL LIVE SUITE",
            text_color=GOLD,
            font=("Segoe UI", 31, "bold")
        ).pack(anchor="w", pady=(8, 0))

        ctk.CTkLabel(
            text,
            text="BROADCAST CONTROL CENTRE",
            text_color=WHITE,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            text,
            text="Live scoring overlays for Scolia and Target DartCounter",
            text_color=MUTED,
            font=("Segoe UI", 12)
        ).pack(anchor="w", pady=(6, 0))

        status_box = ctk.CTkFrame(
            inner,
            fg_color=PANEL_ALT,
            corner_radius=12,
            width=175,
            height=76
        )
        status_box.pack(side="right", pady=18)
        status_box.pack_propagate(False)

        ctk.CTkLabel(
            status_box,
            text="SYSTEM STATUS",
            text_color=MUTED,
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(12, 2))

        self.header_status = ctk.CTkLabel(
            status_box,
            text="●  READY",
            text_color=READY,
            font=("Segoe UI", 14, "bold")
        )
        self.header_status.pack()

    def _build_banner(self):
        frame = ctk.CTkFrame(
            self.main,
            fg_color=PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER
        )
        frame.pack(fill="x", pady=(16, 14))

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 8))

        ctk.CTkLabel(
            top,
            text="MATCH BANNER",
            text_color=GOLD,
            font=("Segoe UI", 15, "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text="Shown on the lower gold bar of the live overlay",
            text_color=MUTED,
            font=("Segoe UI", 11)
        ).pack(side="right")

        controls = ctk.CTkFrame(frame, fg_color="transparent")
        controls.pack(fill="x", padx=18, pady=(0, 16))

        self.banner = ctk.CTkEntry(
            controls,
            height=42,
            corner_radius=10,
            fg_color="#101010",
            border_color="#373737",
            text_color=WHITE,
            placeholder_text="e.g. IDL World Championship - Round 3",
            placeholder_text_color="#666666",
            font=("Segoe UI", 13)
        )
        self.banner.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 12)
        )

        ctk.CTkButton(
            controls,
            text="APPLY BANNER",
            command=self.save_banner,
            width=170,
            height=42,
            corner_radius=10,
            fg_color=GOLD,
            hover_color=GOLD_HOVER,
            text_color="#090909",
            font=("Segoe UI", 12, "bold")
        ).pack(side="right")

    def _build_providers(self):
        frame = ctk.CTkFrame(self.main, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        scolia = ctk.CTkFrame(
            frame,
            fg_color=PANEL_BG,
            corner_radius=18,
            border_width=1,
            border_color=BORDER
        )
        scolia.grid(
            row=0, column=0,
            sticky="nsew",
            padx=(0, 7)
        )

        dartcounter = ctk.CTkFrame(
            frame,
            fg_color=PANEL_BG,
            corner_radius=18,
            border_width=1,
            border_color=BORDER
        )
        dartcounter.grid(
            row=0, column=1,
            sticky="nsew",
            padx=(7, 0)
        )

        self._provider_card(
            scolia,
            "Scolia",
            "scolia",
            SCOLIA_LOGO,
            SCOLIA_GREEN,
            "Auto-scoring connection for live Scolia matches."
        )

        self._provider_card(
            dartcounter,
            "Target DartCounter",
            "dartcounter",
            DARTCOUNTER_LOGO,
            DARTCOUNTER_RED,
            "Browser-based connection for manual or smart scoring."
        )

    def _provider_card(
        self,
        parent,
        name,
        key,
        logo_path,
        accent,
        description
    ):
        ctk.CTkFrame(
            parent,
            height=5,
            fg_color=accent,
            corner_radius=0
        ).pack(fill="x")

        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=18)

        logo_box = ctk.CTkFrame(
            content,
            fg_color=PANEL_ALT,
            corner_radius=14,
            height=120
        )
        logo_box.pack(fill="x")
        logo_box.pack_propagate(False)

        loaded = False

        if logo_path.exists():
            try:
                image = Image.open(logo_path).convert("RGBA")
                # Fit the source PNG inside the logo area without
                # stretching it. Both width and height are scaled by
                # the same ratio.
                if key == "scolia":
                    max_w, max_h = 150, 100
                else:
                    max_w, max_h = 145, 105

                ratio = min(
                    max_w / image.width,
                    max_h / image.height
                )

                logo_size = (
                    max(1, int(image.width * ratio)),
                    max(1, int(image.height * ratio))
                )

                logo = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=logo_size
                )

                if key == "scolia":
                    self.scolia_logo_image = logo
                else:
                    self.dartcounter_logo_image = logo

                ctk.CTkLabel(
                    logo_box,
                    text="",
                    image=logo
                ).pack(expand=True)

                loaded = True
            except Exception:
                pass

        if not loaded:
            ctk.CTkLabel(
                logo_box,
                text=name,
                text_color=WHITE,
                font=("Segoe UI", 22, "bold")
            ).pack(expand=True)

        ctk.CTkLabel(
            content,
            text=name.upper(),
            text_color=WHITE,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(16, 3))

        ctk.CTkLabel(
            content,
            text=description,
            text_color=MUTED,
            font=("Segoe UI", 12),
            justify="left",
            wraplength=390
        ).pack(anchor="w")

        status_box = ctk.CTkFrame(
            content,
            fg_color="#101010",
            corner_radius=10,
            height=48
        )
        status_box.pack(fill="x", pady=(18, 14))
        status_box.pack_propagate(False)

        ctk.CTkLabel(
            status_box,
            text="STATUS",
            text_color="#777777",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(14, 8))

        status = ctk.CTkLabel(
            status_box,
            text="●  READY",
            text_color=READY,
            font=("Segoe UI", 12, "bold")
        )
        status.pack(side="left")

        button = ctk.CTkButton(
            content,
            text=f"START {name.upper()} OVERLAY",
            command=lambda: self.open_overlay(key),
            height=46,
            corner_radius=10,
            fg_color=GOLD,
            hover_color=GOLD_HOVER,
            text_color="#080808",
            font=("Segoe UI", 12, "bold")
        )
        button.pack(fill="x")

        if key == "scolia":
            self.scolia_status = status
            self.scolia_button = button
        else:
            self.dartcounter_status = status
            self.dartcounter_button = button

    def _build_status_bar(self):
        frame = ctk.CTkFrame(
            self.main,
            fg_color="#101010",
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            height=48
        )
        frame.pack(fill="x", pady=(14, 0))
        frame.pack_propagate(False)

        ctk.CTkLabel(
            frame,
            text="IDL LIVE SUITE",
            text_color=GOLD,
            font=("Segoe UI", 11, "bold")
        ).pack(side="left", padx=(16, 12))

        ctk.CTkLabel(
            frame,
            text="•",
            text_color="#555555"
        ).pack(side="left")

        self.status = ctk.CTkLabel(
            frame,
            text="Ready",
            text_color=MUTED,
            font=("Segoe UI", 11)
        )
        self.status.pack(side="left", padx=10)

        ctk.CTkLabel(
            frame,
            text="OVERLAY-V3",
            text_color="#666666",
            font=("Segoe UI", 10, "bold")
        ).pack(side="right", padx=16)

    # ======================================================
    # BANNER
    # ======================================================

    def load_banner(self):
        ensure_runtime_files()

        if not BANNER_FILE.exists():
            BANNER_FILE.write_text(
                json.dumps({"text": ""}, indent=4),
                encoding="utf-8"
            )

        try:
            data = json.loads(
                BANNER_FILE.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            data = {"text": ""}

        self.banner.delete(0, "end")
        self.banner.insert(0, data.get("text", ""))

    def save_banner(self):
        ensure_runtime_files()

        BANNER_FILE.write_text(
            json.dumps(
                {"text": self.banner.get().strip()},
                indent=4
            ),
            encoding="utf-8"
        )

        self.status.configure(text="Match banner saved")

    # ======================================================
    # STATUS HELPERS
    # ======================================================

    def _set_provider_status(self, provider, text, color):
        label = (
            self.scolia_status
            if provider == "scolia"
            else self.dartcounter_status
        )

        label.configure(
            text=text,
            text_color=color
        )

    def _set_other_ready(self, provider):
        if provider == "scolia":
            self.dartcounter_status.configure(
                text="●  READY",
                text_color=READY
            )
        else:
            self.scolia_status.configure(
                text="●  READY",
                text_color=READY
            )

    # ======================================================
    # OVERLAY / PROVIDER SELECTION
    # ======================================================

    def open_overlay(self, provider_name):
        provider_name = provider_name.lower().strip()

        if provider_name not in ("scolia", "dartcounter"):
            self.status.configure(
                text=f"Unknown provider: {provider_name}"
            )
            return

        if (
            self.overlay_process is not None
            and self.overlay_process.poll() is None
        ):
            display = (
                "Scolia"
                if self.active_provider == "scolia"
                else "Target DartCounter"
            )

            self.status.configure(
                text=f"{display} overlay is already running"
            )

            self.header_status.configure(
                text="●  LIVE",
                text_color=LIVE
            )
            return

        try:
            self.active_provider = provider_name

            # Development mode:
            #   launch the overlay as a Python module.
            #
            # Packaged EXE mode:
            #   launch the companion IDL Broadcast Overlay.exe
            #   from the same application folder.
            if getattr(sys, "frozen", False):
                overlay_exe = (
                    Path(sys.executable).resolve().parent
                    / "IDL Broadcast Overlay.exe"
                )

                if not overlay_exe.exists():
                    raise FileNotFoundError(
                        f"Could not find {overlay_exe.name}"
                    )

                command = [
                    str(overlay_exe),
                    provider_name
                ]

                working_dir = Path(sys.executable).resolve().parent

            else:
                command = [
                    sys.executable,
                    "-m",
                    "ui.broadcast_overlay",
                    provider_name
                ]

                working_dir = PROJECT_DIR

            self.overlay_process = subprocess.Popen(
                command,
                cwd=working_dir
            )

            display = (
                "Scolia"
                if provider_name == "scolia"
                else "Target DartCounter"
            )

            self.status.configure(
                text=f"Opening {display} overlay..."
            )

            self.header_status.configure(
                text="●  CONNECTING",
                text_color=CONNECTING
            )

            self._set_provider_status(
                provider_name,
                "●  CONNECTING",
                CONNECTING
            )

            self._set_other_ready(provider_name)

            self.after(1500, self.check_overlay)

        except Exception as exc:
            self.status.configure(
                text=f"Could not open overlay: {exc}"
            )

            self.header_status.configure(
                text="●  ERROR",
                text_color=ERROR
            )

            self._set_provider_status(
                provider_name,
                "●  CONNECTION FAILED",
                ERROR
            )

            self.active_provider = None

    def check_overlay(self):
        if self.overlay_process is None:
            return

        return_code = self.overlay_process.poll()

        if return_code is None:
            display = (
                "Scolia"
                if self.active_provider == "scolia"
                else "Target DartCounter"
            )

            self._set_provider_status(
                self.active_provider,
                "●  LIVE",
                LIVE
            )

            self.header_status.configure(
                text="●  LIVE",
                text_color=LIVE
            )

            self.status.configure(
                text=f"{display} live overlay running"
            )

            self.after(1200, self.check_overlay)

        else:
            if self.active_provider:
                self._set_provider_status(
                    self.active_provider,
                    f"●  STOPPED ({return_code})",
                    ERROR
                )

            self.header_status.configure(
                text="●  READY",
                text_color=READY
            )

            self.status.configure(
                text="Overlay closed"
            )

            self.overlay_process = None
            self.active_provider = None


if __name__ == "__main__":
    MainWindow().mainloop()