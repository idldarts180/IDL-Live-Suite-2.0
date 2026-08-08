"""
IDL Live Suite
Packaged Broadcast Overlay Entry Point
"""

import sys

from ui.broadcast_overlay import BroadcastOverlay


def main():
    provider = "scolia"

    if len(sys.argv) > 1:
        requested = sys.argv[1].strip().lower()

        if requested in ("scolia", "dartcounter"):
            provider = requested

    app = BroadcastOverlay(provider)
    app.mainloop()


if __name__ == "__main__":
    main()