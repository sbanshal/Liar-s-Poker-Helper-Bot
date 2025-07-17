from card import Card, SUITS, RANKS, parse_card
from typing import List

def generate_deck() -> List[Card]:
    """Generate a full 52-card deck."""
    return [Card(rank, suit) for suit in SUITS for rank in RANKS]

def remove_known_cards(deck: List[Card], known: List[Card]) -> List[Card]:
    """Remove known cards from a deck."""
    return [card for card in deck if card not in known]

def parse_card_list(card_strs: List[str]) -> List[Card]:
    """Convert a list of card string descriptions to Card objects."""
    return [parse_card(cs) for cs in card_strs if parse_card(cs) is not None]
