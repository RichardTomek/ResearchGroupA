import random

import time
from otree.api import *
from frisbee.otree_extension.server_instance import server

doc = """
Ball catching task where participants need to catch falling balls using a paddle.
"""

class C(BaseConstants):
    NAME_IN_URL = 'ball_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5
    TIME_PER_ROUND = 60
    TIME_PER_ROUND_MINUTES = TIME_PER_ROUND / 60
    TIME_RESULT = 20

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    balls_caught = models.IntegerField(initial=0)
    balls_total = models.IntegerField(initial=0)
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

class BallGameResults(ExtraModel):
    player = models.Link(Player)
    round_number = models.IntegerField()
    balls_caught = models.IntegerField()
    balls_total = models.IntegerField()
    timestamp = models.StringField()

# FUNCTIONS
def record_ball_game_result(player: Player):
    BallGameResults.create(
        player=player,
        round_number=player.round_number,
        balls_caught=player.balls_caught,
        balls_total=player.balls_total,
        timestamp=str(time.time())
    )

def generate_client_response(player: Player):
    return dict(
        balls_caught=player.balls_caught,
        balls_total=player.balls_total
    )


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
    def vars_for_template(player: Player):
        # Add this to pass the variables to the template
        return dict(
            balls_caught=player.balls_caught,
            balls_total=player.balls_total,
        )

    @staticmethod
    def live_method(player: Player, data):
        t = data['type']

        if t == 'get':
            return {player.id_in_group: generate_client_response(player)}

        elif t == 'ball_caught':
            player.balls_caught = data['balls_caught']
            player.balls_total = data['balls_total']
            return {player.id_in_group: generate_client_response(player)}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        record_ball_game_result(player)
        if player.recording:
            label = player.participant.label
            server.stop_recording(label)
            player.recording = False
        player.results = True

class Results(Page):
    timeout_seconds = C.TIME_RESULT
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            balls_caught=player.balls_caught,
            balls_total=player.balls_total,
            catch_rate=round(player.balls_caught / player.balls_total * 100
                             if player.balls_total > 0 else 0, 1)
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number == C.NUM_ROUNDS:
            rand_round = random.randint(1, 5)
            player.participant.ball_task_win_round = rand_round
            player.participant.ball_task_win_points = cu(player.in_round(rand_round).balls_caught* 0.05)
            player.participant.payoff += player.participant.ball_task_win_points


class SAMPage(Page):
    form_model = 'player'
    form_fields = ['excitement_sam', 'happiness_sam']


class DEQPage(Page):
    form_model = 'player'
    form_fields = ['anxiety', 'happiness', 'anger', 'desire', 'sadness', 'relaxation', 'disgust', 'fear']

page_sequence = [Introduction, Task, SAMPage, DEQPage, Results]