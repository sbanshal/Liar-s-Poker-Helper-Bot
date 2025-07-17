import unittest
from bid import parse_bid, Bid

class TestBidParsing(unittest.TestCase):
    def test_one_pair(self):
        bid = parse_bid("One Pair, Jacks")
        self.assertEqual(bid.hand_type, "One Pair")
        self.assertEqual(bid.primary, 11)

    def test_two_pair(self):
        bid = parse_bid("Two Pair, Kings and Fours")
        self.assertEqual(bid.hand_type, "Two Pair")
        self.assertEqual(bid.primary, 13)
        self.assertEqual(bid.secondary, 4)

    def test_full_house(self):
        bid = parse_bid("Full House, Queens over Twos")
        self.assertEqual(bid.hand_type, "Full House")
        self.assertEqual(bid.primary, 12)
        self.assertEqual(bid.secondary, 2)

    def test_straight(self):
        bid = parse_bid("Straight, 5 to 9")
        self.assertEqual(bid.hand_type, "Straight")
        self.assertEqual(bid.range_start, 5)
        self.assertEqual(bid.range_end, 9)

    def test_flush(self):
        bid = parse_bid("Flush, Spades, high King")
        self.assertEqual(bid.hand_type, "Flush")
        self.assertEqual(bid.primary, 13)
        self.assertEqual(bid.suit, "Spades")

    def test_straight_flush(self):
        bid = parse_bid("Straight Flush, 3 to 7 of Hearts")
        self.assertEqual(bid.hand_type, "Straight Flush")
        self.assertEqual(bid.range_start, 3)
        self.assertEqual(bid.range_end, 7)
        self.assertEqual(bid.suit, "Hearts")

    def test_invalid_rank_parsing(self):
        with self.assertRaises(ValueError):
            parse_bid("One Pair of")

    def test_invalid_hand_type(self):
        with self.assertRaises(ValueError):
            parse_bid("Combo Flush and Pair")

class TestBidComparison(unittest.TestCase):
    def test_hand_type_comparison(self):
        b1 = parse_bid("One Pair, Jacks")
        b2 = parse_bid("Two Pair, Threes and Fours")
        self.assertTrue(b2.beats(b1))

    def test_same_type_higher_primary(self):
        b1 = parse_bid("Three of a Kind, Tens")
        b2 = parse_bid("Three of a Kind, Queens")
        self.assertTrue(b2.beats(b1))

    def test_same_type_lower_primary(self):
        b1 = parse_bid("One Pair, Kings")
        b2 = parse_bid("One Pair, Jacks")
        self.assertFalse(b2.beats(b1))

    def test_full_house_comparison(self):
        b1 = parse_bid("Full House, Tens over Twos")
        b2 = parse_bid("Full House, Queens over Threes")
        self.assertTrue(b2.beats(b1))

    def test_two_pair_secondary_comparison(self):
        b1 = parse_bid("Two Pair, Aces and Threes")
        b2 = parse_bid("Two Pair, Aces and Nines")
        self.assertTrue(b2.beats(b1))

    def test_equal_bids(self):
        b1 = parse_bid("Three of a Kind, Kings")
        b2 = parse_bid("Three of a Kind, Kings")
        self.assertFalse(b2.beats(b1))

if __name__ == '__main__':
    unittest.main()