from dis import Instruction

from otree.api import *


doc = """
This app will give general information about the experiment to the participants and will initialize
global variables for all in terms of winning rounds and overall payout. It is also a page where HR monitoring
should start.
"""


class C(BaseConstants):
    NAME_IN_URL = 'introduction'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# FUNCTIONS
def init_player(player: Player):
    player.participant.math_task_win_round = 0
    player.participant.math_task_win_points = cu(0)
    player.participant.ball_task_win_round = 0
    player.participant.ball_task_win_points = cu(0)


# PAGES
class Introduction(Page):

    @staticmethod
    def is_displayed(player: Player):
        init_player(player)
        return True

class General_Instructions(Page):

    @staticmethod
    def is_displayed(player: Player):
        init_player(player)
        return True


page_sequence = [Introduction]
