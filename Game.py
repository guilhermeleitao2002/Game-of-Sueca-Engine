from random import randint, shuffle, choice
import Strategy
from Card import Card
from Team import Team

class Game:
    '''
        Game ->
            - teams: list of Team objects
            - strategy: game strategy
            - playersOrder: list of Player objects sorted by order to play
            - deck: list of Card objects
            - trump: trump card for that game
    '''

    def __init__ (self, strategy) -> None:
        self.strategy = strategy
        self.playersOrder = []
        self.deck = []
        self.trump = None

        team1 = Team("Sporting")
        team2 = Team("Benfica")

        self.teams = [team1, team2]

        match strategy:
            case 'random':
                player1 = Strategy.RandomPlayer("Leitão", team1)
                player2 = Strategy.RandomPlayer("Fred", team1)
                player3 = Strategy.RandomPlayer("Pedro", team2)
                player4 = Strategy.RandomPlayer("Sebas", team2)
            case _:
                raise ValueError("Invalid strategy")

        team1.add_player(player1)
        team1.add_player(player2)
        team2.add_player(player3)
        team2.add_player(player4)

        # randomize players and team to start
        shuffle(team1.players)
        shuffle(team2.players)
        first_team = choice([team1, team2])
        second_team = team2 if first_team is team1 else team1
        self.playersOrder = [player for pair in zip(first_team.players, second_team.players) for player in pair]

        self.deck = self.create_deck()

    def create_deck(self) -> list:
        suits = ["hearts", "diamonds", "clubs", "spades"]
        ranks = ["2", "3", "4", "5", "6", "7", "J", "Q", "K", "A"]
        deck = []
        for rank in ranks:
            for suit in suits:
                card = Card(rank + "_of_" + suit, suit, rank)
                deck.append(card)
        
        order = {
            '2': 0,
            '3': 1,
            '4': 2,
            '5': 3,
            '6': 4,
            'J': 6,
            'Q': 7,
            'K': 8,
            '7': 9,
            'A': 10
        }
        for card in deck:
            if card.rank == 'A':
                card.value = 11
            elif card.rank == '7':
                card.value = 10
            elif card.rank == 'K':
                card.value = 4
            elif card.rank == 'J':
                card.value = 3
            elif card.rank == 'Q':
                card.value = 2
            else:
                card.value = 0   
            card.order = order[card.rank] 

        return deck

    def rotate_order_to_winner(self, playersOrderList, winner) -> list:
        winner_index = playersOrderList.index(winner)    
        rotated_list = playersOrderList[winner_index:] + playersOrderList[:winner_index]

        return rotated_list
    
    def calculate_round_points(self, cardsPlayedInRound, gameTrumpSuit) -> tuple:
        winningCard = (cardsPlayedInRound[0], 0)

        for i, card in enumerate(cardsPlayedInRound):
            if i == 0:
                continue

            if card.suit == winningCard[0].suit and card.order > winningCard[0].order or\
                card.suit == gameTrumpSuit and winningCard[0].suit != gameTrumpSuit:
                winningCard = (card, i)

        roundPoints = 0
        for card in cardsPlayedInRound:
            roundPoints += card.value

        return roundPoints, winningCard[1]


    def hand_cards(self) -> None:
        for i, player in enumerate(self.playersOrder):
            for j in range(10):
                card = self.deck.pop(randint(0, len(self.deck) - 1))
                player.add_card(card)
                if i == len(self.playersOrder) - 1: ## Last player
                    if j == 9:                      ## Last card
                        self.trump = card

    def play_round(self) -> None:
        print('\n')

        roundSuit = ''
        cardsPlayedInround = []
        for i, player in enumerate(self.playersOrder):
            player.play_round(i, cardsPlayedInround, roundSuit)

        roundPoints, winnerId = self.calculate_round_points(cardsPlayedInround, self.trump.suit)

        playerWinnerOfRound = self.playersOrder[winnerId]
        playerWinnerOfRound.team.score += roundPoints

        print(playerWinnerOfRound.name + " wins the round")

        self.playersOrder = self.rotate_order_to_winner(self.playersOrder, playerWinnerOfRound)


    def play_game(self) -> None:

        for player in self.playersOrder:
            print(player.name)
            for card in player.hand:
                print(card.name)
            print("\n")
        print(f'Trump card: {self.trump.name}')

        for num_rounds in range(10):
            print("\nRound " + str(num_rounds + 1) + ":")
            self.play_round()

        print("\nSporting score: " + str(self.teams[0].score))
        print("Benfica score: " + str(self.teams[1].score))

        if self.teams[0].score > self.teams[1].score:
            print("Sporting wins!")
        elif self.teams[0].score == self.teams[1].score:
            print("It's a tie!")
        else:
            print("Benfica wins!")
