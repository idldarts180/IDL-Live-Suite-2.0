"""
IDL Live Suite
Match Model
Version 2.0
"""


class Match:

    def __init__(self):

        self.provider = ""

        self.player1_name = ""
        self.player2_name = ""

        self.player1_score = 501
        self.player2_score = 501

        self.player1_legs = 0
        self.player2_legs = 0

        self.player1_average = 0.0
        self.player2_average = 0.0

        self.player1_first9 = 0.0
        self.player2_first9 = 0.0

        self.player1_checkout = 0.0
        self.player2_checkout = 0.0

        self.player1_last_score = 0
        self.player2_last_score = 0

        self.current_player = 0

    def reset(self):

        self.__init__()