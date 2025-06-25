import string
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
    lookup_table = models.StringField()
    word = models.StringField()

    def setup_round(self):
        self.payment_per_correct = Currency(0.10)
        self.lookup_table = "AB"
        self.word = "AB"

    @property
    def lookup_dict(self):
        lookup = {}
        for letter in string.ascii_uppercase: # the whole 26 alphabets
            lookup[letter] = self.lookup_table.index(letter)
        return lookup

    @property
    def correct_response(self):
        return [self.lookup_dict[letter] for letter in self.word]


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    response_1 = models.IntegerField()
    response_2 = models.IntegerField()
    is_correct = models.BooleanField()

    @property
    def response(self):
        return [self.response_1, self.response_2]

    def check_response(self):
        self.is_correct = self.response == self.subsession.correct_response
        #(
            #self.response_1 == self.subsession.lookup_dict[self.subsession.word[0]] # 0 is the first word A = 1
           # and
            #self.response_2 == self.subsession.lookup_dict[self.subsession.word[1]] # 1 is the second word B = 2
        #) # we can write it but that's going to be very long. Can we just make a list?
        if self.is_correct:
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
