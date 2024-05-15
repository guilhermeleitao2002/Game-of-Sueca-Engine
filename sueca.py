############################################# Libraries #############################################

from json import dumps
from Game import Game
from argparse import ArgumentParser
from termcolor import colored


########################################## Helper Functions ##########################################

def parse_arguments():
    parser = ArgumentParser(description='Sueca game simulator')

    parser.add_argument('-o', '--output', type=str, required=True, help='Output file to save the game log')
    parser.add_argument('-t1', '--team_1', type=str, required=True, help='Strategy for team 1: random, maxpointswon, maxroundswon, cooperative, greedy, predictor')
    parser.add_argument('-t2', '--team_2', type=str, required=True, help='Strategy for team 2: random, maxpointswon, maxroundswon, cooperative, greedy, predictor')
    parser.add_argument('-n', '--num_games', type=int, default=1, help='Number of games to simulate')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Print the game information as it unfolds')
    parser.add_argument('-m', '--mode', type=str, default='auto', help='Mode of the game: auto (machine vs machine) or human (machine vs user)')

    return parser.parse_args()


########################################## Main Program #############################################

if __name__ == "__main__":
    try:
        args = parse_arguments()
        verbose = args.verbose

        # Open and clean the output file
        with open(args.output, 'w') as f:
            f.write('[\n')

        wins = {'Benfica': 0, 'Sporting': 0, 'ties': 0}

        for i in range(args.num_games):
            if verbose:
                print(colored(f'\nGAME {i + 1}', 'green', attrs=['bold', 'underline']))

            # Initialize the game
            game = Game(args.team_1, args.team_2, verbose, args.mode)

            # If the game is in human mode, print the player's partner
            if args.mode == 'human':
                print(f'\nYour partner is {colored(game.get_partner("Leitao").name, "light_yellow")}')

            # Distribute the cards
            game.hand_cards()

            # Play the game
            winner = game.play_game()
            wins[winner] += 1

            with open(args.output, 'a') as f:
                game.game_info['Game'] = i + 1
                f.write(dumps(game.game_info, indent = 4, sort_keys=True) + f'{"," if i < args.num_games - 1 else ""}\n')

        # Close the output file
        with open(args.output, 'a') as f:
            f.write(']')

        print(colored(f'\nWins: {wins}', 'magenta', attrs=['bold']))

    except KeyboardInterrupt:
        print(colored('\nGoodbye!', 'blue'))
        exit(0)
