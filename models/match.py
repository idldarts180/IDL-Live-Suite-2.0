"""
IDL Live Suite
Match Model
Version 2.1 - Set play support
"""


class Match:

    def __init__(self):

        # -------------------------
        # Provider
        # -------------------------

        self.provider = ""

        # -------------------------
        # Player 1
        # -------------------------

        self.player1_name = "Player 1"
        self.player1_score = 501
        self.player1_average = 0.0
        self.player1_first9 = 0.0
        self.player1_checkout = 0.0
        self.player1_legs = 0
        self.player1_sets = 0
        self.player1_darts_remaining = 3
        self.player1_180_event = 0

        # -------------------------
        # Player 2
        # -------------------------

        self.player2_name = "Player 2"
        self.player2_score = 501
        self.player2_average = 0.0
        self.player2_first9 = 0.0
        self.player2_checkout = 0.0
        self.player2_legs = 0
        self.player2_sets = 0
        self.player2_darts_remaining = 3
        self.player2_180_event = 0

        # -------------------------
        # Match Information
        # -------------------------

        self.first_to = 6
        self.match_format = ""
        self.is_set_play = False
        self.competition = "IDL Exhibition"

    def __str__(self):

        return (
            f"{self.player1_name} ({self.player1_score}) "
            f"vs "
            f"{self.player2_name} ({self.player2_score})"
        )