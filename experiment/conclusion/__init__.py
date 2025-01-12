import time

from otree.api import *
import math

doc = """
This app serves to debrief our participants, tell them how much they have won in which round and in total
 and also in future to implement getting their bank account information in order to pay them out.
"""


class C(BaseConstants):
    NAME_IN_URL = 'conclusion'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass
    # def calculate_chocolates(self):
    #   real_amount = self.participant.payoff_plus_participation_fee().to_real_world_currency(self.session)
    #   bonus_payment = real_amount - 6
    #   bonus_chocolates = math.ceil(bonus_payment / 2)
    #   return max(0, bonus_chocolates) + 3  # Add 3 attendance chocolates


# EXTRA DATABASE MODELS
class FinalScore(ExtraModel):
    player = models.Link(Player)
    math_task_win_round = models.IntegerField()
    math_task_win_points = models.CurrencyField()
    ball_task_win_round = models.IntegerField()
    ball_task_win_points = models.CurrencyField()
    total_payout = models.CurrencyField()
    timestamp = models.StringField()


# FUNCTIONS
def record_final_score(player: Player, timestamp):
    FinalScore.create(player=player,
                      math_task_win_round=player.participant.math_task_win_round,
                      math_task_win_points=player.participant.math_task_win_points,
                      ball_task_win_round=player.participant.ball_task_win_round,
                      ball_task_win_points=player.participant.ball_task_win_points,
                      total_payout=player.participant.payoff_plus_participation_fee(),
                      timestamp=timestamp)


# PAGES
class Results(Page):

    @staticmethod
    def vars_for_template(player: Player):
        record_final_score(player, time.time())
        return dict(
            total_payout=player.participant.payoff_plus_participation_fee()
            # total_chocolates=player.calculate_chocolates()
        )


page_sequence = [Results]
