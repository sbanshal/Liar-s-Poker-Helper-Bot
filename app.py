
import streamlit as st
from simulator import simulate_presence_probability
from bid import parse_bid
from utils import parse_card_list
from constants import HAND_RANKS
import json
import time
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['font.family'] = ['EB Garamond', 'serif']

st.set_page_config(page_title="Liar's Poker Bid Helper", layout="wide")

# Constants
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
hand_types = [
    "High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight",
    "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"
]

# Bid Section
def render_bid_section():
    st.markdown("### Select the last bid you must respond to:")
    hand_type = st.selectbox("Hand Type", hand_types)
    bid_str = ""

    hand_images = {
        "High Card": "high_card.png",
        "One Pair": "pair.png",
        "Two Pair": "two_pair.png",
        "Three of a Kind": "three_of_a_kind.png",
        "Straight": "straight.png",
        "Flush": "flush.png",
        "Full House": "full_house.png",
        "Four of a Kind": "four_of_a_kind.png",
        "Straight Flush": "straight_flush.png",
        "Royal Flush": "royal_flush.png"
    }

    image_path = f"images/{hand_images[hand_type]}"
    st.image(image_path, use_container_width=True)

    if hand_type == "One Pair":
        primary = st.selectbox("Rank of the Pair", ranks)
        bid_str = f"One Pair, {primary}s"
    elif hand_type == "Two Pair":
        primary = st.selectbox("First Pair Rank", ranks)
        secondary = st.selectbox("Second Pair Rank", [r for r in ranks if r != primary])
        bid_str = f"Two Pair, {primary}s and {secondary}s"
    elif hand_type == "Three of a Kind":
        primary = st.selectbox("Rank for Trips", ranks)
        bid_str = f"Three of a Kind, {primary}s"
    elif hand_type == "Straight":
        start = st.selectbox("Straight Start", ["A"] + ranks[:9])
        if start in ["J", "Q", "K"]:
            st.error("Straight cannot start at Jack or higher.")
        end = "5" if start == "A" else ranks[ranks.index(start) + 4]
        bid_str = f"Straight, {start} to {end}"
    elif hand_type == "Flush":
        high_card = st.selectbox("High Card", ranks[4:])
        suit = st.selectbox("Suit", suits)
        bid_str = f"Flush, {suit}, high {high_card}"
    elif hand_type == "Full House":
        trips = st.selectbox("Trips Rank", ranks)
        pair = st.selectbox("Pair Rank", [r for r in ranks if r != trips])
        bid_str = f"Full House, {trips}s over {pair}s"
    elif hand_type == "Four of a Kind":
        primary = st.selectbox("Quads Rank", ranks)
        bid_str = f"Four of a Kind, {primary}s"
    elif hand_type == "Straight Flush":
        start = st.selectbox("Straight Flush Start", ["A"] + ranks[:8])
        if start == "10":
            st.error("Start at 10 is reserved for Royal Flush.")
        end = "5" if start == "A" else ranks[ranks.index(start) + 4]
        suit = st.selectbox("Suit", suits)
        bid_str = f"Straight Flush, {start} to {end} of {suit}"
    elif hand_type == "Royal Flush":
        suit = st.selectbox("Suit", suits)
        bid_str = f"Straight Flush, 10 to A of {suit}"
    else:
        high = st.selectbox("High Card Rank", ranks)
        bid_str = f"High Card, {high}"

    st.subheader(f"Last Bid: {bid_str}")
    return bid_str

