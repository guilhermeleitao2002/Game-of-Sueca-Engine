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
        self.hand = sorted(self.hand, key=lambda x: x.order)

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

class Game:
    def __init__ (self, teams, strategy):
        self.teams = teams
        self.strategy = strategy
        self.playersOrder = []
        self.deck = []
        self.trump = None

def create_game(strategy):
    team1 = Team("Sporting")
    team2 = Team("Benfica")

    player1 = Player("Leitão", team1)
    player2 = Player("Fred", team1)
    player3 = Player("Pedro", team2)
    player4 = Player("Sebas", team2)

    team1.add_player(player1)
    team1.add_player(player2)
    team2.add_player(player3)
    team2.add_player(player4)

    game = Game([team1, team2], strategy)

    # randomize players and team to start
    random.shuffle(team1.players)
    random.shuffle(team2.players)
    first_team = random.choice([team1, team2])
    second_team = team2 if first_team is team1 else team1
    game.playersOrder = [player for pair in zip(first_team.players, second_team.players) for player in pair]

    game.deck = create_deck()

    return game

def create_deck():
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

def hand_cards(game):
    for i, player in enumerate(game.playersOrder):
        for j in range(10):
            card = game.deck.pop(random.randint(0, len(game.deck) - 1))
            player.add_card(card)
            if i == len(game.playersOrder) - 1: ## Last player
                if j == 9:                      ## Last card
                    game.trump = card

def calculate_round_points(cardsPlayedInRound, gameTrumpSuit):
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

def rotate_order_to_winner(playersOrderList, winner):
    winner_index = playersOrderList.index(winner)    
    rotated_list = playersOrderList[winner_index:] + playersOrderList[:winner_index]

    return rotated_list

def play_round(game):
    roundSuit = ''
    cardsPlayedInround = []
    print('\n')

    for i, player in enumerate(game.playersOrder):
        if i == 0:
            cardPlayed = player.hand.pop(random.randint(0, len(player.hand) - 1))
            roundSuit = cardPlayed.suit
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

    print(playerWinnerOfRound.name + " wins the round")

    game.playersOrder = rotate_order_to_winner(game.playersOrder, playerWinnerOfRound)

def play_game(strategy):
    if strategy != 'random':  ### Implement function for seperate strategy
        print('Please provide a supported strategy')
        return 1
    
    game = create_game(strategy)

    hand_cards(game)

    for player in game.playersOrder:
        print(player.name)
        for card in player.hand:
            print(card.name)
        print("\n")
    print(f'Trump card: {game.trump.name}')

    for num_rounds in range(10):
        print("\nRound " + str(num_rounds + 1) + ":")
        play_round(game)

    print("\nSporting score: " + str(game.teams[0].score))
    print("Benfica score: " + str(game.teams[1].score))

    if game.teams[0].score > game.teams[1].score:
        print("Sporting wins!")
    elif game.teams[0].score == game.teams[1].score:
        print("It's a tie!")
    else:
        print("Benfica wins!")


play_game('random')
