# Wallet Risk Scoring

This project fetches on-chain data from the Compound V2 protocol to compute a risk score for a set of Ethereum wallets.

## How to Run

1. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

2. Make sure you have `Wallet id.csv` in the same directory with a column named `wallet_id`.

3. Run the script:
    ```
    python main.py
    ```

4. Output will be saved as `wallet_risk_scores.csv`.

## Notes

- The code uses a working mirror of the Compound V2 subgraph on The Graph.
- Wallets that have not interacted with Compound V2 will be skipped.