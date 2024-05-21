import numpy as np
from random import randint
from Card import Card
from copy import deepcopy
from itertools import product
from termcolor import colored
import Team
import Game

############################################# Player General Classes #############################################

class Player:
    '''
        Player ->
            - name: player name
            - id: id of the player
            - hand: list of Card objects the player has (initially 10)
            - team: team object to which the player belongs
            - verbose: print the player actions
    '''

    def __init__(self, id:int, name:str, team:'Team', v:bool) -> None:
        self.verbose = v
        self.id = id
        self.name = name
        self.hand = []
        self.team = team

    def add_card(self, card:Card) -> None:
        '''
            Add card to player hand and sort it by order to facilitate strategy implementation
        '''

        self.hand.append(card)
        self.team.initial_points += card.value
        self.hand = sorted(self.hand, key=lambda x: x.order)

    def get_cards_by_suit(self, suit:str) -> list[Card]:
        '''
            Get all cards of a given suit
        '''

        filtered_hand = []
        # For each card
        for card in self.hand:
            if card.suit == suit:
                filtered_hand.append(card)

        return filtered_hand

    def get_partner(self) -> 'Player':
        '''
            Get the partner of the player
        '''

        return self.team.get_partner(self)

    def get_card(self, card_name:str) -> Card:
        '''
            Get the card object from the player's hand
        '''

        for card in self.hand:
            if card.name == card_name:
                return card


class BeliefPlayer (Player):
    '''
        BeliefPlayer ->
            - id: id of the player
            - name: player name
            - team: team object to which the player belongs
            - v: verbose
            - beliefs: beliefs of the player
    '''

    def __init__(self, id:int, name:str, team:'Team', v:bool) -> None:
        super().__init__(id, name, team, v)

        # Store the belief at each timestamp [player, suit, card]
        self.beliefs = np.ones((4, 4, 10)) / 3
        # Set the beliefs of the player itself to 0
        self.beliefs[self.id - 1] = 0

    def obtain_suit_index(self, suit: str) -> int:
        '''
            Returns the index of a given suit
        '''

        match suit:
            case "hearts":
                return 0
            case "diamonds":
                return 1
            case "clubs":
                return 2
            case "spades":
                return 3
            case _:
                raise ValueError("Invalid Suit")

    def update_beliefs_initial(self, card:Card) -> None:
        '''
            Update the beliefs of the player after the initial handing of cards
        '''

        self.beliefs[:, self.obtain_suit_index(card.suit), card.order] = 0
        self.beliefs[self.id - 1,
                     self.obtain_suit_index(card.suit), card.order] = 1

    def update_beliefs(self, card: Card, round_suit: str, player: Player, mode:str) -> None:
        '''
            Updates the new belief of the player, after a card has been spotted
        '''

        if self.verbose and mode == 'auto':
            print(f"Player {self.name} saw {card.name}")

        # After a card spotted no one will have it in their hand
        suit = self.obtain_suit_index(card.suit)
        self.beliefs[:, suit, card.order] = 0

        # If the card is not of the round suit, the player no longer has any card of the round suit
        if card.suit != round_suit:
            round_suit = self.obtain_suit_index(round_suit)
            self.beliefs[player.id - 1, round_suit, :] = 0

        # For each card
        for i in range(10):
            # For each suit
            for j in range(4):
                # Number of players that may still have the card
                num_players = np.count_nonzero(self.beliefs[:, j, i])
                # For each player
                for p in range(4):
                    if self.beliefs[p, j, i] != 0:
                        self.beliefs[p, j, i] = 1 / num_players


############################################# Player Sub Classes #############################################

