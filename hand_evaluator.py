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
    is_straight = (
        len(unique_values) == 5 and unique_values[0] - unique_values[4] == 4
    ) or unique_values == [14, 13, 12, 11, 10]

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
    def plural(rank: str):
        return rank + "s"

    VALUE_TO_RANK_NAME = {
        2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
        7: "7", 8: "8", 9: "9", 10: "10",
        11: "J", 12: "Q", 13: "K", 14: "A"
    }

    rank0 = VALUE_TO_RANK_NAME[values[0]]
    rank1 = VALUE_TO_RANK_NAME[values[1]] if len(values) > 1 else None
    low = VALUE_TO_RANK_NAME[values[-1]]

    if hand_type == "High Card":
        return f"{hand_type}, High {rank0}"
    elif hand_type == "One Pair":
        return f"{hand_type}, {plural(rank0)}"
    elif hand_type == "Two Pair":
        return f"{hand_type}, {plural(rank0)} and {plural(rank1)}"
    elif hand_type == "Three of a Kind":
        return f"{hand_type}, {plural(rank0)}"
    elif hand_type == "Straight":
        return f"{hand_type}, {low} to {rank0}"
    elif hand_type == "Flush":
        return f"{hand_type}, {suits[0]}, High {rank0}" if suits else f"{hand_type}, high {rank0}"
    elif hand_type == "Full House":
        return f"{hand_type}, {plural(rank0)} over {plural(rank1)}"
    elif hand_type == "Four of a Kind":
        return f"{hand_type}, {plural(rank0)}"
    elif hand_type == "Straight Flush":
        return f"{hand_type}, {suits[0]}, {low} to {rank0}" if suits else f"{hand_type}, {low} to {rank0}"
    elif hand_type == "Royal Flush":
        return f"{hand_type}, {suits[0]}, 10 to A" if suits else f"{hand_type}, 10 to A"
    else:
        return f"{hand_type}, high {rank0}"
