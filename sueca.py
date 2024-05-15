############################################# Libraries #############################################

from json import dumps
from Game import Game
from argparse import ArgumentParser
from termcolor import colored
from matplotlib.pyplot import subplots, savefig, xticks


########################################## Helper Functions ##########################################

def parse_arguments():
    '''
        Parses the command line arguments
    '''

    parser = ArgumentParser(description='Sueca game simulator')

    parser.add_argument('-o', '--output', type=str, required=True, help='Output file to save the game log')
    parser.add_argument('-s', '--sporting', type=str, required=True, help=f'Strategy for team Sporting: {colored("random", "green", attrs=["bold"])}, {colored("maxpointswon", "green", attrs=["bold"])}, {colored("maxroundswon", "green", attrs=["bold"])}, {colored("cooperative", "green", attrs=["bold"])}, {colored("greedy", "green", attrs=["bold"])}, {colored("predictor", "green", attrs=["bold"])}')
    parser.add_argument('-b', '--benfica', type=str, required=True, help=f'Strategy for team Benfica: {colored("random", "green", attrs=["bold"])}, {colored("maxpointswon", "green", attrs=["bold"])}, {colored("maxroundswon", "green", attrs=["bold"])}, {colored("cooperative", "green", attrs=["bold"])}, {colored("greedy", "green", attrs=["bold"])}, {colored("predictor", "green", attrs=["bold"])}')
    parser.add_argument('-n', '--num_games', type=int, default=1, help='Number of games to simulate')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Print the game information as it unfolds')
    parser.add_argument('-m', '--mode', type=str, default='auto', help=f'Mode of the game: {colored("auto", "green", attrs=["bold"])} (machine vs machine) or {colored("human", "green", attrs=["bold"])} (machine vs user)')

    # the game mode can only be 'auto' or 'human'
    if parser.parse_args().mode not in ['auto', 'human'] or\
       parser.parse_args().sporting not in ['random', 'maxpointswon', 'maxroundswon', 'cooperative', 'greedy', 'predictor'] or\
       parser.parse_args().benfica not in ['random', 'maxpointswon', 'maxroundswon', 'cooperative', 'greedy', 'predictor']:
        # print the help message and exit
        parser.print_help()

    return parser.parse_args()

def plot_results(info, benfica_strat, sporting_strat):
    '''
        Plots the results of the games in a bar plot
    '''

    # Data to bar plot
    strategies = [benfica_strat, sporting_strat, 'ties']
    wins = [info['Benfica'], info['Sporting'], info['ties']]

    # Make it so that if some team has 0 wins, we remove entries from both lists
    for i in range(len(wins)):
        if wins[i] == 0:
            del wins[i]
            del strategies[i]

    # Plot
    _, ax = subplots()
    ax.bar(strategies, wins, color=['red', 'green', 'grey'])
    ax.set_ylabel('Wins')	
    ax.set_title('Game Results')
    xticks(rotation=15)

    # Save the plot
    savefig(f'./results/{sporting_strat}_{benfica_strat}.png')


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
            game = Game(args.sporting, args.benfica, verbose, args.mode)

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
        
        if args.mode == 'auto':
            plot_results(wins, args.benfica, args.sporting)

    except KeyboardInterrupt:
        print(colored('\nGoodbye!', 'blue'))
        exit(0)
