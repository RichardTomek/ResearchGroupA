from otree.api import *
from frisbee.otree_extension.server_instance import server

doc = """
This is the first relaxation video that will be 5 minutes long showing relaxing scenery
 to the participant and asking him to relax while the baseline HR is measured.
"""


class C(BaseConstants):
    NAME_IN_URL = 'video_task_one'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
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


# PAGES
@server.map_frisbee_data
class Video(Page):
    @staticmethod
    def live_method(player: Player, data):
        label = player.participant.label
        if data["type"] == "video_start":
            server.start_recording(player, label)

    @staticmethod
    def before_next_page(player, timeout_happened):
        label = player.participant.label
        server.stop_recording(label)


class Introduction(Page):
    pass

class SAMPage(Page):
    form_model = 'player'
    form_fields = ['excitement_sam', 'happiness_sam']


class DEQPage(Page):
    form_model = 'player'
    form_fields = ['anxiety', 'happiness', 'anger', 'desire', 'sadness', 'relaxation', 'disgust', 'fear']


class End(Page):
    pass


page_sequence = [Introduction, Video, End, SAMPage, DEQPage]
