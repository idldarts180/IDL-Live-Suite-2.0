"""
IDL Live Suite
Playwright Browser
Version 2.1

Stores each user's browser profile in their own Windows LOCALAPPDATA folder
instead of inside the IDL Live Suite application/download folder.
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright


class Browser:

    def __init__(self, profile, url):

        self.original_profile = profile
        self.url = url

        self.playwright = None
        self.context = None
        self.page = None

        # Providers currently pass values such as:
        #   browser/profile
        #   browser/dartcounter_profile
        #
        # Use only the final folder name and store it per Windows user:
        #   %LOCALAPPDATA%\IDL Live Suite\browser\<profile name>
        #
        # This prevents developer login cookies/sessions being shipped
        # inside the public application download.
        profile_name = Path(profile).name

        local_app_data = os.environ.get("LOCALAPPDATA")

        if local_app_data:
            base_dir = Path(local_app_data)
        else:
            base_dir = Path.home() / "AppData" / "Local"

        self.profile = (
            base_dir
            / "IDL Live Suite"
            / "browser"
            / profile_name
        )

        self.profile.mkdir(
            parents=True,
            exist_ok=True
        )

    def connect(self):

        self.playwright = sync_playwright().start()

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile),
            headless=False
        )

        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        self.page.goto(
            self.url,
            wait_until="domcontentloaded"
        )

    def close(self):

        try:
            if self.context is not None:
                self.context.close()
        except Exception:
            pass

        try:
            if self.playwright is not None:
                self.playwright.stop()
        except Exception:
            pass