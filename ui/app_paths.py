"""
IDL Live Suite
Shared Application Paths

Provides:
- writable runtime config in %LOCALAPPDATA%\IDL Live Suite
- PyInstaller-safe bundled resource paths for assets/config
"""

import json
import os
import shutil
import sys
from pathlib import Path


APP_NAME = "IDL Live Suite"


def resource_root():
    """
    Development:
        project root

    PyInstaller one-dir/one-file:
        bundled resource root (sys._MEIPASS)
    """
    if getattr(sys, "frozen", False):
        return Path(
            getattr(
                sys,
                "_MEIPASS",
                Path(sys.executable).resolve().parent
            )
        )

    return Path(__file__).resolve().parent.parent


RESOURCE_ROOT = resource_root()

ASSETS_DIR = RESOURCE_ROOT / "assets"
LOGOS_DIR = ASSETS_DIR / "logos"
ICONS_DIR = ASSETS_DIR / "icons"
EFFECTS_DIR = ASSETS_DIR / "effects"

DEFAULT_CONFIG_DIR = RESOURCE_ROOT / "ui" / "config"

LOCAL_APPDATA = Path(
    os.environ.get(
        "LOCALAPPDATA",
        Path.home() / "AppData" / "Local"
    )
)

USER_DATA_DIR = LOCAL_APPDATA / APP_NAME

BANNER_FILE = USER_DATA_DIR / "banner.json"
LAYOUT_FILE = USER_DATA_DIR / "layout.json"


DEFAULT_BANNER = {
    "text": ""
}


DEFAULT_LAYOUT = {
    "logo": {"x": 509, "y": 119},
    "left_name": {"x": 180, "y": 185},
    "left_score": {"x": 181, "y": 235},
    "left_average": {"x": 181, "y": 279},
    "right_name": {"x": 834, "y": 185},
    "right_score": {"x": 834, "y": 235},
    "right_average": {"x": 834, "y": 279},
    "legs": {"x": 508, "y": 230},
    "format": {"x": 507, "y": 296},
    "banner": {"x": 507, "y": 329},
    "left_checkout": {"x": 181, "y": 279},
    "right_checkout": {"x": 834, "y": 279}
}


def _copy_or_create(source, destination, fallback):
    if destination.exists():
        return

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if source.exists():
        shutil.copy2(source, destination)
        return

    destination.write_text(
        json.dumps(fallback, indent=4),
        encoding="utf-8"
    )


def ensure_runtime_files():
    """
    Create shared writable files on first launch.

    Existing user files are never overwritten.
    """
    USER_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    _copy_or_create(
        DEFAULT_CONFIG_DIR / "banner.json",
        BANNER_FILE,
        DEFAULT_BANNER
    )

    _copy_or_create(
        DEFAULT_CONFIG_DIR / "layout.json",
        LAYOUT_FILE,
        DEFAULT_LAYOUT
    )