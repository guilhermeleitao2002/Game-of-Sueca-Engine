#####################################################################################################
############################################# Libraries #############################################
#####################################################################################################

from Card import Card
from Team import Team
from Game import Game

import Strategy

from random import randint, shuffle, choice


#####################################################################################################
############################################## Functions ############################################
#####################################################################################################

def create_game(strategy) -> Game:
    '''
        Create a game with 2 teams, 2 players each, and a deck of 40 cards
        Randomize players and team to start
        Create game deck
        Return the game object
    '''

    team1 = Team("Sporting")
    team2 = Team("Benfica")

    player1 = Strategy.RandomPlayer("Leitão", team1)
    player2 = Strategy.RandomPlayer("Fred", team1)
    player3 = Strategy.RandomPlayer("Pedro", team2)
    player4 = Strategy.RandomPlayer("Sebas", team2)

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

def create_deck() -> list:
    '''
        Create a deck of 40 cards
        Return the deck
    '''

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

def hand_cards(game) -> None:
    '''
        Distribute 10 cards to each player at random
        Last card is the trump card
    '''

    for i, player in enumerate(game.playersOrder):
        for j in range(10):
            card = game.deck.pop(randint(0, len(game.deck) - 1))
            player.add_card(card)
            if i == len(game.playersOrder) - 1: ## Last player
                if j == 9:                      ## Last card
                    game.trump = card

def calculate_round_points(cardsPlayedInRound, gameTrumpSuit) -> tuple:
    '''
        Calculate the points of a given round and its winner
        Return the round points and the winner index according to the players order
    '''

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

def rotate_order_to_winner(playersOrderList, winner) -> list:
    '''
        Rotate the players order list so that the winner of the round starts the next one
        Maintain the order of the other players
    '''

    winner_index = playersOrderList.index(winner)    
    rotated_list = playersOrderList[winner_index:] + playersOrderList[:winner_index]

    return rotated_list

def play_round(game) -> None:
    '''
        Play a round of the game
        Each player plays a card
        Calculate the round points and the winner
        Update the winner team score
        Rotate the players order list
    '''

    print('\n')

    roundSuit = ''
    cardsPlayedInround = []
    for i, player in enumerate(game.playersOrder):
        player.play_round(i, cardsPlayedInround, roundSuit)

    roundPoints, winnerId = calculate_round_points(cardsPlayedInround, game.trump.suit)

    playerWinnerOfRound = game.playersOrder[winnerId]
    playerWinnerOfRound.team.score += roundPoints

    print(playerWinnerOfRound.name + " wins the round")

    game.playersOrder = rotate_order_to_winner(game.playersOrder, playerWinnerOfRound)

def play_game(strategy) -> None:
    '''
        Play a game of Sueca
        Create a game object
        Hand cards to players
        Play 10 rounds
        Print the final score and winner
    '''

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