class RandomPlayer (Player):
    '''
        RandomPlayer ->
            - id: id of the player
            - name: player name
            - team: team object to which the player belongs
            - v: verbose
    '''

    def __init__(self, id:int, name:str, team:'Team', v:bool) -> None:
        super().__init__(id, name, team, v)

    def play_round(self, i:int, round_suit:str, mode:str) -> Card:
        '''
            Play a round of the game of Sueca, selecting a card at random in each -round
        '''

        if i == 0:  # if the player is the first to play, play a random card
            cardPlayed = self.hand.pop(randint(0, len(self.hand) - 1))
            round_suit = cardPlayed.suit
        else:       # if the player is not the first to play, play a card of the same suit if possible
            cardsOfTheSameSuit = self.get_cards_by_suit(round_suit)
            if len(cardsOfTheSameSuit) != 0:    # if the player has cards of the same suit
                cardPlayed = cardsOfTheSameSuit[randint(
                    0, len(cardsOfTheSameSuit) - 1)]
                self.hand.remove(cardPlayed)
            else:                               # if the player does not have cards of the same suit
                cardPlayed = self.hand.pop(randint(0, len(self.hand) - 1))

        if self.verbose or (mode == 'human' and self.name != 'Leitao'):
            print(
                colored(f"{self.name} played {cardPlayed.name}", 'green', attrs=['bold']))

        return cardPlayed, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
            In this case, the strategy is just random
        '''

        return 'Random Agent'


class GreedyPlayer (Player):
    '''
        GreedyPlayer ->
            - id: id of the player
            - name: player name
            - team: team object to which the player belongs
            - v: verbose
    '''

    def __init__(self, id:int, name:str, team:'Team', v:bool) -> None:
        super().__init__(id, name, team, v)

    def play_round(self, i:int, round_suit:str, mode:str) -> tuple[Card, str]:
        '''
            Play a round of the game of Sueca, selecting the highest ranked card
        '''

        if i == 0:
            card_played = self.hand[-1]
            round_suit = card_played.suit
            self.hand.remove(card_played)
            return card_played, round_suit

        cards_of_the_same_suit = self.get_cards_by_suit(round_suit)
        if len(cards_of_the_same_suit) != 0:    # if the player has cards of the same suit
            card_played = cards_of_the_same_suit[-1]
            self.hand.remove(card_played)
        else:                               # if the player does not have cards of the same suit
            card_played = self.hand[-1]
            self.hand.remove(card_played)

        if self.verbose or (mode == 'human' and self.name != 'Leitao'):
            print(
                colored(f"{self.name} played {card_played.name}", 'green', attrs=['bold']))

        return card_played, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
            In this case, the strategy is just random
        '''

        return 'Greedy Player'


class MaximizePointsPlayer (Player):
    '''
        MaximizePointsPlayer ->
            - id: id of the player
            - name: player name
            - team: team object to which the player belongs
            - v: verbose
    '''

    def __init__(self, id:int, name:str, team:'Team', v:bool) -> None:
        super().__init__(id, name, team, v)

    def play_round(self, i:int, cards_played:list[Card], round_suit:str, players_order:list[Player], game:Game, mode:str) -> Card:
        '''
            Play a round of the game of Sueca, selecting the card that maximizes the points won
        '''

        if i == 0:
            cardPlayed = self.hand[-1]
            round_suit = cardPlayed.suit
            self.hand.remove(cardPlayed)
        else:
            cardsOfTheSameSuit = self.get_cards_by_suit(round_suit)
            _, winner = game.calculate_round_points(cards_played)
            player_winner = players_order[winner[1]]
            if player_winner.team == self.team:  # if the same team
                if cardsOfTheSameSuit:  # play strongest card from same suit
                    cardPlayed = cardsOfTheSameSuit[-1]
                    self.hand.remove(cardPlayed)
                else:
                    # else play strongest from another suit
                    cardPlayed = self.hand[-1]
                    self.hand.remove(cardPlayed)
            else:  # if different team
                if cardsOfTheSameSuit:  # if have cards from suit
                    cardPlayed = cardsOfTheSameSuit[-1]
                    if cardPlayed.order > winner[0].order:  # if can win
                        self.hand.remove(cardPlayed)  # play strongest card
                    else:
                        # else play weakest card
                        cardPlayed = cardsOfTheSameSuit[0]
                        self.hand.remove(cardPlayed)
                else:
                    trumpCards = self.get_cards_by_suit(game.trump.suit)
                    if trumpCards:  # if has trump, play the strongest trump card
                        cardPlayed = trumpCards[-1]
                        self.hand.remove(cardPlayed)
                    else:
                        cardPlayed = self.hand[0]  # play weakest card
                        self.hand.remove(cardPlayed)

        if self.verbose or (mode == 'human' and self.name != 'Leitao'):
            print(colored(f"{self.name} played {cardPlayed.name}", 'green', attrs=['bold']))

        return cardPlayed, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
        '''

        return 'Maximize Points Won'


class MaximizeRoundsWonPlayer (Player):
    '''
        MaximizeRoundsWonPlayer ->
            - id: id of the player
            - name: player name
            - team: team object to which the player belongs
            - v: verbose
    '''

    def __init__(self, id:int, name:str, team:'Team', v:bool) -> None:
        super().__init__(id, name, team, v)

    def play_round(self, i:int, cards_played:list[Card], round_suit:str, players_order:list[Player], game:Game, mode:str) -> Card:
        '''
            Play a round of the game of Sueca, selecting the card that maximizes the rounds won
        '''

        if i == 0:
            cardPlayed = self.hand[-1]
            round_suit = cardPlayed.suit
            self.hand.remove(cardPlayed)
        else:
            cardsOfTheSameSuit = self.get_cards_by_suit(round_suit)
            _, winner = game.calculate_round_points(cards_played)
            player_winner = players_order[winner[1]]
            if player_winner.team == self.team:  # if the same team
                if cardsOfTheSameSuit:  # play weakest card from the same suit
                    # preserves all strong cards
                    cardPlayed = cardsOfTheSameSuit[0]
                    self.hand.remove(cardPlayed)
                else:
                    # else play weakest from other suit
                    cardPlayed = self.hand[0]
                    self.hand.remove(cardPlayed)
            else:
                cardPlayed = None  # if different team
                if cardsOfTheSameSuit:  # if have cards from suit
                    for card in cardsOfTheSameSuit:
                        # Search for the lowest card that can win
                        if card.order > winner[0].order:
                            cardPlayed = card
                            self.hand.remove(card)
                            break
                    if not cardPlayed:  # if cant win
                        cardPlayed = cardsOfTheSameSuit[0]  # play weakest card
                        self.hand.remove(cardPlayed)
                else:
                    trumpCards = self.get_cards_by_suit(game.trump.suit)
                    if trumpCards:  # if has trump, play the weakest trump card
                        cardPlayed = trumpCards[0]
                        self.hand.remove(cardPlayed)
                    else:
                        cardPlayed = self.hand[0]  # play weakest card
                        self.hand.remove(cardPlayed)

        if self.verbose or (mode == 'human' and self.name != 'Leitao'):
            print(colored(f"{self.name} played {cardPlayed.name}", 'green', attrs=['bold']))

        return cardPlayed, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
        '''

        return 'Maximize Rounds Won'


