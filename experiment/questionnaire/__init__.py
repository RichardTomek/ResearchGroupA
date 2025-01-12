from otree.api import *


doc = """
This is the file containing our questionnaire description, including the self-assesment manikin and the DEQ
"""


class C(BaseConstants):
    NAME_IN_URL = 'questionnaire'
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
class SAMPage(Page):
     form_model = 'player'
     form_fields = ['excitement_sam', 'happiness_sam']

class DEQPage(Page):
        form_model = 'player'
        form_fields = ['anxiety', 'happiness', 'anger', 'desire', 'sadness', 'relaxation', 'disgust', 'fear']


page_sequence = [SAMPage, DEQPage]


