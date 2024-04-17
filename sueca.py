import random

class Team:
    def __init__ (self, name):
        self.name = name
        self.players = []
        self.score = 0
    
    def add_player(self, player):
        self.players.append(player)

class Player:
    def __init__ (self, name, team):
        self.name = name 
        self.hand = []
        self.team = team

    def add_card(self, card):
        self.hand.append(card)

    def get_cards_by_suit(self, suit):
        filtered_hand = []
        for card in self.hand:
            if card.suit == suit:
                filtered_hand.append(card)
        return filtered_hand

class Card:
    def __init__ (self, name, suit, rank):
        self.name = name
        self.suit = suit
        self.rank = rank
        self.order = 0
        self.value = 0

    def setValue(self, value):
        self.value = value

class Game:
    def __init__ (self, teams, strategy):
        self.teams = teams
        self.strategy = strategy
        self.playersOrder = []
        self.deck = []
        self.trump = None
        self.winner = None

def create_game(startegy):
    team1 = Team("Team 1")
    team2 = Team("Team 2")

    player1 = Player("Player 1", team1)
    player2 = Player("Player 2", team1)
    player3 = Player("Player 3", team2)
    player4 = Player("Player 4", team2)

    team1.add_player(player1)
    team1.add_player(player2)
    team2.add_player(player3)
    team2.add_player(player4)

    game = Game([team1, team2], startegy)

    # randomize players and team to start
    random.shuffle(team1.players)
    random.shuffle(team2.players)
    first_team = random.choice([team1, team2])
    second_team = team2 if first_team is team1 else team1
    game.playersOrder = [player for pair in zip(first_team.players, second_team.players) for player in pair]

    return game
    
def create_deck():
    suits = ["hearts", "diamonds", "clubs", "spades"]
    ranks = ["2", "3", "4", "5", "6", "7", "J", "Q", "K", "A"]
    deck = []
    for rank in ranks:
        for suit in suits:
            card = Card(rank + "_of_" + suit, suit, rank)
            deck.append(card)
    set_card_values(deck)
    return deck

def set_card_values(deck):
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

def hand_cards(game):
    for i, player in enumerate(game.playersOrder):
        for j in range(10):
            card = game.deck.pop(random.randint(0, len(game.deck) - 1))
            player.add_card(card)
            if i == len(game.playersOrder) - 1: ## Last card is the trump
                if j == 9:
                    game.trump = card

def calculate_round_points(cardsPlayedInRound, gameTrumpSuit):
    winningCard = (None, None)
    i = 0
    while i < len(cardsPlayedInRound):
        if i == 0:
            if cardsPlayedInRound[i].suit == cardsPlayedInRound[i+1].suit:
                winningCard = (cardsPlayedInRound[i] if cardsPlayedInRound[i].order > cardsPlayedInRound[i+1].order else cardsPlayedInRound[i+1],\
                   i if cardsPlayedInRound[i].order > cardsPlayedInRound[i+1].order else i+1) 
            else: 
                if cardsPlayedInRound[i+1].suit == gameTrumpSuit:
                    winningCard = (cardsPlayedInRound[i+1], i+1)
                else:
                    winningCard = (cardsPlayedInRound[i], i)
            i += 1
        else: 
            if winningCard[0].suit == cardsPlayedInRound[i].suit:
                winningCard = (winningCard[0] if winningCard[0].order > cardsPlayedInRound[i].order else cardsPlayedInRound[i],
                               winningCard[1] if winningCard[0].order > cardsPlayedInRound[i].order else i)                
            else:
                if cardsPlayedInRound[i].suit == gameTrumpSuit:
                    winningCard = (cardsPlayedInRound[i], i)
        i += 1
    roundPoints = 0
    for card in cardsPlayedInRound:
        roundPoints += card.value
    return roundPoints, winningCard[1]

def rotate_order_to_winner(playersOrderList, winner):
    winner_index = playersOrderList.index(winner)    
    rotated_list = playersOrderList[winner_index:] + playersOrderList[:winner_index]
    return rotated_list

def play_game(strategy):
    if strategy != 'random':  ### Implement function for seperate strategy
        print('Please provide a supported strategy')
        return 1
    
    game = create_game(strategy)
    game.deck = create_deck()
    hand_cards(game)

    for player in game.playersOrder:
        print(player.name)
        for card in player.hand:
            print(card.name)
        print("\n")
    print(game.trump.name)

    num_rounds = 0
    for num_rounds in range(10):
        print("Round " + str(num_rounds + 1) + ":")
        roundSuit = ''
        cardsPlayedInround = []
        for i, player in enumerate(game.playersOrder):
            if i == 0:
                cardPlayed = player.hand.pop(random.randint(0, len(player.hand) - 1))
                roundSuit = cardPlayed.suit
                cardsPlayedInround.append(cardPlayed)
            else:
                cardsOfTheSameSuit = player.get_cards_by_suit(roundSuit)
                if len(cardsOfTheSameSuit) != 0:
                    cardPlayed = cardsOfTheSameSuit[random.randint(0, len(cardsOfTheSameSuit) - 1)]
                    player.hand.remove(cardPlayed)
                else:
                    cardPlayed = player.hand.pop(random.randint(0, len(player.hand) - 1))
                cardsPlayedInround.append(cardPlayed)
            print(player.name + " played " + cardPlayed.name)

        roundPoints, winnerId = calculate_round_points(cardsPlayedInround, game.trump.suit)
        playerWinnerOfRound = game.playersOrder[winnerId]
        playerWinnerOfRound.team.score += roundPoints 
        game.playersOrder = rotate_order_to_winner(game.playersOrder, playerWinnerOfRound)

    print("Team 1 score: " + str(game.teams[0].score))
    print("Team 2 score: " + str(game.teams[1].score))
    if game.teams[0].score > game.teams[1].score:
        print("Team 1 wins!")
    else:
        print("Team 2 wins!")

play_game('random')