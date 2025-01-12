from os import environ


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_db',
        'USER': 'otree_user',
        'PASSWORD': 'researchlaba',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


SESSION_CONFIGS = [
     dict(
         name='experiment',
         app_sequence=['introduction', 'video_task_one',
                       'introduction_task', 'math_task',
                       'video_task_two', 'ball_task',
                       'demographics' ,'conclusion'],
        # app_sequence=['ball_task'],
         num_demo_participants=3,
     ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.10, participation_fee=6.00, doc=""
)

ROOMS = [
    dict(
        name='TestRoom',
        display_name='Test room for HR',
        participant_label_file='_rooms/pretest.txt',
    )
]

PARTICIPANT_FIELDS = ['math_task_win_round', 'math_task_win_points', 'ball_task_win_round', 'ball_task_win_points']
SESSION_FIELDS = []

# ISO-639 cod
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '3943740758195'

DEBUG = False