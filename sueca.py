############################################# Libraries #############################################

import json
from Game import Game
import argparse
from termcolor import colored

def parse_arguments():
    parser = argparse.ArgumentParser(description='Sueca game simulator')

    parser.add_argument('--o', '-output', type=str, required=True, help='Output file to save the game log')
    parser.add_argument('--t1', '-team_1', type=str, required=True, help='Strategy for team 1')
    parser.add_argument('--t2', '-team_2', type=str, required=True, help='Strategy for team 2')
    parser.add_argument('--n', '-num_games', type=int, default=1, help='Number of games to simulate')

    return parser.parse_args()

########################################## Main Program #############################################

if __name__ == "__main__":
    args = parse_arguments()
    print(args)

    wins = {'Benfica': 0, 'Sporting': 0, 'ties': 0}

    for i in range(args.n):
        print(f'\nGame {i+1}')

        # Initialize the game
        game = Game(args.t1, args.t2)

        # Distribute the cards
        game.hand_cards()

        # Play the game
        winner = game.play_game()
        wins[winner] += 1

        with open(args.o, 'w') as f:
            json.dump(game.game_info, f, indent = 4)
        print(f'\nGame log saved to {args.o}')

    print(colored(f'\nWins: {wins}', 'magenta', attrs=['bold']))
