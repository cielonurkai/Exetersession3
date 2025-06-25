from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'encryption'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3


class Subsession(BaseSubsession):
    payment_per_correct = models.CurrencyField()
    word = models.StringField()

    def setup_round(self):
        self.payment_per_correct = Currency(0.10)
        self.word = "AB"

    @property
    def lookup_dict(self):
        return {"A": 1, "B": 2}

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    response_1 = models.IntField()
    response_2 = models.IntField()


def creating_session(subsession):
    subsession.setup_round() #subsession 1 (round 1)

# PAGES
class Intro(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Decision(Page):
    form_model = "player"
    form_fields = ["response_1", "response_2"]


class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Intro, Decision, Results]
