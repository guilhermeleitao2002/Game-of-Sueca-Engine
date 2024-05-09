import numpy as np

from random import randint
from Card import Card


class Player:
    '''
        Player ->
            - name: player name
            - id: id of the player
            - hand: list of Card objects the player has (initially 10)
            - team: team object to which the player belongs
            - add_card(card): add card to player hand and sort it by order
            - get_cards_by_suit(suit): get all cards of a given suit
    '''

    def __init__(self, id, name, team) -> None:
        self.id = id
        self.name = name
        self.hand = []
        self.team = team

    def add_card(self, card) -> None:
        '''
            Add card to player hand and sort it by order to facilitate strategy implementation
        '''

        self.hand.append(card)
        self.hand = sorted(self.hand, key=lambda x: x.order)

    def get_cards_by_suit(self, suit) -> list:
        '''
            Get all cards of a given suit
        '''

        filtered_hand = []
        # For each card
        for card in self.hand:
            if card.suit == suit:
                filtered_hand.append(card)

        return filtered_hand


class RandomPlayer (Player):
    '''
        RandomPlayer ->
            - name: player name
            - team: team object to which the player belongs
            - play_round(i, cards_played, round_suit): play a round of the game
    '''

    def __init__(self, id, name, team) -> None:
        super().__init__(id, name, team)

    def play_round(self, i, cards_played, round_suit, players_order) -> Card:
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

        cards_played.append(cardPlayed)

        print(self.name + " played " + cardPlayed.name)
        return cardPlayed, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
            In this case, the strategy is just random
        '''
        return 'Random Agent'


class MaximizePointsPlayer(Player):

    def __init__(self, id, name, team) -> None:
        super().__init__(id, name, team)

    def play_round(self, i, cards_played, round_suit, players_order, game) -> Card:
        if i == 0:
            cardPlayed = self.hand.pop(randint(0, len(self.hand) - 1))
            round_suit = cardPlayed.suit
        else:
            cardsOfTheSameSuit = self.get_cards_by_suit(round_suit)
            _, winner = game.calculate_round_points(cards_played, round_suit)
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

        print(cardPlayed.name)
        cards_played.append(cardPlayed)
        return cardPlayed, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
        '''
        return 'Maximize Points Won'


