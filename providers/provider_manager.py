"""
IDL Live Suite
Provider Manager
Version 3.0
"""

from providers.scolia import ScoliaProvider
from providers.dartcounter import DartCounterProvider


class ProviderManager:

    def __init__(self):

        self.provider = None

    # ==========================================
    # Select Provider
    # ==========================================

    def use_scolia(self):

        self.provider = ScoliaProvider()

    def use_dartcounter(self):

        self.provider = DartCounterProvider()

    # ==========================================
    # Pass-through Methods
    # ==========================================

    def connect(self):

        if self.provider:
            self.provider.connect()

    def wait_for_match(self):

        if self.provider:
            self.provider.wait_for_match()

    def update(self):

        if self.provider:
            self.provider.update()

    def get_match(self):

        if self.provider:
            return self.provider.get_match()

        return None

    def close(self):

        if self.provider:
            self.provider.close()