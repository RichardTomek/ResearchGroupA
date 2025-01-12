from otree.api import *

doc = """
Demographics Part
"""

class C(BaseConstants):
    NAME_IN_URL = 'demographics'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    gender = models.StringField(
        choices=['Female', 'Male', 'Other', 'Prefer not to say'],
        label="What is your gender?",
        widget=widgets.RadioSelect
    )

    age = models.StringField(
        choices=['18-24', '25-34', '35-44', '45-54', '55-70', 'above 70'],
        label="What is your age?",
        widget=widgets.RadioSelect  # Added widget for consistent styling
    )

    consumed_substances = models.StringField(
        choices=['None', 'Coffee', 'Alcohol', 'Other substances'],
        label="Have you consumed any of the following within the last 2 hours?",
        widget=widgets.RadioSelect
    )

    heavy_meal = models.BooleanField(
        label="Have you had a heavy meal within the last 2 hours?",
        choices=[
            [True, 'Yes'],
            [False, 'No']
        ],
        widget=widgets.RadioSelect
    )

    exercise = models.BooleanField(
        label="Have you done any intense physical exercise within the last 2 hours?",
        choices=[
            [True, 'Yes'],
            [False, 'No']
        ],
        widget=widgets.RadioSelect
    )

    math_enjoyment = models.IntegerField(
        choices=[
            (1, 'Not at all'),
            (2, 'Slightly'),
            (3, 'Somewhat'),
            (4, 'Moderately'),
            (5, 'Quite a bit'),
            (6, 'Very much'),
            (7, 'An extreme amount')
        ],
        label="How much do you enjoy mathematical tasks in general?",
        widget=widgets.RadioSelect
    )

    ball_task_enjoyment = models.IntegerField(
        choices=[
            (1, 'Not at all'),
            (2, 'Slightly'),
            (3, 'Somewhat'),
            (4, 'Moderately'),
            (5, 'Quite a bit'),
            (6, 'Very much'),
            (7, 'An extreme amount')
        ],
        label="How much did you enjoy catching-ball tasks in general?",
        widget=widgets.RadioSelect
    )

# PAGES
class Demo(Page):
    form_model = 'player'
    form_fields = ['gender', 'age', 'consumed_substances', 'heavy_meal',
                  'exercise', 'math_enjoyment', 'ball_task_enjoyment']

page_sequence = [Demo]