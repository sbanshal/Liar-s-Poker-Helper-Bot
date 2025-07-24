
# Liar’s Poker Helper Bot

This tool simulates whether a 5-card poker hand bid is statistically plausible based on a player’s private cards and total cards in play, using combinatorial enumeration and Monte Carlo sampling. Built for the Collective Hold'em variant of Liar’s Poker, it serves as both a teaching tool and a probabilistic strategy aid.

---

## Try the App

- [Launch the Streamlit App](https://share.streamlit.io/sbanshal/liars-poker-helper-bot/main/app.py)
- [Liar's Poker – Bid Interpretation Guide (PDF)](https://github.com/sbanshal/Liar-s-Poker-Helper-Bot/raw/main/Liar's%20Poker%20–%20Bid%20Interpretation%20Guide.pdf)
- [Liar's Poker Handbook and Bid Progressions (PDF)](https://github.com/sbanshal/Liar-s-Poker-Helper-Bot/raw/main/Liar's%20Poker%20Handbook%20and%20Bid%20Progressions.pdf)

---

## How It Works

This tool evaluates whether a claimed 5-card poker hand bid (e.g., "Two Pair, 9s and 7s") can be beaten by any plausible hand that could still exist in the deck given:

- The player’s private cards
- The number of total cards in play (i.e., across all players)

For each of a fixed number of simulated trials (default: 1000), the simulator randomly draws a set of unknown cards from the remaining deck to build a hypothetical “pool” of community cards.

For each trial, it then evaluates **all possible valid 5-card poker bids** that could be made from that pool and determines:

- Which of those bids would be legal
- Which of those bids would be stronger than the current one

The output reflects the proportion of simulations in which **at least one plausible stronger bid** exists.

Each trial maps the hand space above the given bid — this is not checking if one specific stronger hand exists, but if any legal stronger bids are possible given the simulated pool. a unique pool of unknown cards and enumerates all possible 5-card hands that can be formed. The code checks how often a stronger hand appears across trials to compute the empirical probability of the bid being false (i.e., a stronger hand is present).

1. User inputs a bid (e.g. “Two Pair, 9s and 7s”) and private cards into a Streamlit interface.
2. The simulator runs thousands of random 5-card draws from the remaining unknown deck.
3. For each simulated pool, it checks if any 5-card hand exactly matches or beats the bid.
4. Results are summarized as a presence probability.
5. Only stronger hands above a frequency threshold (e.g., 5%) are returned.
6. Results are saved locally and uploaded remotely.

---

## Core Logic

The core logic is implemented in `simulator.py`, `hand_evaluator.py`, and `bid.py`, using logic such as:

- Full enumeration of all plausible 5-card bids from the simulated pool
- Legal bid parsing and comparison handled via `Bid` objects and `.beats(...)` logic
- Hand evaluator computes rank of each 5-card combination
- For each trial, the simulation checks whether any stronger bid could have legally been made

Monte Carlo accuracy:

- 1000 trials gives an approximate standard error of ~1.6% for the presence probability estimate
- Increasing trials (e.g. to 10,000) improves precision but increases runtime

Hand evaluation covers all standard hand types: high card, pair, two pair, three of a kind, straight, flush, full house, four of a kind, straight flush, and royal flush.

- All 5-card combinations are generated using combinatorics from the unknown portion of the deck.
- A fixed number of pool trials (default: 1000) are sampled to simulate different realistic distributions of unknown cards.
- The simulator does not count stronger hands when validating a weaker bid — exact-match logic is enforced.
- Estimated standard error of probability is approximately 1.6% with 1000 trials.

---

## File Structure

```
├── app.py                 # Streamlit UI
├── simulator.py           # Monte Carlo simulation engine
├── utils.py               # Card parsing, deck formatting, JSON output builder
├── server.py              # Flask API to accept JSON and serve it back
├── download_all.py        # Pulls latest results from server daily
├── synced_results/        # Extracted ZIPs from server
├── uploaded_jsons/        # Server-stored uploads
├── test_bid_logic.py      # Hand ranking unit tests
├── requirements.txt       # Streamlit, Flask, matplotlib
├── Liar's Poker – Bid Interpretation Guide.pdf
├── Liar's Poker Handbook and Bid Progressions.pdf
```

---

## Output Format

Each run produces a structured `.json` result that includes:

- All simulation inputs: cards, bid, total cards, threshold
- The resulting `presence_probability` of a stronger hand
- A list of matching stronger hands (if any), each with frequency
- A final decision recommendation (`suggestion`) based on threshold

Example:

```json
{
  "inputs": {
    "hand": ["9 of Clubs", "9 of Spades"],
    "bid": {
      "hand_type": "Two Pair",
      "primary": "9",
      "secondary": "7"
    },
    "total_cards": 20,
    "threshold": 0.05
  },
  "outputs": {
    "presence_probability": 0.724,
    "stronger_hands": [
      { "type": "Three of a Kind", "primary_rank": "9", "frequency": 0.121 },
      { "type": "Straight", "frequency": 0.211 }
    ],
    "suggestion": "Call BS or Bluff"
  }
}
```

- Stronger hands below the threshold are excluded entirely.
- Each output includes a suggestion field to aid decision-making.

---

## Automation

To automatically sync all submissions:

1. A cron job is installed locally that runs `download_all.py` at 8:00 AM daily
2. This script downloads the remote ZIP archive of all simulation results from `/files.zip`
3. It extracts them to a timestamped folder under `synced_results/`
4. The ZIP is deleted after extraction

You can run it manually too:

```bash
python3 download_all.py
```

To install the cron job:

```bash
crontab -e
```

Then add:

```bash
0 8 * * * /Library/Frameworks/Python.framework/Versions/3.9/bin/python3 /Users/shlokbanshal/Downloads/liars_poker_helper_bot/download_all.py
```

---

## Server Endpoints (Flask @ Render)

Deployed at: [https://liars-poker-uploader.onrender.com](https://liars-poker-uploader.onrender.com)

| Route               | Method | Description                         |
| ------------------- | ------ | ----------------------------------- |
| `/upload`           | POST   | Accepts a new `.json` simulation    |
| `/files`            | GET    | Lists all stored file names         |
| `/files/<name>`     | GET    | Returns the raw JSON file           |
| `/files.zip`        | GET    | All results zipped into one archive |
| `/stats` (optional) | GET    | Returns mean probability + count    |

---

## Running the App

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the Streamlit app:

```bash
python3 -m streamlit run app.py
```

---

## Created By

Built and iteratively refined by Shlok Banshal, Summer 2025.

This project is intended for use in educational tournament settings, simulations, and player testing for Liar's Poker adapted formats.

Feel free to fork or submit contributions via pull request.

© Shlok Banshal. All rights reserved.
