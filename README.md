# Liar's Poker Helper Bot

This is an intelligent simulation and strategy tool designed for evaluating bids in the game of Liar’s Poker. It uses Monte Carlo simulations to suggest whether to call or raise based on your hand and public game conditions.

---

## Features

* Streamlit interface for bid simulation and decision making
* Monte Carlo simulation of millions of hands for statistical backing
* Automatic decision output based on probability threshold
* Local and remote saving of results (as `.json`)
* Centralized Flask server hosted on Render for collecting submissions
* Daily auto-downloaded results using cron
* Auto-extracted ZIPs saved to `synced_results/`

---

## How It Works

1. User enters hand and bid into the Streamlit UI
2. Simulation is run using known and unknown cards
3. Results are formatted into structured JSON, including:

   * Hand input
   * Total players
   * Stronger hands above threshold (only these are saved)
4. Saved locally to `data/output_<timestamp>.json`
5. Uploaded to Render via a REST POST to `/upload`
6. Filename and download link shown in the UI
7. On the server:

   * JSONs are saved in `/uploaded_jsons/`
   * Public `/files.zip` endpoint is updated

---

## Key Scripts

### `app.py`

* Streamlit interface for bid selection and simulation
* Cleans and standardizes output format
* Uniform UI style for feedback

### `download_all.py`

* Downloads `files.zip` from the server
* Extracts into: `synced_results/<timestamp>/`
* Deletes ZIP after extraction
* Can be run manually or scheduled via cron

---

## Cron Automation

The script `download_all.py` is automatically run every day at 8:00 AM on macOS via `cron`.

Make sure your machine is awake and not asleep if you want the job to fire.

To edit the schedule:

```bash
crontab -e
```

Sample entry:

```bash
0 8 * * * /Library/Frameworks/Python.framework/Versions/3.9/bin/python3 /Users/yourname/path/to/download_all.py
```

---

## Server Endpoints (Flask)

* `POST /upload` – accepts JSON upload and saves to disk
* `GET /files` – returns list of all `.json` files
* `GET /files/<filename>` – returns the raw `.json` file
* `GET /files.zip` – returns all `.json` files in a single archive
* `GET /stats` (optional) – returns server-side summary stats

Hosted on: [https://liars-poker-uploader.onrender.com](https://liars-poker-uploader.onrender.com)

---

## Data Output Format

Each uploaded `.json` includes:

```json
{
  "inputs": {
    "hand": [...],
    "bid": ..., 
    "players": ...
  },
  "outputs": {
    "presence_probability": 0.72,
    "suggestion": "raise",
    "stronger_hands": [
      { "type": "Straight", "frequency": 0.12, ... },
      ...
    ]
  }
}
```

Note: Only `stronger_hands` above the threshold are included.

---

## Project Structure

```
├── app.py                 # Streamlit UI
├── download_all.py        # Daily pull of all JSON results
├── server.py              # Flask collector backend
├── synced_results/        # Extracted results per day
├── uploaded_jsons/        # Stored JSONs (on server only)
├── utils.py               # Formatter for ML output
├── simulator.py           # Core simulation logic
├── bid.py, card.py        # Bid/card parsing logic
├── requirements.txt
└── README.md
```

---

## Testing

Use `test_bid_logic.py` to validate:

* Bid parsing
* Hand ranking
* Input formatting

Run with:

```bash
python -m unittest test_bid_logic.py
```

---

## Optional Enhancements

* Add metadata per user (initials, session tag)
* Visualize synced results via charts
* Auto-sync `synced_results/` to Google Drive or GitHub Pages

---

## Created By

Shlok Banshal — Summer 2025

Inspired by game theory, poker modeling, and AI-backed decision support tools.