from dis import Instruction

from otree.api import *


doc = """
This app will give general information about the experiment to the participants and will initialize
global variables for all in terms of winning rounds and overall payout. It is also a page where HR monitoring
should start.
"""


class C(BaseConstants):
    NAME_IN_URL = 'introduction_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass



# PAGES
class General_Instructions(Page):
    pass


page_sequence = [General_Instructions]
