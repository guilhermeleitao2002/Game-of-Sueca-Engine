'''
    Player ->
        - name: player name
        - hand: list of Card objects the player has (initially 10)
        - team: team object to which the player belongs
        - add_card(card): add card to player hand and sort it by order
        - get_cards_by_suit(suit): get all cards of a given suit
'''
class Player:
    def __init__ (self, name, team) -> None:
        self.name = name 
        self.hand = []
        self.team = team

    def add_card(self, card) -> None:
        self.hand.append(card)
        self.hand = sorted(self.hand, key=lambda x: x.order)

    def get_cards_by_suit(self, suit) -> list:
        filtered_hand = []
        for card in self.hand:
            if card.suit == suit:
                filtered_hand.append(card)

        return filtered_hand