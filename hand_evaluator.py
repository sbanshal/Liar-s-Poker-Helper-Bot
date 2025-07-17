from collections import Counter
from functools import lru_cache
from card import Card, RANK_VALUES
from typing import List, Tuple
from constants import VALUE_TO_RANK_NAME, RANK_NAME_TO_VALUE, HAND_RANKS, SUITS

@lru_cache(maxsize=None)
def evaluate_hand_cached(values_tuple: Tuple[int, ...], suits_tuple: Tuple[str, ...]) -> Tuple[str, List[int]]:
    values = sorted(values_tuple, reverse=True)
    suits = list(suits_tuple)
    value_counts = Counter(values)
    unique_values = sorted(set(values), reverse=True)
    is_flush = len(set(suits)) == 1
    is_straight = len(unique_values) == 5 and unique_values[0] - unique_values[4] == 4

    if set(values) == {14, 2, 3, 4, 5}:
        is_straight = True
        values = [5, 4, 3, 2, 14]

    if is_flush and is_straight:
        return ('Straight Flush', values)
    elif 4 in value_counts.values():
        four = [val for val, count in value_counts.items() if count == 4]
        kicker = [val for val in values if val not in four]
        return ('Four of a Kind', four + kicker)
    elif 3 in value_counts.values() and 2 in value_counts.values():
        three = [val for val, count in value_counts.items() if count == 3]
        pair = [val for val, count in value_counts.items() if count == 2]
        return ('Full House', three + pair)
    elif is_flush:
        return ('Flush', values)
    elif is_straight:
        return ('Straight', values)
    elif 3 in value_counts.values():
        trips = [val for val, count in value_counts.items() if count == 3]
        kickers = [val for val in values if val not in trips]
        return ('Three of a Kind', trips + kickers)
    elif list(value_counts.values()).count(2) == 2:
        pairs = sorted([val for val, count in value_counts.items() if count == 2], reverse=True)
        kicker = [val for val in values if val not in pairs]
        return ('Two Pair', pairs + kicker)
    elif 2 in value_counts.values():
        pair = [val for val, count in value_counts.items() if count == 2]
        kickers = [val for val in values if val not in pair]
        return ('One Pair', pair + kickers)
    else:
        return ('High Card', values)
    
def evaluate_hand_from_tuples(card_tuples: List[Tuple[int, str]]) -> Tuple[str, List[int]]:
    """Evaluate hand from (value, suit) tuples"""
    values = tuple(sorted((t[0] for t in card_tuples), reverse=True))
    suits = tuple(t[1] for t in card_tuples)
    return evaluate_hand_cached(values, suits)

def evaluate_hand(cards: List[Card]) -> Tuple[str, List[int]]:
    assert len(cards) == 5, "Must evaluate exactly 5 cards"
    values_tuple = tuple(sorted([card.value for card in cards], reverse=True))
    suits_tuple = tuple(card.suit for card in cards)
    return evaluate_hand_cached(values_tuple, suits_tuple)

def describe_hand(hand_type: str, values: List[int], suits: List[str] = None) -> str:
    if hand_type in ["One Pair", "Three of a Kind", "Four of a Kind"]:
        return f"{hand_type}, {VALUE_TO_RANK_NAME[values[0]]}s"
    elif hand_type == "Two Pair":
        return f"{hand_type}, {VALUE_TO_RANK_NAME[values[0]]}s and {VALUE_TO_RANK_NAME[values[1]]}s"
    elif hand_type == "Full House":
        return f"{hand_type}, {VALUE_TO_RANK_NAME[values[0]]}s over {VALUE_TO_RANK_NAME[values[1]]}s"
    elif hand_type == "Straight":
        return f"{hand_type}, {VALUE_TO_RANK_NAME[values[-1]]} to {VALUE_TO_RANK_NAME[values[0]]}"
    elif hand_type == "Flush":
        if suits:
            return f"{hand_type}, {suits[0]}, high {VALUE_TO_RANK_NAME[values[0]]}"
        else:
            return f"{hand_type}, high {VALUE_TO_RANK_NAME[values[0]]}"
    elif hand_type == "Straight Flush":
        if suits:
            return f"{hand_type}, {suits[0]}, {VALUE_TO_RANK_NAME[values[-1]]} to {VALUE_TO_RANK_NAME[values[0]]}"
        else:
            return f"{hand_type}, {VALUE_TO_RANK_NAME[values[-1]]} to {VALUE_TO_RANK_NAME[values[0]]}"
    else:
        return f"{hand_type}, high {VALUE_TO_RANK_NAME[values[0]]}"