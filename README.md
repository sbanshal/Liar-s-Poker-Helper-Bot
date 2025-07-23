# Liar's Poker – Bid Helper (Collective Hold’em Variant)

This web-based simulation tool helps players of the **Liar’s Poker Collective Hold’em Variant** evaluate the plausibility of specific 5-card poker hand bids.

🃏 [Launch the app here](https://liar-s-poker-apper-bot-bgvknhv8kzniydeygtqr6j.streamlit.app/)

---

## 🎯 What It Does

- You input:
  - Your hand (e.g., `4 of Hearts`, `10 of Spades`)
  - The total number of cards in play (e.g., 20)
  - The most recent bid (e.g., `Three of a Kind, Queens`)
  - A confidence threshold (e.g., 0.5)
- The app simulates thousands of possible pools and tells you:
  - Whether the bid is likely valid
  - What stronger hands are probable
  - What your best next move might be

---

## 📜 Game Rules & Hand Rankings

This project uses the “Collective Hold’em” ruleset of Liar’s Poker.

- 🎮 [Game Handbook and Bid Progressions (PDF)](Liar's%20Poker%20Handbook%20and%20Bid%20Progressions.pdf)
- 📘 [Bid Interpretation Guide (PDF)](Liar's%20Poker%20–%20Bid%20Interpretation%20Guide.pdf)

Key bidding clarifications:
- Bids must be fulfilled exactly — stronger hands don’t count
- For example, a **Full House** doesn’t satisfy a **Three of a Kind** bid
- Flushes are defined by high card, not suit hierarchy
- Royal Flush is treated as its own rank above Straight Flush

---

## 📦 How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🚀 Deployment

This app is deployed publicly via [Streamlit Cloud](https://streamlit.io/cloud).  
It auto-updates with every push to the `main` branch.

---

## 🙌 Contributing

Pull requests and feature suggestions welcome!  
This project was built to test probability assumptions in advanced bluff-based gameplay — but can be extended into teaching tools, AI bidding bots, or player analytics.

---

## 📫 Contact

Made by [Shlok Banshal](mailto:shlok.banshal@duke.edu)

---

© 2025 Shlok Banshal. All rights reserved.