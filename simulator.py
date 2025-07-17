import random
import time
import math
from collections import Counter
from typing import List, Dict
from itertools import combinations
from tqdm import tqdm

from card import Card
from utils import generate_deck, remove_known_cards
from hand_evaluator import evaluate_hand_from_tuples, describe_hand
from bid import Bid
from constants import HAND_RANKS

# Constants
DEFAULT_MC_SAMPLES = 1_000
CONFIDENCE_EPSILON = 0.01

# ---- Core Simulator ----

def simulate_presence_probability(
    known_cards: List[Card],
    total_cards_in_play: int,
    last_bid: Bid,
    threshold: float = 0.05,
    max_samples: int = DEFAULT_MC_SAMPLES,
    show_timing: bool = True
) -> Dict:

    start_time = time.time()
    deck = generate_deck()
    remaining_deck = remove_known_cards(deck, known_cards)
    cards_to_draw = total_cards_in_play - len(known_cards)

    if cards_to_draw < 0:
        raise ValueError("More known cards than total cards in play.")

    hit_count = 0
    total_samples = 0
    matching_hands = Counter()

    if len(known_cards) >= 5:
        seen_this_pool = set()
        for hand in combinations(known_cards, 5):
            hand_type, hand_vals = evaluate_hand_from_tuples([(c.value, c.suit) for c in hand])
            if beats_bid_direct(hand_type, hand_vals, last_bid):
                desc = describe_hand(hand_type, hand_vals, [c.suit for c in hand])
                if desc not in seen_this_pool:
                    matching_hands[desc] += 1
                    seen_this_pool.add(desc)

        if seen_this_pool:
            hit_count += 1

    for _ in tqdm(range(max_samples), desc="Presence Monte Carlo"):
        draw = random.sample(remaining_deck, cards_to_draw)
        pool = known_cards + draw

        seen_this_pool = set()
        for hand in combinations(pool, 5):
            hand_type, hand_vals = evaluate_hand_from_tuples([(c.value, c.suit) for c in hand])
            if beats_bid_direct(hand_type, hand_vals, last_bid):
                desc = describe_hand(hand_type, hand_vals, [c.suit for c in hand])
                if desc not in seen_this_pool:
                    matching_hands[desc] += 1
                    seen_this_pool.add(desc)

        if seen_this_pool:
            hit_count += 1

        total_samples += 1


    presence_probability = hit_count / total_samples if total_samples else 0

    if show_timing:
        print(f"[Presence Mode] {hit_count} / {total_samples} pools had stronger hands")
        print(f"→ Presence probability: {presence_probability:.4f}")

    return {
        "presence_probability": presence_probability,
        "matching_hands": dict(matching_hands),
        "total_samples": total_samples,
        "elapsed_time": time.time() - start_time
    }

# ---- Comparison Logic ----

def beats_bid_direct(hand_type: str, hand_values: List[int], bid: Bid) -> bool:
    hand_rank = HAND_RANKS[hand_type]
    bid_rank = HAND_RANKS[bid.hand_type]

    if hand_rank > bid_rank:
        return True
    elif hand_rank < bid_rank:
        return False

    # Tie-breakers by hand type
    if hand_type in ["One Pair", "Three of a Kind", "Four of a Kind"]:
        return hand_values[0] > (bid.primary or 0)
    elif hand_type == "Two Pair":
        return (hand_values[0], hand_values[1]) > (bid.primary or 0, bid.secondary or 0)
    elif hand_type == "Full House":
        return (hand_values[0], hand_values[1]) > (bid.primary or 0, bid.secondary or 0)
    elif hand_type in ["Straight", "Straight Flush"]:
        return hand_values[0] > (bid.range_end or 0)
    elif hand_type == "Flush":
        return hand_values[0] > (bid.primary or 0)
    else:  # High Card
        return hand_values[0] > (bid.primary or 0)