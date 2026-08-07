"""
IDL Live Suite
Match Controller
"""

from providers.scolia import ScoliaProvider
from providers.dartcounter import DartCounterProvider


class MatchController:

    def __init__(self, provider_name="scolia"):

        self.provider_name = provider_name.lower().strip()
        self.provider = self._create_provider(self.provider_name)

        self.connected = False

    # ======================================

    def _create_provider(self, provider_name):

        if provider_name == "scolia":
            return ScoliaProvider()

        if provider_name == "dartcounter":
            return DartCounterProvider()

        raise ValueError(
            f"Unsupported provider: {provider_name}"
        )

    # ======================================

    def connect(self):

        if self.connected:
            return

        self.provider.connect()

        self.connected = True

        print(
            f"Connected to {self.provider.provider_name}."
        )

    # ======================================

    def update(self):

        if not self.connected:
            return None

        self.provider.update()

        return self.provider.get_match()

    # ======================================

    def close(self):

        try:
            self.provider.close()
        finally:
            self.connected = False