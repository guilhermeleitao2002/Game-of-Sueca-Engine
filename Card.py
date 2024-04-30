class Card:
    '''
        Card ->
            - name: card name
            - suit: card suit (hearts, diamonds, clubs, spades)
            - rank: card rank (2, 3, 4, 5, 6, 7, J, Q, K, A)
            - order: card order (0 - 10)
            - value: card value (0, 2, 3, 4, 10, 11)
    '''
    
    def __init__ (self, name, suit, rank) -> None:
        self.name = name
        self.suit = suit
        self.rank = rank
        self.order = 0
        self.value = 0
