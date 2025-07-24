from bid import Bid
from card import Card, SUITS, RANKS, parse_card
from hand_evaluator import describe_hand
from pathlib import Path
from typing import List, Dict, Any
import datetime
import json

def save_json(data: Any, folder: str = "data", prefix: str = "output") -> str:
    Path(folder).mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(folder) / f"{prefix}_{timestamp}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return str(path)

def generate_deck() -> List[Card]:
    """Generate a full 52-card deck."""
    return [Card(rank, suit) for suit in SUITS for rank in RANKS]

def remove_known_cards(deck: List[Card], known: List[Card]) -> List[Card]:
    """Remove known cards from a deck."""
    return [card for card in deck if card not in known]

def parse_card_list(card_strs: List[str]) -> List[Card]:
    """Convert a list of card string descriptions to Card objects."""
    return [parse_card(cs) for cs in card_strs if parse_card(cs) is not None]

def format_bid(bid: Bid) -> str:
    if bid.hand_type in ["Straight", "Straight Flush"]:
        if bid.range_start is not None and bid.range_end is not None:
            high = bid.range_start
            low = bid.range_end
            if high == 14 and low == 5:
                value_list = list(range(5, 15))
            else:
                value_list = list(range(max(low, high), min(low, high) - 1, -1))
        else:
            value_list = []
    elif bid.hand_type == "Royal Flush":
        value_list = [10, 11, 12, 13, 14]
    else:
        value_list = [v for v in [bid.primary, bid.secondary] if v is not None]

    if not value_list:
        return bid.hand_type
    return describe_hand(bid.hand_type, value_list, [bid.suit] if bid.suit else None)

def format_simulation_for_ml(
    hand: List[Card],
    bid: Dict[str, Any],
    total_cards: int,
    threshold: float,
    results: Dict[str, Any]
) -> Dict[str, Any]:
    def parse_hand_key(key: str) -> Dict[str, Any]:
        try:
            parts = key.split(", ")
            base = {"type": parts[0]}
            for part in parts[1:]:
                if part.startswith("High "):
                    base["high_card"] = part.replace("High ", "")
                elif part in ["Hearts", "Spades", "Diamonds", "Clubs"]:
                    base["suit"] = part
                elif part.endswith("s"):
                    base["primary_rank"] = part.replace("s", "")
            return base
        except Exception as e:
            return {"type": "Unknown", "raw": key}

    stronger_hands = []
    for label, count in results["matching_hands"].items():
        parsed = parse_hand_key(label)
        parsed["frequency"] = count / results["total_samples"]
        stronger_hands.append(parsed)

    return {
        "inputs": {
            "hand": [str(c) for c in hand],
            "bid": bid,
            "total_cards": total_cards,
            "threshold": threshold
        },
        "outputs": {
            "presence_probability": results.get("presence_probability", 0),
            "stronger_hands": stronger_hands,
            "suggestion": (
                "Raise" if any(
                    (count / results["total_samples"]) >= threshold
                    for count in results["matching_hands"].values()
                ) else "Call BS or Bluff"
            )
        }
    }