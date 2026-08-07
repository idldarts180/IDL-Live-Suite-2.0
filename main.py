"""
IDL Live Suite
Main
Version 3.0
"""

from providers.provider_manager import ProviderManager
from ui.overlay import Overlay


def main():

    # ==========================================
    # Provider
    # ==========================================

    manager = ProviderManager()

    # Change this later from the Control Centre
    manager.use_scolia()

    # ==========================================
    # Connect
    # ==========================================

    manager.connect()

    manager.wait_for_match()

    # ==========================================
    # Overlay
    # ==========================================

    overlay = Overlay()

    # ==========================================
    # Refresh Loop
    # ==========================================

    def refresh():

        manager.update()

        match = manager.get_match()

        if match:

            overlay.update_match(match)

        overlay.after(500, refresh)

    refresh()

    try:

        overlay.mainloop()

    finally:

        manager.close()


if __name__ == "__main__":

    main()