# Card Input Section
def render_card_input_section():
    st.markdown("### Your Cards")
    card_count = st.slider("Number of cards in your hand:", 1, 10, 4)
    cards = []

    for i in range(card_count):
        with st.container():
            st.markdown(f"<div style='font-weight:600; font-size:16px;'>Card {i+1}</div>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                rank = st.selectbox("Rank", ranks, key=f"rank_{i}")
            with col2:
                suit = st.selectbox("Suit", suits, key=f"suit_{i}")
            cards.append(f"{rank} of {suit}")

    if len(cards) != len(set(cards)):
        st.error("Duplicate cards detected in your hand. Each card must be unique.")

    st.markdown("#### Your Hand:")
    st.markdown(", ".join(cards))
    return cards

# Game Settings Section
def render_game_settings():
    st.markdown("### Game Parameters")
    col1, col2 = st.columns(2)
    with col1:
        total_cards = st.number_input("Total cards in play:", min_value=5, max_value=52, value=20)
    with col2:
        thresh = st.slider("Probability threshold", 0.0, 1.0, 0.50, 0.01)

    sample_override = st.number_input(
        "Sample Count", min_value=1_000, max_value=10_000, step=100, value=1_000
    )

    est_sec = sample_override / 100  # Example: 5000 → 50s
    est_min = est_sec / 60

    if est_min < 1:
        st.caption(f"Estimated runtime: ~{int(est_sec)} seconds")
    else:
        st.caption(f"Estimated runtime: ~{round(est_min, 1)} minutes")
        st.caption(f"Estimated runtime: ~{est_min} min")

    return total_cards, thresh, sample_override

# Main App
st.title("Liar's Poker – Bid Helper")
st.caption("Use this tool to decide whether to challenge or raise the last bid in play.")

with st.expander("Game Instructions (click to expand)", expanded=False):
    st.markdown("""
    - A bid is a claim that *at least one* valid 5-card poker hand of that strength exists in the pool.
    - On your turn: Raise with a stronger hand or Call BS.
    - The simulation tells you if stronger hands are likely enough to justify raising.
    """)

bid_str = render_bid_section()
your_cards = render_card_input_section()
total_cards, thresh, sample_override = render_game_settings()

st.divider()

if st.button("Simulate and Decide"):
    try:
        parsed_cards = parse_card_list(your_cards)
        parsed_bid = parse_bid(bid_str)

        with st.spinner("Simulating... This may take a few seconds."):
            start = time.time()
            results = simulate_presence_probability(
                known_cards=parsed_cards,
                total_cards_in_play=total_cards,
                last_bid=parsed_bid,
                threshold=thresh,
                show_timing=True,
                max_samples=sample_override
            )
            dist = results.get("hand_type_distribution", {})
            elapsed = results.get("elapsed_time", time.time() - start)

            presence_prob = results.get("presence_probability", 0)
            st.subheader(f"Probability a stronger hand exists: {presence_prob * 100:.2f}%")

            matching = results.get("matching_hands", {})
            if matching:
                st.success("Stronger hand(s) likely exist. Suggestion: Call BS or Raise.")
                st.markdown("### Stronger Hands Found in Pools (Above Threshold):")

            total = results["total_samples"]
            filtered_matches = {
                hand: count for hand, count in matching.items()
                if (count / total) >= thresh
            }

            if not filtered_matches:
                st.info("No stronger hands exceeded the threshold.")
            else:
                for hand, count in sorted(filtered_matches.items(), key=lambda x: -(x[1] / total)):
                    prob = count / total
                    st.write(f"- {hand} — {prob * 100:.1f}%")

                filtered_json = json.dumps(
                    {hand: round(count / total, 4) for hand, count in filtered_matches.items()},
                    indent=2
                )
                st.download_button(
                    "Download Filtered Results (JSON)",
                    data=filtered_json,
                    file_name="filtered_matching_hands.json",
                    mime="application/json"
                )

        st.caption(f"Simulation completed in {elapsed:.2f} seconds")

        if dist:
            st.markdown("### Hand Type Frequency:")
            fig, ax = plt.subplots(figsize=(10, 4))
            ordered_labels = sorted(dist.items(), key=lambda x: HAND_RANKS.get(x[0], 0))
            labels = [label for label, _ in ordered_labels]
            values = [count for _, count in ordered_labels]
            colors = plt.cm.magma([i / len(labels) for i in range(len(labels))])

            ax.bar(labels, values, color=colors, width=0.5, edgecolor='black')
            ax.set_ylabel("Count", fontsize=12, labelpad=8)
            ax.set_xlabel("Hand Type", fontsize=12, labelpad=8)
            ax.set_title("Hand Type Distribution", fontsize=16, fontweight='bold', pad=12)
            ax.set_xticklabels(labels, rotation=25, ha='right', fontsize=10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error during simulation: {e}")
