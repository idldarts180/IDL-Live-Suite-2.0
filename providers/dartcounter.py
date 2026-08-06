"""
IDL Live Suite
DartCounter Provider
Version 2.0
"""

from providers.base_provider import BaseProvider
from models.match import Match


class DartCounterProvider(BaseProvider):

    def __init__(self):

        super().__init__()

        self.provider_name = "DartCounter"

        self.match = Match()
        self.match.provider = self.provider_name

    def connect(self):

        print("Connecting to DartCounter...")

    def wait_for_match(self):

        print("Waiting for match...")

    def update(self):

        pass

    def get_match(self):

        return self.match

    def close(self):

        print("Closing DartCounter.")