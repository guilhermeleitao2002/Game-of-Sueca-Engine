from random import randint, shuffle, choice
from Card import Card
from Team import Team
from Player import CooperativePlayer, GreedyPlayer, RandomPlayer, MaximizePointsPlayer, MaximizeRoundsWonPlayer, PredictorPlayer, Player
from termcolor import colored
from time import sleep

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

    def __init__(self, team_1_strategy: str, team_2_strategy: str, v:bool, mode:str) -> None:
        self.verbose = v
        self.mode = mode

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
                player1 = RandomPlayer(1, "Leitao", team1, self.verbose)
                player2 = RandomPlayer(2, "Fred", team1, self.verbose)
            case 'maxpointswon':
                player1 = MaximizePointsPlayer(1, "Leitao", team1, self.verbose)
                player2 = MaximizePointsPlayer(2, "Fred", team1, self.verbose)
            case 'maxroundswon':
                player1 = MaximizeRoundsWonPlayer(1, "Leitao", team1, self.verbose)
                player2 = MaximizeRoundsWonPlayer(2, "Fred", team1, self.verbose)
            case 'cooperative':
                player1 = CooperativePlayer(1, "Leitao", team1, self.verbose)
                player2 = CooperativePlayer(2, "Fred", team1, self.verbose)
            case 'predictor':
                player1 = PredictorPlayer(1, "Leitao", team1, self.verbose)
                player2 = PredictorPlayer(2, "Fred", team1, self.verbose)
            case 'greedy':
                player1 = GreedyPlayer(1, "Leitao", team1, self.verbose)
                player2 = GreedyPlayer(2, "Fred", team1, self.verbose)

            case _:  # default
                raise ValueError("Invalid strategy")

        match team_2_strategy:
            case 'random':
                player3 = RandomPlayer(3, "Pedro", team2, self.verbose)
                player4 = RandomPlayer(4, "Sebas", team2, self.verbose)
            case 'maxpointswon':
                player3 = MaximizePointsPlayer(3, "Pedro", team2, self.verbose)
                player4 = MaximizePointsPlayer(4, "Sebas", team2, self.verbose)
            case 'maxroundswon':
                player3 = MaximizeRoundsWonPlayer(3, "Pedro", team2, self.verbose)
                player4 = MaximizeRoundsWonPlayer(4, "Sebas", team2, self.verbose)
            case 'cooperative':
                player3 = CooperativePlayer(3, "Pedro", team2, self.verbose)
                player4 = CooperativePlayer(4, "Sebas", team2, self.verbose)
            case 'predictor':
                player3 = PredictorPlayer(3, "Pedro", team2, self.verbose)
                player4 = PredictorPlayer(4, "Sebas", team2, self.verbose)
            case 'greedy':
                player3 = GreedyPlayer(3, "Pedro", team2, self.verbose)
                player4 = GreedyPlayer(4, "Sebas", team2, self.verbose)

            case _:  # default
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
        ranks = ["2", "3", "4", "5", "6", "7", "Q", "J", "K", "A"]

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
            'Q': 5,
            'J': 6,
            'K': 7,
            '7': 8,
            'A': 9
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
        rotated_list = playersOrderList[winner_index:] + \
            playersOrderList[:winner_index]

        return rotated_list

    def calculate_round_points(self, cardsPlayedInRound) -> tuple[int, int]:
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
                    card.suit == self.trump.suit and winningCard[0].suit != self.trump.suit:
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

                # Update beliefs of the player
                if player.get_strategy() == 'Deck Predictor' or player.get_strategy() == 'Cooperative Player':
                    player.update_beliefs_initial(card)

                if i == len(self.playersOrder) - 1: # Last player
                    if j == 9:                      # Last card
                        self.trump = card           # Is the trump

        # Print game details
        # For each player
        if self.verbose and self.mode == 'auto':
            for player in self.playersOrder:
                print(colored(f'{player.name} -> {player.team.name}', 'yellow', attrs=['underline']))
                print(colored(player.get_strategy(), attrs=['bold']))
                # For each card
                for card in player.hand:
                    print(card.name)
                print("\n")
        if self.verbose or self.mode == 'human':
            print(colored(f'Trump card: {self.trump.name}\n\n', 'blue', attrs=['bold']))
            
    def update_beliefs(self, cardPlayed, round_suit, player) -> None:
        '''
            Update the beliefs of the players except the one that played the card (no need!)
        '''

        for p in self.playersOrder:
            if p.name != player.name and (p.get_strategy() == 'Deck Predictor' or p.get_strategy() == 'Cooperative Player'):
                p.update_beliefs(cardPlayed, round_suit, player)

    def play_round(self, num_round) -> dict[str, str]:
        '''
            Play a round of the game
        '''

        roundSuit = ''
        round_info = {}
        cardsPlayedInround = []

        # For each player
        for i, player in enumerate(self.playersOrder):
            match player.get_strategy():
                case 'Maximize Points Won' | 'Maximize Rounds Won':
                    card_played, roundSuit = player.play_round(i, cardsPlayedInround, roundSuit, self.playersOrder, self, self.mode)
                case 'Deck Predictor' | 'Cooperative Player':
                    card_played, roundSuit = player.play_round(i, cardsPlayedInround, roundSuit, self.playersOrder, self, self.mode, num_round)
                case _:
                    card_played, roundSuit = player.play_round(i, roundSuit, self.mode)

            # In human mode, print the cards played by the player and let him chose
            if player.name == 'Leitao' and self.mode == 'human':
                # Put the card played back in the hand
                player.add_card(card_played)

                print(colored(f'Your current hand:', 'yellow'))
                for card in player.hand:
                    print(colored(card.name, attrs=['bold']))
                print('\nThe engine suggests you play', end=' ')
                print(colored(card_played.name, 'blue', attrs=['bold']))
                # Wait for user input
                while True:
                    try:
                        card_name = input(colored('> ', attrs=['bold']))
                    except KeyboardInterrupt:
                        print(colored('\nGoodbye!', 'blue'))
                        exit(0)

                    card_played = player.get_card(card_name)
                    if card_played:
                        break
                    print(colored('Invalid card! Try again', 'red'))

                if i == 0:
                    roundSuit = card_played.suit

                # Remove the card played from the hand
                player.hand.remove(card_played)
                print(colored(f'You played {card_played.name}', 'green', attrs=['bold']))

            # Add the card played to the list of cards played in the round
            cardsPlayedInround.append(card_played)

            # Update the beliefs of the players
            self.update_beliefs(card_played, roundSuit, player)

            # If the round is in human mode, wait for 5 seconds
            if self.mode == 'human':
                sleep(5)

        # Get the total points played in the round and the respective winner
        roundPoints, winnerId = self.calculate_round_points(cardsPlayedInround)

        round_info["Winner"] = self.playersOrder[winnerId[1]].name
        round_info["Points"] = roundPoints

        playerWinnerOfRound = self.playersOrder[winnerId[1]]
        playerWinnerOfRound.team.score += roundPoints

        if self.verbose or self.mode == 'human':
            print(colored('You win the round' if playerWinnerOfRound.name == 'Leitao' else playerWinnerOfRound.name + " wins the round", 'blue', attrs=['bold']))

        # Rotate the players order to the winner of the round
        self.playersOrder = self.rotate_order_to_winner(self.playersOrder, playerWinnerOfRound)

        return round_info

    def play_game(self) -> dict[str, str]:
        '''
            Play the game of Sueca
        '''

        # For each of the 10 rounds
        for num_rounds in range(10):
            if self.verbose or self.mode == 'human':
                print(colored("\nRound " + str(num_rounds + 1) + ":", 'green', attrs=['underline']))

            round_info = self.play_round(num_rounds)
            (self.game_info["Rounds"])[num_rounds + 1] = round_info

        # Print the final game details
        if self.verbose or self.mode == 'human':
            print(colored("\nSporting score: " + str(self.teams[0].score), 'green'))
            print(colored("Benfica score: " + str(self.teams[1].score), 'red'))
        self.game_info["Teams"] = [self.teams[0].dump_to_json(), self.teams[1].dump_to_json()]
        if self.teams[0].score > self.teams[1].score:
            if self.verbose or self.mode == 'human':
                print()
                print(colored("Sporting wins", 'white', 'on_green'))
            return self.teams[0].name
        elif self.teams[0].score == self.teams[1].score:
            if self.verbose or self.mode == 'human':
                print()
                print(colored("It's a tie!", 'white', 'on_dark_grey'))
            return "ties"
        else:
            if self.verbose or self.mode == 'human':
                print()
                print(colored("Benfica wins!", 'white', 'on_red'))
            return self.teams[1].name
