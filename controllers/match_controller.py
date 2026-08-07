"""
IDL Live Suite
Match Controller
"""

from providers.scolia import ScoliaProvider


class MatchController:

    def __init__(self):

        self.provider = ScoliaProvider()

        self.connected = False

    # ======================================

    def connect(self):

        if self.connected:
            return

        self.provider.connect()

        # Removed wait_for_match() so the GUI
        # doesn't pause waiting for Enter.

        self.connected = True

        print("Connected to Scolia.")

    # ======================================

    def update(self):

        if not self.connected:
            return None

        self.provider.update()

        return self.provider.get_match()

    # ======================================

    def close(self):

        self.provider.close()