from typing import Optional
from constants import VALUE_TO_RANK_NAME, RANK_NAME_TO_VALUE, HAND_RANKS, SUITS

BID_ALIASES = {
    "2s": "2", "3s": "3", "4s": "4", "5s": "5", "6s": "6", "7s": "7", "8s": "8", "9s": "9", "10s": "10",
    "Twos": "2", "Threes": "3", "Fours": "4", "Fives": "5", "Sixes": "6", "Sevens": "7",
    "Eights": "8", "Nines": "9", "Tens": "10",
    "Js": "Jacks", "Qs": "Queens", "Ks": "Kings", "As": "Aces",
    "Jacks": "Jacks", "Queens": "Queens", "Kings": "Kings", "Aces": "Aces",
    "Jack": "Jacks", "Queen": "Queens", "King": "Kings", "Ace": "Aces"
}

class Bid:
    def __init__(self, hand_type: str, primary: Optional[int] = None, secondary: Optional[int] = None,
                 suit: Optional[str] = None, range_start: Optional[int] = None, range_end: Optional[int] = None):
        if hand_type not in HAND_RANKS:
            raise ValueError(f"Invalid hand type: {hand_type}")
        self.hand_type = hand_type
        self.rank_value = HAND_RANKS[hand_type]
        self.primary = primary
        self.secondary = secondary
        self.suit = suit
        self.range_start = range_start
        self.range_end = range_end

    def beats(self, other: 'Bid') -> bool:
        if self.rank_value > other.rank_value:
            return True
        elif self.rank_value < other.rank_value:
            return False
        if self.primary and other.primary and self.primary > other.primary:
            return True
        elif self.primary == other.primary and self.secondary and other.secondary:
            return self.secondary > other.secondary
        elif self.range_end and other.range_end:
            return self.range_end > other.range_end
        return False

    def __repr__(self):
        parts = [self.hand_type]
        if self.hand_type in ["One Pair", "Three of a Kind", "Four of a Kind"]:
            parts.append(f"of {VALUE_TO_RANK_NAME.get(self.primary)}")
        elif self.hand_type == "Two Pair":
            parts.append(f"{VALUE_TO_RANK_NAME.get(self.primary)} and {VALUE_TO_RANK_NAME.get(self.secondary)}")
        elif self.hand_type == "Full House":
            parts.append(f"{VALUE_TO_RANK_NAME.get(self.primary)} over {VALUE_TO_RANK_NAME.get(self.secondary)}")
        elif self.hand_type in ["Straight", "Straight Flush"]:
            parts.append(f"{VALUE_TO_RANK_NAME.get(self.range_start)} to {VALUE_TO_RANK_NAME.get(self.range_end)}")
            if self.suit:
                parts.append(f"of {self.suit}")
        elif self.hand_type == "Flush":
            if self.suit:
                parts.append(f"{self.suit}, high {VALUE_TO_RANK_NAME.get(self.primary)}")
            else:
                parts.append(f"high {VALUE_TO_RANK_NAME.get(self.primary)}")
        return ", ".join(parts)

def parse_bid(bid_str: str) -> Bid:
    bid_str = bid_str.strip()
    tokens = bid_str.replace(",", "").split()
    hand_type = None
    primary = None
    secondary = None
    suit = None
    range_start = None
    range_end = None

    normalized = [BID_ALIASES.get(token, token) for token in tokens]

    if "Straight Flush" in bid_str:
        hand_type = "Straight Flush"
    elif "Four of a Kind" in bid_str:
        hand_type = "Four of a Kind"
    elif "Full House" in bid_str:
        hand_type = "Full House"
    elif "Flush" in bid_str:
        hand_type = "Flush"
    elif "Straight" in bid_str:
        hand_type = "Straight"
    elif "Three of a Kind" in bid_str:
        hand_type = "Three of a Kind"
    elif "Two Pair" in bid_str:
        hand_type = "Two Pair"
    elif "One Pair" in bid_str:
        hand_type = "One Pair"
    else:
        hand_type = "High Card"

    try:
        if hand_type in ["One Pair", "Three of a Kind", "Four of a Kind"]:
            for word in normalized:
                if word in RANK_NAME_TO_VALUE:
                    primary = RANK_NAME_TO_VALUE[word]
                    break
            if primary is None:
                raise ValueError(f"Could not parse primary rank from bid: '{bid_str}'")

        elif hand_type == "Two Pair":
            found = [RANK_NAME_TO_VALUE[word] for word in normalized if word in RANK_NAME_TO_VALUE]
            if len(found) >= 2:
                primary, secondary = found[:2]
            else:
                raise ValueError(f"Could not parse Two Pair ranks from bid: '{bid_str}'")

        elif hand_type == "Full House":
            found = [RANK_NAME_TO_VALUE[word] for word in normalized if word in RANK_NAME_TO_VALUE]
            if len(found) >= 2:
                primary, secondary = found[:2]
            else:
                raise ValueError(f"Could not parse Full House ranks from bid: '{bid_str}'")

        elif hand_type in ["Straight", "Straight Flush"]:
            found = [RANK_NAME_TO_VALUE[word] for word in normalized if word in RANK_NAME_TO_VALUE]
            if len(found) >= 2:
                range_start, range_end = found[:2]
            else:
                raise ValueError(f"Could not parse range for {hand_type}: '{bid_str}'")
            for word in SUITS:
                if word in normalized:
                    suit = word
                    break

        elif hand_type == "Flush":
            for word in normalized:
                if word in SUITS:
                    suit = word
                if word in RANK_NAME_TO_VALUE:
                    primary = RANK_NAME_TO_VALUE[word]
            if primary is None:
                raise ValueError(f"Could not parse high card for Flush: '{bid_str}'")

    except Exception as e:
        raise ValueError(f"Error parsing bid: {bid_str} — {e}")

    return Bid(hand_type, primary, secondary, suit, range_start, range_end)