class MaximizeRoundsWonPlayer(Player):

    def __init__(self, id, name, team) -> None:
        super().__init__(id, name, team)

    def play_round(self, i, cards_played, round_suit, players_order, game):
        if i == 0:
            cardPlayed = self.hand.pop(randint(0, len(self.hand) - 1))
            round_suit = cardPlayed.suit
        else:
            cardsOfTheSameSuit = self.get_cards_by_suit(round_suit)
            _, winner = game.calculate_round_points(cards_played, round_suit)
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
                        # Search for the lowest card taht can win
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

        print(cardPlayed.name)
        cards_played.append(cardPlayed)
        return cardPlayed, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
        '''
        return 'Maximize Rounds Won'


class BeliefPlayer(Player):
    '''
        BeliefPlayer ->
            - name: player name
            - team: team object to which the player belongs
            - play_round(i, cards_played, round_suit): play a round of the game
    '''

    def __init__(self, id, name, team, others) -> None:
        super().__init__(id, name, team)
        self.card_ordering_index = {
            '2_of_hearts': 0, '2_of_diamonds': 1, '2_of_spades': 2, '2_of_clubs': 3,
            '3_of_hearts': 4, '3_of_diamonds': 5, '3_of_spades': 6, '3_of_clubs': 7,
            '4_of_hearts': 8, '4_of_diamonds': 9, '4_of_spades': 10, '4_of_clubs': 11,
            '5_of_hearts': 12, '5_of_diamonds': 13, '5_of_spades': 14, '5_of_clubs': 15,
            '6_of_hearts': 16, '6_of_diamonds': 17, '6_of_spades': 18, '6_of_clubs': 19,
            'J_of_hearts': 20, 'J_of_diamonds': 21, 'J_of_spades': 22, 'J_of_clubs': 23,
            'Q_of_hearts': 24, 'Q_of_diamonds': 25, 'Q_of_spades': 26, 'Q_of_clubs': 27,
            'K_of_hearts': 28, 'K_of_diamonds': 29, 'K_of_spades': 30, 'K_of_clubs': 31,
            '7_of_hearts': 32, '7_of_diamonds': 33, '7_of_spades': 34, '7_of_clubs': 35,
            'A_of_hearts': 36, 'A_of_diamonds': 37, 'A_of_spades': 38, 'A_of_clubs': 39
        }
        self.beliefs = {others[0]: [1/3 for _ in range(40)], others[1]: [
                                    1/3 for _ in range(40)], others[2]: [1/3 for _ in range(40)]}

        # Store the belief at each timestep [suit, card, player]
        # hearts - 0
        # diamonds - 1
        self.beliefs_2 = np.ones((4,10,4)) / 3

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
            case _ :
                raise ValueError("Invalid Suit")

    def update_beliefs(self, card, round_suit, player_name) -> None:
        '''
            The card was seen so we now know that no player no longer has it
        '''

        # Update the beliefs of the other players
        print(f"Player {self.name} saw {card.name}")
        for player in self.beliefs:
            index = self.card_ordering_index[card.name]
            self.beliefs[player][index] = 0

        # If the card is not of the round suit, update the beliefs of the
        # player that played the card
        if card.suit != round_suit and self.name != player_name:
            print(f"Player {self.name} noticed that {player_name} does not have any more {round_suit}!!!")

            match round_suit:
                case "hearts":
                    j = 0
                case "diamonds":
                    j = 1
                case "spades":
                    j = 2
                case "clubs":
                    j = 3

            # TODO: In this case, player is set to the last key of self
            for i in range(10):
                self.beliefs[player_name][i*4 + j] = 0
            
                    
            print(self.beliefs)

    def update_beliefs_2(self, card: Card, round_suit: str, player: Player) -> None:
        '''
            Updates the new belief of the player, after a card has been spoted
        '''

        print(f"Player {self.name} saw {card.name}")
        
        # After a card spotted no one will have it in their hand
        self.beliefs_2[self.obtain_suit_index(card.suit)][card.order] = 0

        if card.suit != round_suit:
            print(f"Player {self.name} noticed that {player.name} does not have any more {round_suit}!!!")

            for i in range(10):
                prob_dist = self.beliefs_2[self.obtain_suit_index(card.suit)][i]
                prob_sum = np.sum(prob_dist) - 1
                possible_players = np.count_nonzero(prob_dist)
                self.beliefs_2[self.obtain_suit_index(card.suit)][i][player.id - 1] = 0
                self.beliefs_2[self.obtain_suit_index(card.suit)][i][prob_dist > 0] = prob_sum / possible_players

            print(self.beliefs_2)
            

    # For immediately after the cards are handed
    def update_beliefs_initial(self, card) -> None:
        '''
            Update the beliefs of the player after the initial handing of cards
        '''

        for player in self.beliefs:
            index = self.card_ordering_index[card]
            self.beliefs[player][index] = 0

    def update_beliefs_initial_2(self, deck: list[Card]) -> None:
        '''
            Updates the belief_2 matrix to take into consideration the initial Deck
        '''
        print(self.hand)
        for card in deck:
            if card in self.hand:
                #print(f"Player {self.name} has {card.name}")
                self.beliefs_2[self.obtain_suit_index(card.suit)][card.order] = 0
                self.beliefs_2[self.obtain_suit_index(card.suit)][card.order][self.id -1] = 1
            else:
                self.beliefs_2[self.obtain_suit_index(card.suit)][card.order][self.id -1] = 0
        #print(self.beliefs_2)

class CooperativePlayer(BeliefPlayer):
    '''
        CoopeartivePlayer ->
            - name: player name
            - team: team object to which the player belongs
            - play_round(i, cards_played, round_suit): play a round of the game
    '''

    def __init__(self,id,  name, team, others) -> None:
        super().__init__(id, name, team, others)

    def update_beliefs(self, card, round_suit, player_name) -> None:
        '''
            The card was seen so we now know that no player no longer has it
        '''
        super().update_beliefs(card, round_suit, player_name)

    def update_beliefs_initial(self, card) -> None:
        return super().update_beliefs_initial(card)

    def play_round(self, i, cards_played_in_round, round_suit, players_order) -> Card:
        '''
            Play a round of the game of Sueca, selecting the card, considering
            the cards that its partner has, acting as a "team player"
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

        cards_played_in_round.append(cardPlayed)

        print(self.name + " played " + cardPlayed.name)

        self.beliefs_2[self.obtain_suit_index(cardPlayed.suit)][cardPlayed.order][self.id - 1] = 0

        return cardPlayed, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
        '''
        return 'Cooperative Player'


class PredictorPlayer(BeliefPlayer):

    def __init__(self,id,  name, team, others) -> None:
        super().__init__(id, name, team, others)

    # For during the game
    def update_beliefs(self, card, round_suit, player_name) -> None:
        super().update_beliefs(card, round_suit, player_name)

    # For immediately after the cards are handed
    def update_beliefs_initial(self, card) -> None:
        return super().update_beliefs_initial(card)

    def play_round(self, i, cards_played, round_suit, players_order) -> tuple[Card, str]:
        '''
            Play a round of the game of Sueca, selecting a card at random in each round
        '''

        # Update beliefs
        #self.update_beliefs(cards_played, round_suit, player_name)

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

        cards_played.append(cardPlayed)

        print(self.name + " played " + cardPlayed.name)

        return cardPlayed, round_suit

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
            In this case, the strategy is just random
        '''
        return 'Deck Predictor'


### TODO: Implement more strategies
### TODO: Implement more strategies
### TODO: Implement more strategies
