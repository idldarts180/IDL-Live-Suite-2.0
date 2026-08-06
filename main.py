"""
IDL Live Suite
Version 2.2
"""

from providers.provider_manager import ProviderManager
from ui.dashboard import Dashboard


def main():

    # -----------------------------------
    # Choose Provider
    # -----------------------------------

    manager = ProviderManager()

    provider = manager.use_scolia()
    # provider = manager.use_dartcounter()

    # -----------------------------------
    # Connect
    # -----------------------------------

    provider.connect()

    provider.wait_for_match()

    # -----------------------------------
    # Dashboard
    # -----------------------------------

    app = Dashboard()

    # -----------------------------------
    # Live Refresh Loop
    # -----------------------------------

    def refresh():

        provider.update()

        match = provider.get_match()

        app.update_match(match)

        print("\033c", end="")

        print("=" * 45)
        print("IDL LIVE SUITE")
        print("=" * 45)
        print()

        print(f"Provider : {match.provider}")

        print()
        print(match.player1_name)
        print(f"Score     : {match.player1_score}")
        print(f"Average   : {match.player1_average}")
        print(f"First 9   : {match.player1_first9}")
        print(f"Checkout  : {match.player1_checkout}%")

        print()

        print(match.player2_name)
        print(f"Score     : {match.player2_score}")
        print(f"Average   : {match.player2_average}")
        print(f"First 9   : {match.player2_first9}")
        print(f"Checkout  : {match.player2_checkout}%")

        app.after(1000, refresh)

    refresh()

    try:

        app.mainloop()

    finally:

        provider.close()


if __name__ == "__main__":

    main()