"""
IDL Live Suite
Playwright Browser
Version 2.0
"""

from playwright.sync_api import sync_playwright


class Browser:

    def __init__(self, profile, url):

        self.profile = profile
        self.url = url

        self.playwright = None
        self.context = None
        self.page = None

    def connect(self):

        self.playwright = sync_playwright().start()

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.profile,
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
            self.context.close()
        except:
            pass

        try:
            self.playwright.stop()
        except:
            pass