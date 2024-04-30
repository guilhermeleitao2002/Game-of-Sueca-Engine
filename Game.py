class Game:
    '''
        Game ->
            - teams: list of Team objects
            - strategy: game strategy
            - playersOrder: list of Player objects sorted by order to play
            - deck: list of Card objects
            - trump: trump card for that game
    '''
    
    def __init__ (self, teams, strategy) -> None:
        self.teams = teams
        self.strategy = strategy
        self.playersOrder = []
        self.deck = []
        self.trump = None