class CooperativePlayer (BeliefPlayer):
    '''
        CooperativePlayer ->
            - id: id of the player
            - name: player name
            - team: team object to which the player belongs
            - v: verbose
    '''

    def __init__(self, id:int, name:str, team:'Team', v:bool) -> None:
        super().__init__(id, name, team, v)

    def update_beliefs_initial(self, card:Card) -> None:
        '''
            Update the beliefs of the player after the initial handing of cards
        '''

        return super().update_beliefs_initial(card)

    def update_beliefs(self, card:Card, round_suit:str, player:Player, mode:str) -> None:
        '''
            The card was seen so we now know that no player no longer has it
        '''

        super().update_beliefs(card, round_suit, player, mode)

    def play_round(self, i:int, round_suit:str, game: Game, cards_played_in_round: list[Card]) -> tuple[Card, str]:
        '''
            Play a round of the game of Sueca, selecting the card, considering
            the cards that its partner has, acting as a "team player"
        '''

        players_order = game.playersOrder
        mode = game.mode
        partner_id = self.get_partner().id
        partner_belief = self.beliefs[partner_id - 1]
        player_belief = self.beliefs[self.id - 1]
        suits = np.array(["hearts", "diamonds", "clubs", "spades"])
        player_points = np.ones((4, 10))
        partner_points = np.ones((4, 10))
        card_points = np.array([0, 0, 0, 0, 0, 2, 3, 4, 10, 11])

        for suit in suits:
            suit_index = self.obtain_suit_index(suit)
            for p in range(10):
                # Check the suit for which the partner has the best cards
                partner_points[suit_index][p] *= partner_belief[suit_index,
                                                                p] * card_points[p]
                player_points[suit_index][p] *= player_belief[suit_index,
                                                              p] * card_points[p]

        possible_points = partner_points + player_points
        if i == 0:
            # if the player is the first to play, try to play a suit for the
            # partner to use a trump card

            for suit in suits:
                suit_index = self.obtain_suit_index(suit)
                cards_of_the_same_suit = self.get_cards_by_suit(suit)
                if np.count_nonzero(partner_belief[suit_index]) == 0 and\
                        np.count_nonzero(partner_belief[self.obtain_suit_index(game.trump.suit)]) != 0\
                        and len(cards_of_the_same_suit) > 0:
                    card_played = cards_of_the_same_suit[-1]
                    self.hand.remove(cards_of_the_same_suit[-1])
                    return card_played, suit

            # Check the cards we have for which the partner has the best cards
            for suit in suits:
                suit_index = self.obtain_suit_index(suit)
                cards_to_play = self.get_cards_by_suit(suit)
                if len(cards_to_play) == 0:
                    possible_points[suit_index] = 0

            if np.count_nonzero(possible_points) > 0:
                suit_to_play = np.argmax(np.sum(possible_points, axis=1))
                cards_of_the_same_suit = self.get_cards_by_suit(
                    suits[suit_to_play])
                card_played = cards_of_the_same_suit[-1]
                self.hand.remove(cards_of_the_same_suit[-1])
                return card_played, suits[suit_to_play]

            # TODO: Make the player save the trumps in case he has no more points
            card_played = self.hand[-1]
            self.hand.remove(card_played)
            return card_played, card_played.suit

        if i == 1:
            cards_of_the_same_suit = self.get_cards_by_suit(round_suit)
            suit_index = self.obtain_suit_index(round_suit)
            if np.count_nonzero(partner_belief[self.obtain_suit_index(game.trump.suit)]) != 0\
                    and len(cards_of_the_same_suit) > 0 and\
                    np.count_nonzero(partner_belief[suit_index]) == 0:
                # In this case independently of our play our partner can cut
                card_played = cards_of_the_same_suit[-1]

            # Check if either we or our partner can cut
            elif len(cards_of_the_same_suit) == 0:
                trump_cards = self.get_cards_by_suit(game.trump.suit)
                if trump_cards:  # if has trump, play the weakest trump card
                    card_played = trump_cards[0]
                else:
                    if np.count_nonzero(partner_belief[self.obtain_suit_index(game.trump.suit)]) != 0 and\
                            np.count_nonzero(partner_belief[suit_index]) == 0:
                        card_played = self.hand[-1]  # play weakest card
                    else:
                        card_played = self.hand[0]
            else:
                _, winner = game.calculate_round_points(cards_played_in_round)
                # Search for the lowest card that can win
                winning_card_found = False
                if np.count_nonzero(possible_points[suit_index]) > 0:
                    for k in range(10):
                        if (player_points[suit_index][k] > 0 or partner_points[suit_index][k] > 0)\
                                and k > winner[0].order:
                            if cards_of_the_same_suit:
                                card_played = cards_of_the_same_suit[-1]
                            else:
                                card_played = self.hand[-1]
                            winning_card_found = True
                            break
                if not winning_card_found:
                    card_played = cards_of_the_same_suit[0]
            self.hand.remove(card_played)

        else:       # if the player is not the first to play, play a card of the same suit if possible
            cards_of_the_same_suit = self.get_cards_by_suit(round_suit)
            _, winner = game.calculate_round_points(cards_played_in_round)
            player_winner = players_order[winner[1]]
            if player_winner == self.get_partner():  # if the same team
                if cards_of_the_same_suit:  # play strongest card from same suit
                    card_played = cards_of_the_same_suit[-1]
                    self.hand.remove(card_played)
                else:
                    # else play strongest from another suit
                    card_played = self.hand[-1]
                    self.hand.remove(card_played)
            else:  # if different team
                if cards_of_the_same_suit:  # if have cards from suit
                    card_played = cards_of_the_same_suit[-1]
                    if card_played.order > winner[0].order:  # if can win
                        self.hand.remove(card_played)  # play strongest card
                    else:
                        # else play weakest card
                        card_played = cards_of_the_same_suit[0]
                        self.hand.remove(card_played)
                else:
                    trumpCards = self.get_cards_by_suit(game.trump.suit)
                    if trumpCards:  # if has trump, play the strongest trump card
                        card_played = trumpCards[-1]
                        self.hand.remove(card_played)
                    else:
                        card_played = self.hand[0]  # play weakest card
                        self.hand.remove(card_played)

        if self.verbose or (mode == 'human' and self.name != 'Leitao'):
            print(
                colored(f"{self.name} played {card_played.name}", 'green', attrs=['bold']))

        return card_played, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
        '''

        return 'Cooperative Player'


class PredictorPlayer (BeliefPlayer):
    '''
        PredictorPlayer ->
            - id: id of the player
            - name: player name
            - team: team object to which the player belongs
            - v: verbose
    '''

    def __init__(self, id:int, name:str, team:'Team', v:bool) -> None:
        super().__init__(id, name, team, v)

    def update_beliefs_initial(self, card:Card) -> None:
        '''
            Update the beliefs of the player after the initial handing of cards
        '''

        return super().update_beliefs_initial(card)

    def update_beliefs(self, card:Card, round_suit:str, player:Player, mode:str) -> None:
        '''
            Update the beliefs of the player after a card has been spotted
        '''

        super().update_beliefs(card, round_suit, player, mode)

    def get_player_possible_cards(self, player:Player, suit:str='all') -> tuple[list[Card], list[float]]:
        '''
            Returns the cards of a given player
        '''

        if suit != 'all':
            player_cards = player.get_cards_by_suit(suit)
            if player_cards == []:
                player_cards = deepcopy(player.hand)
        else:
            player_cards = deepcopy(player.hand)

        # Get the probability of each card in beliefs
        cards_prob = []
        for card in player_cards:
            cards_prob.append(
                self.beliefs[player.id - 1, self.obtain_suit_index(card.suit), card.order])

        return player_cards, cards_prob

    def play_round(self, i:int, cards_played_in_round:list[Card], round_suit:str, players_order:list[Player], game:Game, mode:str, num_round:int) -> tuple[Card, str]:
        '''
            Play a round of Sueca, selecting the card considering the cards that its partner has,
            acting as a "team player", and using utility based on projected round points and
            probabilities of card holdings.
        '''
        cards_to_play = {}
        cards_probability = {}
        for player in players_order:
            if i == 0 or not player.get_cards_by_suit(round_suit):
                cards_to_play[player.id], cards_probability[player.id] = self.get_player_possible_cards(
                    player)
            else:
                cards_to_play[player.id], cards_probability[player.id] = self.get_player_possible_cards(
                    player, round_suit)

        utility_per_card = {}

        for card in cards_to_play[self.id]:
            expected_utility = 0
            other_players_ids = [
                player.id for player in players_order if players_order.index(player) > i]
            possible_plays_combinations = [
                cards_to_play[pid] for pid in other_players_ids]
            probabilities_combinations = [
                cards_probability[pid] for pid in other_players_ids]

            # Create cartesian product of all combinations with their probabilities
            for other_cards_tuple in product(*possible_plays_combinations):
                combination_probability = np.prod([
                    probabilities_combinations[j][possible_plays_combinations[j].index(
                        card)]
                    for j, card in enumerate(other_cards_tuple)
                ])

                # Simulate this card being played along with the combination
                simulated_cards_played = cards_played_in_round + \
                    [card] + list(other_cards_tuple)
                round_points, winning_card = game.calculate_round_points(
                    simulated_cards_played)
                if players_order[winning_card[1]].team.name == self.team.name:
                    expected_utility += round_points * combination_probability
                else:
                    expected_utility -= round_points * combination_probability

            utility_per_card[card] = expected_utility

        utilities = [(card.name, utility_per_card[card])
                     for card in utility_per_card.keys()]

        ##############################################################
        # NOTE: In here, put individual strategies that you remember #
        ##############################################################
        if num_round < 2:    # In the first 2 rounds, if you are the first to play
            # Avoid using the trump card by decreasing its utility
            for card in utilities:
                if self.get_card(card[0]).suit == game.trump.suit:
                    utilities[utilities.index(card)] = (card[0], card[1] - 1000)    # NOT REALLY DOING ANYTHING BUT IT SHOULD RIGHT?
        ##############################################################
        # NOTE: In here, put individual strategies that you remember #
        ##############################################################

        # Sort the cards by utility
        utilities = sorted(utilities, key=lambda x: x[1], reverse=True)

        # Print the card.name and its utility
        if self.verbose and mode == 'auto':
            print(
                f"Player {self.name} has the following utilities: {utilities}")

        # Get the card with the highest utility
        # If there is a draw, the first card with the lowest card.order is chosen
        best_card = self.get_card(utilities[0][0])
        if i == 0:
            round_suit = best_card.suit
        self.hand.remove(best_card)

        if self.verbose and mode == 'auto' or (mode == 'human' and self.name != 'Leitao'):
            print(colored(f"{self.name} played {best_card.name}", 'green', attrs=['bold']))

        return best_card, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
            In this case, the strategy is just random
        '''

        return 'Deck Predictor'
