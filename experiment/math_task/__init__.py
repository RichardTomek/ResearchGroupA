import time

from otree.api import *
from frisbee.otree_extension.server_instance import server

import random

doc = """
Math task app will make participants do equations in their head.
 The equations are randomly generated and consist of four 2-digit
 numbers which must be summed up by the participants in head.
 No help is allowed in any form (calculator, paper etc).
 There are 5 rounds each giving 2 minutes to solve as many equations
 as possible. In the end one random round shall be picked for the payout.
"""


class C(BaseConstants):
    NAME_IN_URL = 'math_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5
    TIME_PER_ROUND = 60
    TIME_PER_ROUND_MINUTES = TIME_PER_ROUND/60
    TIME_RESULT = 20


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    n1 = models.IntegerField()
    n2 = models.IntegerField()
    n3 = models.IntegerField()
    n4 = models.IntegerField()
    ans_correct = models.IntegerField()
    ans_player = models.IntegerField()
    is_correct = models.BooleanField(initial=False)
    count_equations = models.IntegerField(initial=0)
    count_correct = models.IntegerField(initial=0)
    recording = models.BooleanField(initial=False)
    results = models.BooleanField(initial=False)

    anger = models.IntegerField(
        choices=[
            (1, 'Not at all'),
            (2, 'Slightly'),
            (3, 'Somewhat'),
            (4, 'Moderately'),
            (5, 'Quite a bit'),
            (6, 'Very much'),
            (7, 'An extreme amount'),
        ],
        label="Anger",
        widget=widgets.RadioSelect
    )

    disgust = models.IntegerField(
        choices=[
            (1, 'Not at all'),
            (2, 'Slightly'),
            (3, 'Somewhat'),
            (4, 'Moderately'),
            (5, 'Quite a bit'),
            (6, 'Very much'),
            (7, 'An extreme amount'),
        ],
        label="Disgust",
        widget=widgets.RadioSelect
    )

    fear = models.IntegerField(
        choices=[
            (1, 'Not at all'),
            (2, 'Slightly'),
            (3, 'Somewhat'),
            (4, 'Moderately'),
            (5, 'Quite a bit'),
            (6, 'Very much'),
            (7, 'An extreme amount'),
        ],
        label="Fear",
        widget=widgets.RadioSelect
    )

    anxiety = models.IntegerField(
        choices=[
            (1, 'Not at all'),
            (2, 'Slightly'),
            (3, 'Somewhat'),
            (4, 'Moderately'),
            (5, 'Quite a bit'),
            (6, 'Very much'),
            (7, 'An extreme amount'),
        ],
        label="Anxiety",
        widget=widgets.RadioSelect
    )

    sadness = models.IntegerField(
        choices=[
            (1, 'Not at all'),
            (2, 'Slightly'),
            (3, 'Somewhat'),
            (4, 'Moderately'),
            (5, 'Quite a bit'),
            (6, 'Very much'),
            (7, 'An extreme amount'),
        ],
        label="Sadness",
        widget=widgets.RadioSelect
    )

    happiness = models.IntegerField(
        choices=[
            (1, 'Not at all'),
            (2, 'Slightly'),
            (3, 'Somewhat'),
            (4, 'Moderately'),
            (5, 'Quite a bit'),
            (6, 'Very much'),
            (7, 'An extreme amount'),
        ],
        label="Happiness",
        widget=widgets.RadioSelect
    )

    desire = models.IntegerField(
        choices=[
            (1, 'Not at all'),
            (2, 'Slightly'),
            (3, 'Somewhat'),
            (4, 'Moderately'),
            (5, 'Quite a bit'),
            (6, 'Very much'),
            (7, 'An extreme amount'),
        ],
        label="Desire",
        widget=widgets.RadioSelect
    )

    relaxation = models.IntegerField(
        choices=[
            (1, 'Not at all'),
            (2, 'Slightly'),
            (3, 'Somewhat'),
            (4, 'Moderately'),
            (5, 'Quite a bit'),
            (6, 'Very much'),
            (7, 'An extreme amount'),
        ],
        label="Relaxation",
        widget=widgets.RadioSelect
    )

    excitement_sam = models.IntegerField(
        choices=list(range(1, 10)),  # 1-9 scale
        label="How excited do you feel right now?",
        widget=widgets.RadioSelectHorizontal
    )

    happiness_sam = models.IntegerField(
        choices=list(range(1, 10)),  # 1-9 scale
        label="How happy do you feel right now?",
        widget=widgets.RadioSelectHorizontal
    )

