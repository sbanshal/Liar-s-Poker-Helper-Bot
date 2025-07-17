import argparse
import json
from utils import parse_card_list
from bid import parse_bid, Bid
from simulator import simulate_presence_probability
from datetime import datetime

def generate_filename(n, bid):
    safe_bid = str(bid).replace(' ', '').replace(',', '_').replace('of', '').replace('/', '')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    return f"ev_sim_{n}cards_{safe_bid}_{timestamp}.json"

def main():
    parser = argparse.ArgumentParser(description="Liar's Poker EV Simulator")
    parser.add_argument('--n', type=int, required=True, help='Total number of cards in play')
    parser.add_argument('--x', type=int, required=True, help='Number of cards you have')
    parser.add_argument('--cards', nargs='+', required=True, help='Your cards, e.g. "K of Hearts" "3 of Spades"')
    parser.add_argument('--bid', type=str, required=True, help='Last bid, e.g. "Two Pair, Jacks and Threes"')
    parser.add_argument('--threshold', type=float, default=0.50, help='Probability threshold to show')
    parser.add_argument('--save', nargs='?', const=True, default=False, help='Optional filename to save results (or leave blank to auto-name)')
    parser.add_argument('--debug-sample', type=int, help='Force a specific Monte Carlo sample size (overrides default)', default=None)

    args = parser.parse_args()

    your_cards = parse_card_list(args.cards)
    last_bid = parse_bid(args.bid)

    if len(your_cards) != args.x:
        print(f"Expected {args.x} cards but got {len(your_cards)} parsed cards.")
        return

    print(f"Running simulation with:")
    print(f"  Total cards in play: {args.n}")
    print(f"  Your cards: {your_cards}")
    print(f"  Last bid: {last_bid}")
    print(f"  Showing hands with >= {args.threshold * 100:.1f}% probability\n")

    results = simulate_presence_probability(
        known_cards=your_cards,
        total_cards_in_play=args.n,
        last_bid=last_bid,
        threshold=args.threshold,
        max_samples=args.debug_sample,
        show_timing=True
    )

    presence_prob = results.get("presence_probability", 0)
    print(f"\n📊 Presence Probability: {presence_prob * 100:.2f}%")

    matching_hands = results.get("matching_hands", {})
    if matching_hands:
        print("\n🔍 Matching Stronger Hands Found:")
        for hand, count in sorted(matching_hands.items(), key=lambda x: -x[1]):
            print(f"  {hand}: {count} hits")
    else:
        print("⚠️ No stronger hands found in sampled pools.")

    if args.save:
        filename = generate_filename(args.n, last_bid) if args.save is True else args.save
        out = {
            "params": {
                "n": args.n,
                "x": args.x,
                "cards": [str(c) for c in your_cards],
                "last_bid": str(last_bid),
                "threshold": args.threshold
            },
            "results": [
                {"hand": hand, "count": count}
                for hand, count in results.get("matching_hands", {}).items()
            ]

        }
        with open(filename, 'w') as f:
            json.dump(out, f, indent=2)
        print(f"Results saved to: {filename}")

if __name__ == '__main__':
    main()