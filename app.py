
import streamlit as st
from simulator import simulate_presence_probability
from bid import parse_bid
from utils import parse_card_list, format_bid, format_simulation_for_ml, save_json

from constants import HAND_RANKS, RANKS, SUITS, HAND_TYPES, RANK_TO_VALUE
import json
import time

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond&display=swap');

        html, body, [class*="st-"], .css-18e3th9, .css-1d391kg, .block-container {
            font-family: 'EB Garamond', serif !important;
        }

        h1, h2, h3, h4 {
            font-family: 'EB Garamond', serif !important;
            font-weight: 600;
        }

        .stSelectbox label, .stSlider label, .stNumberInput label {
            font-weight: 500;
            font-size: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .uniform-text {
        font-family: 'EB Garamond', serif;
        font-size: 15px;
        color: #DDDDDD;
        margin-bottom: 10px;
    }
    .uniform-text a {
        color: #77C0FF;
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Liar's Poker Bid Helper", layout="wide")

# Bid Section
def render_bid_section():
    st.markdown("### Select the last bid you must respond to:")
    hand_type = st.selectbox("Hand Type", HAND_TYPES, key="widget_hand_type")

    # Optional: show image
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
    st.image(f"images/{hand_images[hand_type]}", use_container_width=True)

    primary = secondary = suit = range_start = range_end = None

    if hand_type == "High Card":
        primary = RANK_TO_VALUE[st.selectbox("High Card Rank", RANKS, key="widget_highcard_rank")]
    elif hand_type == "One Pair":
        primary = RANK_TO_VALUE[st.selectbox("Rank of the Pair", RANKS, key="widget_pair_rank")]
    elif hand_type == "Two Pair":
        primary = RANK_TO_VALUE[st.selectbox("First Pair Rank", RANKS, key="widget_two_pair_first")]
        secondary = RANK_TO_VALUE[st.selectbox("Second Pair Rank", [r for r in RANKS if RANK_TO_VALUE[r] != primary], key="widget_two_pair_second")]
    elif hand_type == "Three of a Kind":
        primary = RANK_TO_VALUE[st.selectbox("Rank for Trips", RANKS, key="widget_trips_rank")]
    elif hand_type == "Straight":
        options = ["A"] + RANKS[:9]
        start = st.selectbox("Straight Start", options, key="widget_straightflush_start")
        range_start = RANK_TO_VALUE[start]
        range_end = 5 if start == "A" else range_start + 4
        if range_end > 14:
            range_end = 14
    elif hand_type == "Flush":
        primary = RANK_TO_VALUE[st.selectbox("High Card", RANKS[4:], key="widget_flush_high")]
        suit = st.selectbox("Suit", SUITS, key="widget_suit")
    elif hand_type == "Full House":
        primary = RANK_TO_VALUE[st.selectbox("Trips Rank", RANKS, key="widget_fullhouse_trips")]
        secondary = RANK_TO_VALUE[st.selectbox("Pair Rank", [r for r in RANKS if RANK_TO_VALUE[r] != primary], key="widget_fullhouse_pair")]
    elif hand_type == "Four of a Kind":
        primary = RANK_TO_VALUE[st.selectbox("Quads Rank", RANKS, key="widget_quads_rank")]
    elif hand_type == "Straight Flush":
        options = ["A"] + RANKS[:8]
        start = st.selectbox("Straight Start", options, key="widget_straightflush_start")
        suit = st.selectbox("Suit", SUITS, key="widget_suit")
        range_start = RANK_TO_VALUE[start]
        range_end = 5 if start == "A" else range_start + 4
        if range_end > 14:
            range_end = 14
    elif hand_type == "Royal Flush":
        suit = st.selectbox("Suit", SUITS, key="widget_suit")

    return hand_type, primary, secondary, suit, range_start, range_end

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
                rank = st.selectbox("Rank", RANKS, key=f"widget_card_rank_{i}")
            with col2:
                suit = st.selectbox("Suit", SUITS, key=f"widget_card_suit_{i}")
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
        total_cards = st.number_input("Total cards in play:", min_value=5, max_value=52, value=20, key="widget_total_cards")
    with col2:
        thresh = st.slider("Probability Threshold", 0.0, 1.0, 0.50, 0.01, key="widget_probability_threshold")

    sample_override = 1000

    return total_cards, thresh, sample_override

# Main App
st.title("Liar's Poker – Bid Helper")
st.caption("Use this tool to decide whether to challenge or raise the last bid in play.")

from bid import Bid
from hand_evaluator import describe_hand

hand_type, primary, secondary, suit, range_start, range_end = render_bid_section()

parsed_bid = Bid(
    hand_type=hand_type,
    primary=primary,
    secondary=secondary,
    suit=suit,
    range_start=range_start,
    range_end=range_end
)

if hand_type in ["Straight", "Straight Flush"]:
    if parsed_bid.range_start is not None and parsed_bid.range_end is not None:
        high = parsed_bid.range_start
        low = parsed_bid.range_end
        if hand_type in ["Straight", "Straight Flush"] and parsed_bid.range_start == 14 and parsed_bid.range_end == 5:
            value_list = list(range(5, 15)) 
        else:
            value_list = list(range(max(low, high), min(low, high) - 1, -1)) 
    else:
        value_list = []
elif hand_type == "Royal Flush":
    value_list = [10, 11, 12, 13, 14]
else:
    value_list = [v for v in [parsed_bid.primary, parsed_bid.secondary] if v is not None]

if not value_list:
    bid_str = hand_type
else:
    bid_str = describe_hand(
        hand_type=parsed_bid.hand_type,
        values=value_list,
        suits=[parsed_bid.suit] if parsed_bid.suit else None
    )

st.subheader(f"Last Bid: {bid_str}")

your_cards = render_card_input_section()
total_cards, thresh, _ = render_game_settings()
sample_override = 1000

st.divider()

if st.button("Simulate and Decide"):
    try:
        parsed_cards = parse_card_list(your_cards)

        progress_bar = st.progress(0)
        progress_placeholder = st.empty()

        def update_progress(current, total):
            percent = int(current / total * 100)
            progress_bar.progress(percent)
            progress_placeholder.markdown(f"**Progress:** {percent}% Complete")
        
        parsed_bid = parse_bid(bid_str)

        with st.spinner("Simulating... This may take a few minutes."):
            start = time.time()
            results = simulate_presence_probability(
                known_cards=parsed_cards,
                total_cards_in_play=total_cards,
                last_bid=parsed_bid,
                threshold=thresh,
                show_timing=True,
                max_samples=sample_override,
                progress_callback=update_progress
            )
            dist = results.get("hand_type_distribution", {})
            elapsed = results.get("elapsed_time", time.time() - start)

            progress_bar.empty()

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

                import os
                os.makedirs("data", exist_ok=True)

                bid_output = {
                    "hand_type": parsed_bid.hand_type,
                    "primary": parsed_bid.primary,
                    "secondary": parsed_bid.secondary,
                    "suit": parsed_bid.suit,
                    "range_start": parsed_bid.range_start,
                    "range_end": parsed_bid.range_end
                }

                ml_output = format_simulation_for_ml(
                    hand=parsed_cards,
                    bid=bid_output,
                    total_cards=total_cards,
                    threshold=thresh,
                    results=results
                )

                save_path = save_json(ml_output)

                # --- SEND TO CENTRAL FLASK COLLECTOR ---
                import requests

                try:
                    if "inputs" in ml_output and "outputs" in ml_output:
                        response = requests.post(
                            "https://liars-poker-uploader.onrender.com/upload",
                            json=ml_output
                        )
                        if response.ok:
                            uploaded = response.json()
                            filename = uploaded.get("file", "").split("/")[-1]
                            url = f"https://liars-poker-uploader.onrender.com/files/{filename}"

                            st.markdown(f"<div class='uniform-text'>Saved remotely as: uploaded_jsons/{filename}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='uniform-text'><a href='{url}' target='_blank'>View uploaded file</a></div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='uniform-text'>Saved locally as: {save_path}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='uniform-text'>Simulation completed in {elapsed:.2f} seconds</div>", unsafe_allow_html=True)
                        else:
                            st.warning(f"Upload failed: {response.status_code} — {response.text}")
                    else:
                        st.warning("Skipping upload: Simulation result is incomplete.")
                except Exception as e:
                    st.warning(f"Could not upload result: {e}")

    except Exception as e:
        st.error(f"Error during simulation: {e}")


st.markdown("")

st.markdown("<hr>", unsafe_allow_html=True)

footer = """
<style>
.footer {
    position: relative;
    bottom: 0;
    width: 100%;
    text-align: center;
    font-size: 0.9em;
    color: gray;
    margin-top: 3em;
}
</style>
<div class="footer">© 2025 Shlok Banshal. All rights reserved.</div>
"""

st.markdown(footer, unsafe_allow_html=True)