# Liar's Poker Helper Bot

This tool simulates whether a given bid in Liar's Poker is likely to be true given your own hand and the total number of cards in play. It uses combinatorial enumeration and Monte Carlo simulation to compute the probability that at least one stronger 5-card hand exists.

---

## Features

* Streamlit interface for entering bids and cards
* Monte Carlo simulation using combinatorial sampling of all possible unseen 5-card hands
* Automatically filters to only show hands above a frequency threshold
* Local and remote `.json` saving of results
* Remote server collects data and allows central access to all simulations
* Daily cron job pulls all results into a local folder and unzips them automatically

---

## How It Works

1. User inputs a bid and cards into the Streamlit app (`app.py`)
2. The simulation runs (`simulator.py`) and checks if a stronger hand could exist

   * All 5-card combinations from the remaining deck are enumerated
   * A subset of trials (default 1000) is sampled from random pool configurations
   * For each trial, we check if any hand beats the given bid
3. The result is returned as a probability estimate (`presence_probability`)

   * The standard error with 1000 trials is approximately 1.6%
4. All matching hands are filtered to those with frequency ≥ threshold
5. The result is saved locally and sent to a Flask server
6. The server stores all simulations in a timestamped `.json` format

---

## Repository Structure

```
├── app.py                 # Streamlit UI for simulation
├── simulator.py           # Core Monte Carlo logic + enumeration
├── utils.py               # JSON formatting and deck handling
├── server.py              # Flask endpoint to collect uploads and serve files
├── download_all.py        # Downloads + extracts all remote `.json`s daily
├── synced_results/        # Locally extracted simulation results
├── uploaded_jsons/        # (on server) All saved results
├── requirements.txt       # Python dependencies
└── test_bid_logic.py      # Bid parsing tests
```

---

## Data Format

Each `.json` result includes:

```json
{
  "inputs": {
    "hand": ["7 of Hearts", "9 of Diamonds"],
    "bid": {
      "hand_type": "Two Pair",
      "primary": "7",
      "secondary": "2",
      "suit": null,
      "range_start": null,
      "range_end": null
    },
    "total_cards": 20,
    "threshold": 0.05
  },
  "outputs": {
    "presence_probability": 0.731,
    "stronger_hands": [
      {"type": "Three of a Kind", "primary_rank": "7", "frequency": 0.12},
      ...
    ],
    "suggestion": "Call BS"
  }
}
```

* Only `stronger_hands` **above the threshold** are included

---

## Automation

To fetch all uploaded `.json` files daily:

* A cron job is installed locally that runs `download_all.py` every morning at 8:00am
* This script pulls `files.zip` from the server, extracts it into `synced_results/`, and deletes the zip

To test it manually:

```bash
python download_all.py
```

To install the cron job:

```bash
crontab -e
```

Then add:

```
0 8 * * * /Library/Frameworks/Python.framework/Versions/3.9/bin/python3 /Users/shlokbanshal/Downloads/liars_poker_helper_bot/download_all.py
```

---

## Server Routes

Server is hosted on Render at:
[https://liars-poker-uploader.onrender.com](https://liars-poker-uploader.onrender.com)

* `POST /upload` → receives JSON simulation result and stores it
* `GET /files` → returns list of all stored filenames
* `GET /files/<filename>` → returns the actual `.json` file
* `GET /files.zip` → returns all results as a ZIP

---

## Resources

Two supplemental documents are included in this repo:

* **Liar's Poker – Bid Interpretation Guide.pdf** – rules for interpreting each hand type and suit-based bid
* **Liar's Poker Handbook and Bid Progressions.pdf** – complete hand ranking hierarchy and strategic guidelines

These are useful for players unfamiliar with the structure of valid bids or for instructors teaching the format.

---

## Running the App

Install dependencies:

```bash
pip install -r requirements.txt
```

Then launch the Streamlit UI:

```bash
streamlit run app.py
```

Or open the app directly if hosted: (Replace this with your public Streamlit share link)

[Launch the app](https://share.streamlit.io/your-username/liars-poker-helper-bot/main/app.py)

---

## Created by

Shlok Banshal – Summer 2025