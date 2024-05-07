from random import randint, shuffle, choice
from Card import Card
from Team import Team
from Player import CooperativePlayer, RandomPlayer, MaximizePointsPlayer, MaximizeRoundsWonPlayer, PredictorPlayer, Player

class Game:
    '''
        Game ->
            - teams: list of Team objects
            - strategy: game strategy
            - playersOrder: list of Player objects sorted by order to play
            - deck: list of Card objects
            - trump: trump card for that game
            - game_info: dictionary with game information
    '''

    def __init__ (self, team_1_strategy: str, team_2_strategy: str) -> None:
        #self.strategy = strategy
        self.trump = None

        # Initialize game information
        self.game_info = {}
        self.game_info["Teams"] = []
        self.game_info["Rounds"] = {}

        # Create teams
        team1 = Team("Sporting")
        team2 = Team("Benfica")
        self.teams = [team1, team2]

        # Create players based on strategy type
        match team_1_strategy:
            case 'random':
                player1 = RandomPlayer("Leitao", team1)
                player2 = RandomPlayer("Fred", team1)
            case 'maxpointswon':
                player1 = MaximizePointsPlayer("Leitao", team1)
                player2 = MaximizePointsPlayer("Fred", team1)
            case 'maxroundswon':
                player1 = MaximizeRoundsWonPlayer("Leitao", team1)
                player2 = MaximizeRoundsWonPlayer("Fred", team1)
            case 'predictor':
                player1 = PredictorPlayer("Leitao", team1, ["Fred", "Pedro", "Sebas"])
                player2 = PredictorPlayer("Fred", team1, ["Leitao", "Pedro", "Sebas"])
            case 'cooperative':
                player1 = CooperativePlayer("Leitao", team1)
                player2 = CooperativePlayer("Fred", team1)
            case _: # default
                raise ValueError("Invalid strategy")

        match team_2_strategy:
            case 'random':
                player3 = RandomPlayer("Pedro", team2)
                player4 = RandomPlayer("Sebas", team2)
            case 'maxpointswon':
                player3 = MaximizePointsPlayer("Pedro", team2)
                player4 = MaximizePointsPlayer("Sebas", team2)
            case 'maxroundswon':
                player3 = MaximizeRoundsWonPlayer("Pedro", team2)
                player4 = MaximizeRoundsWonPlayer("Sebas", team2)
            case 'cooperative':
                player3 = CooperativePlayer("Pedro", team2)
                player4 = CooperativePlayer("Sebas", team2)
            case 'predictor':
                player3 = PredictorPlayer("Pedro", team2, ["Sebas", "Leitao", "Fred"])
                player4 = PredictorPlayer("Sebas", team2, ["Pedro", "Leitao", "Fred"])
            case _: # default
                raise ValueError("Invalid strategy")

        # Add players to teams
        team1.add_player(player1)
        team1.add_player(player2)
        team2.add_player(player3)
        team2.add_player(player4)

        # Randomize players and team to start
        shuffle(team1.players)
        shuffle(team2.players)
        first_team = choice([team1, team2])
        second_team = team2 if first_team is team1 else team1

        # Order players
        self.playersOrder = [player for pair in zip(first_team.players, second_team.players) for player in pair]

        # Create deck
        self.deck = self.create_deck()

    def create_deck(self) -> list[Card]:
        '''
            Create a deck of 40 cards with the following suits:
                - hearts
                - diamonds
                - clubs
                - spades
            and the following ranks:
                - 2, 3, 4, 5, 6, J, Q, K, 7, A
            that have the respective values:
                - 0, 0, 0, 0, 0, 2, 3, 4, 10, 11
            '''

        # Create deck suits
        suits = ["hearts", "diamonds", "clubs", "spades"]
        # Create deck ranks
        ranks = ["2", "3", "4", "5", "6", "7", "J", "Q", "K", "A"]

        deck = []
        for rank in ranks:
            for suit in suits:
                card = Card(rank + "_of_" + suit, suit, rank)
                deck.append(card)

        # Set card "importance"
        # NOTE: Different from the card value
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

        # Set card value
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

    def rotate_order_to_winner(self, playersOrderList, winner) -> list[Player]:
        '''
            Rotate the list of players to the winner of the round
        '''

        winner_index = playersOrderList.index(winner)
        rotated_list = playersOrderList[winner_index:] + playersOrderList[:winner_index]

        return rotated_list

    def calculate_round_points(self, cardsPlayedInRound, gameTrumpSuit) -> tuple[int, int]:
        '''
            Calculate the points and the winner of the round
        '''

        # Initialize winning card to the first card played
        winningCard = (cardsPlayedInRound[0], 0)

        # For each card played in the round
        for i, card in enumerate(cardsPlayedInRound):
            if i == 0:  # Skip first card (it's the winning card so far)
                continue

            # If the card is of the same suit as the winning card and has a higher order or
            # if the card is of the trump suit and the winning card is not then
            # the card is the new winning card
            if card.suit == winningCard[0].suit and card.order > winningCard[0].order or\
                card.suit == gameTrumpSuit and winningCard[0].suit != gameTrumpSuit:
                winningCard = (card, i)

        # Accumulate the points of the round
        roundPoints = 0
        for card in cardsPlayedInRound:
            roundPoints += card.value

        return roundPoints, winningCard

    def hand_cards(self) -> None:
        '''
            Distribute the cards between the players
        '''

        # For each player
        for i, player in enumerate(self.playersOrder):
            # For each card
            for j in range(10):
                # Pop a card at random
                card = self.deck.pop(randint(0, len(self.deck) - 1))
                player.add_card(card)

                if i == len(self.playersOrder) - 1: # Last player
                    if j == 9:                      # Last card
                        self.trump = card           # Is the trump

    def update_beliefs(self, cardPlayed, player_name, round_suit) -> None:
        '''
            Update the beliefs of the players except the one that played the card (no need!)
        '''

        for player in self.playersOrder:
            if player.name != player_name:
                player.update_beliefs(cardPlayed, round_suit, player_name)

        return

    def play_round(self) -> dict[str, str]:
        '''
            Play a round of the game
        '''

        print('\n')

        roundSuit = ''
        round_info = {}
        cardsPlayedInround = []

        # For each player
        for i, player in enumerate(self.playersOrder):
            if player.get_strategy() == 'Maximize Points Won' or player.get_strategy() == 'Maximize Rounds Won':
                card_played, roundSuit = player.play_round(i, cardsPlayedInround, roundSuit, self.playersOrder, self)
            else:
                card_played, roundSuit = player.play_round(i, cardsPlayedInround, roundSuit, self.playersOrder)
            if player.get_strategy() == 'Deck Predictor':
                self.update_beliefs(card_played, player.name, roundSuit)    # Update beliefs of the players

        # Get the total points played in the round and the respective winner
        roundPoints, winnerId = self.calculate_round_points(cardsPlayedInround, self.trump.suit)

        round_info["Winner"] = self.playersOrder[winnerId[1]].name
        round_info["Points"] = roundPoints

        playerWinnerOfRound = self.playersOrder[winnerId[1]]
        playerWinnerOfRound.team.score += roundPoints

        print(playerWinnerOfRound.name + " wins the round")

        # Rotate the players order to the winner of the round
        self.playersOrder = self.rotate_order_to_winner(self.playersOrder, playerWinnerOfRound)

        return round_info

    def play_game(self) -> None:
        '''
            Play the game of Sueca
        '''

        # For each player
        for player in self.playersOrder:
            print(player.name)
            # For each card
            for card in player.hand:
                print(card.name)
            print("\n")
        print(f'Trump card: {self.trump.name}')

        # For each of the 10 rounds
        for num_rounds in range(10):
            print("\nRound " + str(num_rounds + 1) + ":")
            round_info = self.play_round()
            (self.game_info["Rounds"])[num_rounds + 1] = round_info

        # Print the final game details
        print("\nSporting score: " + str(self.teams[0].score))
        print("Benfica score: " + str(self.teams[1].score))
        self.game_info["Teams"] = [self.teams[0].dump_to_json(), self.teams[1].dump_to_json()]
        if self.teams[0].score > self.teams[1].score:
            print("Sporting wins!")
        elif self.teams[0].score == self.teams[1].score:
            print("It's a tie!")
        else:
            print("Benfica wins!")
