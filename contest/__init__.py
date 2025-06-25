from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'contest'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2
    ENDOWMENT = Currency(10)
    COST_PER_TICKET = Currency(0.50)
    PRIZE = Currency(8)


class Subsession(BaseSubsession):
    is_paid = models.BooleanField()
    csf = models.StringField(choices=["share", "allpay"])

    def setup_round(self):
        self.is_paid = self.round_number % 2 == 1 # now paid the odd number; True means we pay every round at this moment
        self.csf = self.session.config["contest_csf"]
        for group in self.get_groups():
            group.setup_round()

    def compute_outcome(self):
        for group in self.get_groups():
            group.compute_outcome()

class Group(BaseGroup):
    prize = models.CurrencyField()


    def setup_round(self):
        self.prize = C.PRIZE
        for player in self.get_players():
            player.setup_round()

    def compute_outcome_share(self):
        total = sum(player.tickets_purchased for player in self.get_players())
        for player in self.get_players():
            try:
                 player.prize_won = player.tickets_purchased / total
            except ZeroDivisionError:
                 player.prize_won = 1 / len(self.get_players())
            player.earnings = (
                player.endowment -
                player.tickets_purchased * player.cost_per_ticket +
                self.prize * player.prize_won
            )
            if self.subsession.is_paid:  #subsession.round_number % 2 == 1:
                player.payoff = player.earnings # payoff is set by otree.

    def compute_outcome_allpay(self):
        max_tickets = max(player.tickets_purchased for player in self.get_players())
        num_tied = len([
            player for player in self.get_players()
                       if player.tickets_purchased == max_tickets])
        for player in self.get_players():
            if player.tickets_purchased == max_tickets:
                player.prize_won = 1 / num_tied
            else:
                player.prize_won = 0



    def compute_outcome(self):
        if self.subsession.csf == "share":
            self.compute_outcome_share()
        elif self.subsession.csf == "allpay":
            self.compute_outcome_allpay()
        for player in self.get_players():
                player.earnings = (
                player.endowment -
                player.tickets_purchased * player.cost_per_ticket +
                self.prize * player.prize_won
        )
        if self.subsession.is_paid:
            player.payoff = player.earnings

class Player(BasePlayer):
    endowment = models.CurrencyField()
    cost_per_ticket = models.CurrencyField()
    tickets_purchased = models.IntegerField() # can do IntegerField(min=0, max=100) but only when you are certain about the number
    # max_tickets_affordable = models.IntegerField() but better use the property
    prize_won = models.FloatField()
    earnings = models. CurrencyField()

    def setup_round(self):
        self.endowment = self.session.config.get("contest_endowment", C.ENDOWMENT)
        self.cost_per_ticket = C.COST_PER_TICKET


    @property #property is usually very short, 2-3 lines, instead of long
    def coplayer(self):
        return self.group.get_player_by_id(3 - self.id_in_group)
    # @property lets you access a method like an attribute — without using parentheses
    # Now you can just write:
    # player.coplayer with no parentheses

    @property
    def max_tickets_affordable(self):
        return int(self.endowment / self.cost_per_ticket)





#def creating_session(subsession): # then you don't need the SetupRound anymore
    #subsession.setup_round()

# PAGES
class SetupRound(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession):
        subsession.setup_round() # this function calls when all players arrive, and do whatever you put in this function,
        #here is call setup_round()


class Intro(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Decision(Page):
    form_model = "player"
    form_fields = ["tickets_purchased"]

    @staticmethod
    def error_message(player, values):
        if values["tickets_purchased"] < 0:
            return "You cannot buy a negative number of tickets."
        if values["tickets_purchased"] > player.max_tickets_affordable: #it's now a property
            return (
                "Buying {values['tickets_purchased']} tickets would cost" # single quotes
                # This is a regular string.
                # It has no f prefix, so Python does not evaluate the {...}.
                # It's just text — the curly braces and the dictionary access inside will not be evaluated.
                f"{values['tickets_purchased'] * player.cost_per_ticket}"
                # This is an f-string (formatted string literal).
                # Python evaluates everything inside the {}.
                # It computes the actual multiplication result and inserts it into the string.
                f"which is more than your endowment of {player.endowment}." # in Python, you can split the sentences and Python will automatically fix that into a whole sentence.
            )
        return None # optional
    # If you don’t explicitly write return None, Python will automatically return None by default when a function reaches the end without hitting a return statement.


class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession):
        subsession.compute_outcome()


class Results(Page):
    pass
# almost don't use vars something


class EndBlock(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    SetupRound,
    Intro,
    Decision,
    ResultsWaitPage,
    Results,
    EndBlock,]
