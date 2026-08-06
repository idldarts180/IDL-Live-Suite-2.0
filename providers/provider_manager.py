"""
IDL Live Suite
Provider Manager
Version 2.0
"""

from providers.scolia import ScoliaProvider
from providers.dartcounter import DartCounterProvider


class ProviderManager:

    def __init__(self):

        self.provider = None

    def use_scolia(self):

        self.provider = ScoliaProvider()

        return self.provider

    def use_dartcounter(self):

        self.provider = DartCounterProvider()

        return self.provider

    def get_provider(self):

        return self.provider