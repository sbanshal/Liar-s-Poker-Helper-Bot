SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

RANK_NAME_TO_VALUE = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Jacks': 11, 'Q': 12, 'Queens': 12,
    'K': 13, 'Kings': 13, 'A': 14, 'Aces': 14
}

VALUE_TO_RANK_NAME = {v: k for k, v in RANK_NAME_TO_VALUE.items()}

HAND_RANKS = {
    'High Card': 0,
    'One Pair': 1,
    'Two Pair': 2,
    'Three of a Kind': 3,
    'Straight': 4,
    'Flush': 5,
    'Full House': 6,
    'Four of a Kind': 7,
    'Straight Flush': 8,
    'Royal Flush': 9
}

HAND_TYPES = list(HAND_RANKS.keys())

RANK_TO_VALUE = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 11, "Q": 12, "K": 13, "A": 14
}