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
        if i == 0:
            cardPlayed = self.hand.pop(randint(0, len(self.hand) - 1))
            round_suit = cardPlayed.suit
        else:
            cardsOfTheSameSuit = self.get_cards_by_suit(round_suit)
            if len(cardsOfTheSameSuit) != 0:
                cardPlayed = cardsOfTheSameSuit[randint(0, len(cardsOfTheSameSuit) - 1)]
                self.hand.remove(cardPlayed)
            else:
                cardPlayed = self.hand.pop(randint(0, len(self.hand) - 1))

        cards_played.append(cardPlayed)

        print(self.name + " played " + cardPlayed.name)
        return cardPlayed
