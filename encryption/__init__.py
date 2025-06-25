import string
import time
import random

from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'encryption'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3
    TIME_FOR_TASK = 40
    LOOKUP_TABLES = [
        "ZYXJIUTLKQSRNWVHGFEDMOPCBA",
        "ZYXWVUTSRQPONMLKJIHGFEDCBA",
        "BADCFEHGJILKNMPORQTSVUXWZY",
    ]


class Subsession(BaseSubsession):
    payment_per_correct = models.CurrencyField()
    time_for_task = models.IntegerField()
    lookup_table = models.StringField()
    word = models.StringField()
    random_seed = models.IntegerField()

    def setup_round(self):
        if self.round_number == 1:
            self.random_seed = self.session.config.get("random_seed", 123435678)
            random.seed(self.random_seed)
        self.payment_per_correct = Currency(0.10)
        self.time_for_task = C.TIME_FOR_TASK
        self.lookup_table = C.LOOKUP_TABLES[(self.round_number - 1) % 3]
        self.word = "".join(random.choices(string.ascii_uppercase, k=5))

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
    started_task_at = models.FloatField()
    response_1 = models.IntegerField()
    response_2 = models.IntegerField()
    response_3 = models.IntegerField()
    response_4 = models.IntegerField()
    response_5 = models.IntegerField()
    is_correct = models.BooleanField()


    @property
    def response_fields(self):
        return ["response_1", "response_2", "response_3", "response_4", "response_5"]

    @property
    def response(self):
        return [self.response_1, self.response_2, self.response_3, self.response_4, self.response_5]

    def check_response(self):
        self.is_correct = self.response == self.subsession.correct_response
        #(
            #self.response_1 == self.subsession.lookup_dict[self.subsession.word[0]] # 0 is the first word A = 1
           # and
            #self.response_2 == self.subsession.lookup_dict[self.subsession.word[1]] # 1 is the second word B = 2
        #) # we can write it but that's going to be very long. Can we just make a list?
        if self.is_correct:
            self.payoff = self.subsession.payment_per_correct

    def start_task(self):
        self.started_task_at = time.time()

    def get_time_elapsed(self):
        return time.time() - self.in_round(1).started_task_at

    def get_time_remaining(self):
        return self.subsession.in_round(1).time_for_task - self.get_time_elapsed()

def creating_session(subsession):
    subsession.setup_round() #subsession 1 (round 1)

# PAGES
class Intro(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.start_task()


class Decision(Page):
    form_model = "player"


    @staticmethod
    def get_timeout_seconds(player):
        return player.get_time_remaining()

    @staticmethod
    def get_form_fields(player):
        return player.response_fields

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.check_response()

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Intro, Decision, Results]
