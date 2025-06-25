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
    response_1 = models.IntegerField()
    response_2 = models.IntegerField()
    is_correct = models.BooleanField()

    def check_response(self):
        self.is_correct = (
            self.response_1 == self.subsession.lookup_dict[self.subsession.word[0]]
            and
            self.response_2 == self.subsession.lookup_dict[self.subsession.word[1]]
        )
        if self.iscorrect:
            self.payoff = self.subsession.payment_per_correct

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

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.check_response()

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Intro, Decision, Results]
