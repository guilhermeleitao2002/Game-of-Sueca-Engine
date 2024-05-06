############################################# Libraries #############################################

import json
import sys
from Game import Game


########################################## Main Program #############################################

if __name__ == "__main__":
    output_file = sys.argv[1]

    # Initialize the game
    game = Game(sys.argv[2])

    # Distribute the cards
    game.hand_cards()

    # Play the game
    game.play_game()

    with open(output_file, 'w') as f:
        json.dump(game.game_info, f, indent = 4)
    print(f'Game log saved to {output_file}')
