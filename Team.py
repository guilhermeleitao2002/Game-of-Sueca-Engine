class Team:
    ''' 
        Team ->
            - name: team name
            - players: list of Player objects
            - score: team score (0 - 120)
            - add_player(player): add player to team
    '''
    
    def __init__ (self, name) -> None:
        self.name = name
        self.players = []
        self.score = 0
    
    def add_player(self, player) -> None:
        self.players.append(player)
