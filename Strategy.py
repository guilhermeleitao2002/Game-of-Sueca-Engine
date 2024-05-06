from Player import Player
from random import randint
from Card import Card

class RandomPlayer (Player):
    '''
        RandomPlayer ->
            - name: player name
            - team: team object to which the player belongs
            - play_round(i, cards_played, round_suit): play a round of the game
    '''

    def __init__ (self, name, team) -> None:
        super().__init__(name, team)

    def play_round(self, i, cards_played, round_suit) -> Card:
        '''
            Play a round of the game of Sueca, selecting a card at random in each round
        '''

        if i == 0:  # if the player is the first to play, play a random card
            cardPlayed = self.hand.pop(randint(0, len(self.hand) - 1))
            round_suit = cardPlayed.suit
        else:       # if the player is not the first to play, play a card of the same suit if possible
            cardsOfTheSameSuit = self.get_cards_by_suit(round_suit)
            if len(cardsOfTheSameSuit) != 0:    # if the player has cards of the same suit
                cardPlayed = cardsOfTheSameSuit[randint(0, len(cardsOfTheSameSuit) - 1)]
                self.hand.remove(cardPlayed)
            else:                               # if the player does not have cards of the same suit
                cardPlayed = self.hand.pop(randint(0, len(self.hand) - 1))

        cards_played.append(cardPlayed)

        print(self.name + " played " + cardPlayed.name)

        return cardPlayed
    
    def update_beliefs(self, card_played) -> None:
        '''
            Update the beliefs of the player
            DOES NOT APPLY TO THIS STRATEGY
        '''

        return

    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
            In this case, the strategy is just random
        '''
        return 'Random Agent'


class PredictorPlayer (Player):


    def __init__(self, name, team, others) -> None:
        super().__init__(name, team)

        # Initialize belief state for players (partner and opponents, total of 3 players)
        # The belief state is a list of 10*4 elements corresponding to the probability of each card being in the player's hand
        # The ordering of the cards is the following:
        # 2 of hearts,diamonds,spades,clubs | 3 of hearts,diamonds,spades,clubs | ... | 7 of hearts,diamonds,spades,clubs | Ace of hearts,diamonds,spades,clubs
        self.card_ordering_index = {'2_of_hearts': 0, '2_of_diamonds': 1, '2_of_spades': 2, '2_of_clubs': 3,
                               '3_of_hearts': 4, '3_of_diamonds': 5, '3_of_spades': 6, '3_of_clubs': 7,
                               '4_of_hearts': 8, '4_of_diamonds': 9, '4_of_spades': 10, '4_of_clubs': 11,
                               '5_of_hearts': 12, '5_of_diamonds': 13, '5_of_spades': 14, '5_of_clubs': 15,
                               '6_of_hearts': 16, '6_of_diamonds': 17, '6_of_spades': 18, '6_of_clubs': 19,
                               'J_of_hearts': 20, 'J_of_diamonds': 21, 'J_of_spades': 22, 'J_of_clubs': 23,
                               'Q_of_hearts': 24, 'Q_of_diamonds': 25, 'Q_of_spades': 26, 'Q_of_clubs': 27,
                               'K_of_hearts': 28, 'K_of_diamonds': 29, 'K_of_spades': 30, 'K_of_clubs': 31,
                               '7_of_hearts': 32, '7_of_diamonds': 33, '7_of_spades': 34, '7_of_clubs': 35,
                               'A_of_hearts': 36, 'A_of_diamonds': 37, 'A_of_spades': 38, 'A_of_clubs': 39}

        # Before handing the cards, the probability of each card being in each player's hand is 0.25
        # However, after the initial handing of cards, it will be 0.33 for those cards that are not in the own player's hand
        # So we initialize the belief state with 0.33 for all cards for each player
        self.beliefs = {others[0]:[0.33 for _ in range(40)], others[1]:[0.33 for _ in range(40)], others[2]:[0.33 for _ in range(40)]}

    def update_beliefs(self, card, round_suit, player_name) -> None:
            '''
                The card was seen so we now know that no player no longer has it
            '''

            # Update the beliefs of the other players
            print(f"Player {self.name} saw {card.name}")
            for player in self.beliefs:
                index = self.card_ordering_index[card.name]
                self.beliefs[player][index] = 0

            if card.suit != round_suit:
                print(f"Player {self.name} noticed that {player_name} does not have any more {round_suit}!!!")

                player = self.beliefs[player_name]
                
                match round_suit:
                    case "hearts":
                        j = 0
                    case "diamonds":
                        j = 1
                    case "spades":
                        j = 2
                    case "clubs":
                        j = 3    

                for i in range(10):
                    player[i*4 + j] = 0

    def play_round(self, i, cards_played, round_suit) -> Card:
        '''
            Play a round of the game of Sueca, selecting a card at random in each round
        '''

        if i == 0:  # if the player is the first to play, play a random card
            cardPlayed = self.hand.pop(randint(0, len(self.hand) - 1))
            round_suit = cardPlayed.suit
        else:       # if the player is not the first to play, play a card of the same suit if possible
            cardsOfTheSameSuit = self.get_cards_by_suit(round_suit)
            if len(cardsOfTheSameSuit) != 0:    # if the player has cards of the same suit
                cardPlayed = cardsOfTheSameSuit[randint(0, len(cardsOfTheSameSuit) - 1)]
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
