############################################# Libraries #############################################

import json
import sys
from Game import Game


########################################## Main Program #############################################

if __name__ == "__main__":
    output_file = sys.argv[1]
    team_1_strategy = sys.argv[2]
    team_2_strategy = sys.argv[3]

    # Initialize the game
    game = Game(team_1_strategy, team_2_strategy)

    # Distribute the cards
    game.hand_cards()

    # Play the game
    game.play_game()

    with open(output_file, 'w') as f:
        json.dump(game.game_info, f, indent = 4)
    print(f'Game log saved to {output_file}')