# EXTRA DATABASE MODELS
class EquationAttempt(ExtraModel):
    player = models.Link(Player)
    n1 = models.IntegerField()
    n2 = models.IntegerField()
    n3 = models.IntegerField()
    n4 = models.IntegerField()
    ans_correct = models.IntegerField()
    ans_player = models.IntegerField()
    is_correct = models.BooleanField()
    timestamp = models.StringField()


class MathRoundResults(ExtraModel):
    player = models.Link(Player)
    round_number = models.IntegerField()
    count_equations = models.IntegerField()
    count_correct = models.IntegerField()
    timestamp = models.StringField()


# FUNCTIONS
def generate_equation(player: Player):
    player.n1 = random.randint(-99, 99)
    player.n2 = random.randint(-99, 99)
    player.n3 = random.randint(-99, 99)
    player.n4 = random.randint(-99, 99)
    player.ans_correct = player.n1 + player.n2 + player.n3 + player.n4


def generate_client_response(player: Player):
    return dict(
            n1=player.n1,
            n2=player.n2,
            n3=player.n3,
            n4=player.n4)


def record_equation_attempt(player: Player, timestamp):
    EquationAttempt.create(player=player,
                           n1=player.n1,
                           n2=player.n2,
                           n3=player.n3,
                           n4=player.n4,
                           ans_correct=player.ans_correct,
                           ans_player=player.ans_player,
                           is_correct=player.is_correct,
                           timestamp=timestamp)


def record_math_round_results(player: Player):
    MathRoundResults.create(player=player,
                            round_number=player.round_number,
                            count_equations=player.count_equations,
                            count_correct=player.count_correct,
                            timestamp=time.time())


# PAGES
class Introduction(Page):
    pass


@server.map_frisbee_data
class Task(Page):
    timeout_seconds = C.TIME_PER_ROUND

    @staticmethod
    def is_displayed(player: Player):
        if not player.recording and not player.results:
            label = player.participant.label
            server.start_recording(player, label)
            player.recording = True

        return True

    @staticmethod
    def live_method(player, data):
        t = data['type']

        if t == 'get':
            if player.field_maybe_none('n1') is None:
                generate_equation(player)
            return {player.id_in_group: generate_client_response(player)}

        elif t == 'submit':
            player.ans_player = data['value']
            timestamp = data['timestamp']

            player.count_equations += 1
            player.is_correct = player.ans_player == player.ans_correct
            if player.is_correct:
                player.count_correct += 1

            record_equation_attempt(player, timestamp)
            generate_equation(player)
            return {player.id_in_group: generate_client_response(player)}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        record_math_round_results(player)
        if player.recording:
            label = player.participant.label
            server.stop_recording(label)
            player.recording = False
        player.results = True


class Results(Page):
    timeout_seconds = C.TIME_RESULT

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            rand_round = random.randint(1, 5)
            player.participant.math_task_win_round = rand_round
            player.participant.math_task_win_points = cu(player.in_round(rand_round).count_correct * 0.5)
            player.participant.payoff += player.participant.math_task_win_points
        player.results = False

class SAMPage(Page):
    form_model = 'player'
    form_fields = ['excitement_sam', 'happiness_sam']


class DEQPage(Page):
    form_model = 'player'
    form_fields = ['anxiety', 'happiness', 'anger', 'desire', 'sadness', 'relaxation', 'disgust', 'fear']


page_sequence = [Introduction, Task, SAMPage, DEQPage, Results]
