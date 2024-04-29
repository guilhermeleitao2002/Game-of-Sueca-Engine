#####################################################################################################
############################################# Libraries #############################################
#####################################################################################################

from random import shuffle, randint, choice


#####################################################################################################
############################################## Classes ##############################################
#####################################################################################################

''' 
    Team ->
        - name: team name
        - players: list of Player objects
        - score: team score (0 - 120)
        - add_player(player): add player to team
'''
class Team:
    def __init__ (self, name) -> None:
        self.name = name
        self.players = []
        self.score = 0
    
    def add_player(self, player) -> None:
        self.players.append(player)

'''
    Player ->
        - name: player name
        - hand: list of Card objects the player has (initially 10)
        - team: team object to which the player belongs
        - add_card(card): add card to player hand and sort it by order
        - get_cards_by_suit(suit): get all cards of a given suit
'''
class Player:
    def __init__ (self, name, team) -> None:
        self.name = name 
        self.hand = []
        self.team = team

    def add_card(self, card) -> None:
        self.hand.append(card)
        self.hand = sorted(self.hand, key=lambda x: x.order)

    def get_cards_by_suit(self, suit) -> list:
        filtered_hand = []
        for card in self.hand:
            if card.suit == suit:
                filtered_hand.append(card)

        return filtered_hand

'''
    Card ->
        - name: card name
        - suit: card suit (hearts, diamonds, clubs, spades)
        - rank: card rank (2, 3, 4, 5, 6, 7, J, Q, K, A)
        - order: card order (0 - 10)
        - value: card value (0, 2, 3, 4, 10, 11)
'''
class Card:
    def __init__ (self, name, suit, rank) -> None:
        self.name = name
        self.suit = suit
        self.rank = rank
        self.order = 0
        self.value = 0

'''
    Game ->
        - teams: list of Team objects
        - strategy: game strategy
        - playersOrder: list of Player objects sorted by order to play
        - deck: list of Card objects
        - trump: trump card for that game
'''
class Game:
    def __init__ (self, teams, strategy) -> None:
        self.teams = teams
        self.strategy = strategy
        self.playersOrder = []
        self.deck = []
        self.trump = None


#####################################################################################################
############################################## Functions ############################################
#####################################################################################################

'''
    Create a game with 2 teams, 2 players each, and a deck of 40 cards
    Randomize players and team to start
    Create game deck
    Return the game object
'''
def create_game(strategy) -> Game:
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
    shuffle(team1.players)
    shuffle(team2.players)
    first_team = choice([team1, team2])
    second_team = team2 if first_team is team1 else team1
    game.playersOrder = [player for pair in zip(first_team.players, second_team.players) for player in pair]

    game.deck = create_deck()

    return game

'''
    Create a deck of 40 cards
    Return the deck
'''
def create_deck() -> list:
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

'''
    Distribute 10 cards to each player at random
    Last card is the trump card
'''
def hand_cards(game) -> None:
    for i, player in enumerate(game.playersOrder):
        for j in range(10):
            card = game.deck.pop(randint(0, len(game.deck) - 1))
            player.add_card(card)
            if i == len(game.playersOrder) - 1: ## Last player
                if j == 9:                      ## Last card
                    game.trump = card

'''
    Calculate the points of a given round and its winner
    Return the round points and the winner index according to the players order
'''
def calculate_round_points(cardsPlayedInRound, gameTrumpSuit) -> tuple:
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

'''
    Rotate the players order list so that the winner of the round starts the next one
    Maintain the order of the other players
'''
def rotate_order_to_winner(playersOrderList, winner) -> list:
    winner_index = playersOrderList.index(winner)    
    rotated_list = playersOrderList[winner_index:] + playersOrderList[:winner_index]

    return rotated_list

'''
    Play a round of the game
    Each player plays a card
    Calculate the round points and the winner
    Update the winner team score
    Rotate the players order list
'''
def play_round(game) -> None:
    roundSuit = ''
    cardsPlayedInround = []
    print('\n')

    for i, player in enumerate(game.playersOrder):
        if i == 0:
            cardPlayed = player.hand.pop(randint(0, len(player.hand) - 1))
            roundSuit = cardPlayed.suit
        else:
            cardsOfTheSameSuit = player.get_cards_by_suit(roundSuit)
            if len(cardsOfTheSameSuit) != 0:
                cardPlayed = cardsOfTheSameSuit[randint(0, len(cardsOfTheSameSuit) - 1)]
                player.hand.remove(cardPlayed)
            else:
                cardPlayed = player.hand.pop(randint(0, len(player.hand) - 1))
        
        cardsPlayedInround.append(cardPlayed)

        print(player.name + " played " + cardPlayed.name)

    roundPoints, winnerId = calculate_round_points(cardsPlayedInround, game.trump.suit)

    playerWinnerOfRound = game.playersOrder[winnerId]
    playerWinnerOfRound.team.score += roundPoints

    print(playerWinnerOfRound.name + " wins the round")

    game.playersOrder = rotate_order_to_winner(game.playersOrder, playerWinnerOfRound)

'''
    Play a game of Sueca
    Create a game object
    Hand cards to players
    Play 10 rounds
    Print the final score and winner
'''
def play_game(strategy) -> None:
    if strategy != 'random':  ### Implement function for separate strategy
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


#####################################################################################################
########################################## Main Program #############################################
#####################################################################################################

if __name__ == "__main__":
    play_game('random')