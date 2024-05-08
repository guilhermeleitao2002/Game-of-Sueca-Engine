from Player import Player


class Team:
    '''
        Team ->
            - name: team name
            - players: list of Player objects
            - score: team score (0 - 120)
            - add_player(player): add player to team
    '''

    def __init__(self, name) -> None:
        self.name = name
        self.players = []
        self.score = 0

    def add_player(self, player: Player) -> None:
        '''
            Add player to the team
        '''

        self.players.append(player)

    def dump_to_json(self) -> dict[str, any]:
        '''
            Dump the team information to a dictionary
        '''

        team = {}
        team["name"] = self.name
        team["players"] = []
        # For each player
        for player in self.players:
            player_info = {}
            player_info["name"] = player.name
            player_info["strategy"] = player.get_strategy()
            team['players'].append(player_info)
        team['score'] = self.score

        return team
