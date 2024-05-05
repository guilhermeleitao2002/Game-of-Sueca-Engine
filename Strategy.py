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
    
    def get_strategy(self) -> str:
        '''
            Return the strategy of the player
            In this case, the strategy is just random
        '''
        return 'Random Strategy'

### TODO: Implement more strategies
