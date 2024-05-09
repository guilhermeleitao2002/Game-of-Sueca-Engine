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

    def __eq__(self, value: 'Card') -> bool:
        return self.name == value.name and self.suit == value.suit and\
            self.rank == value.rank and self.order == value.order and\
            self.value == value.value
