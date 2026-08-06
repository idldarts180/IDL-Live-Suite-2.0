"""
IDL Live Suite
Version 2.0
"""

from providers.provider_manager import ProviderManager


def main():

    manager = ProviderManager()

    # Choose your provider
    provider = manager.use_scolia()
    # provider = manager.use_dartcounter()

    # Connect to provider
    provider.connect()

    # Wait until a match is open
    provider.wait_for_match()

    # Read the live match
    provider.update()

    # Get the Match object
    match = provider.get_match()

    print()
    print("=" * 40)
    print("MATCH OBJECT")
    print("=" * 40)
    print()

    print(f"Provider : {match.provider}")
    print(f"Player 1 : {match.player1_name}")
    print(f"Player 2 : {match.player2_name}")
    print(f"Score    : {match.player1_score} - {match.player2_score}")

    # Close browser
    provider.close()


if __name__ == "__main__":

    main()