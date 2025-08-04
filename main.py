
import pandas as pd
import numpy as np
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from sklearn.preprocessing import MinMaxScaler
import time

# Updated Compound V2 subgraph endpoint (working mirror)
transport = RequestsHTTPTransport(
    url="https://api.thegraph.com/subgraphs/name/graphprotocol/compound-v2",
    verify=True,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=False)


# Load wallet addresses
wallets_df = pd.read_csv("Wallet id.csv")
wallet_addresses = wallets_df["wallet_id"].tolist()

# GraphQL query
query_template = """
query ($user: ID!) {
  account(id: $user) {
    id
    tokens {
      symbol
      supplyBalanceUnderlying
      borrowBalanceUnderlying
    }
  }
}
"""

def fetch_wallet_data(wallet):
    query = gql(query_template)
    try:
        result = client.execute(query, variable_values={"user": wallet.lower()})
        return result.get("account", None)
    except Exception as e:
        print(f"Error fetching data for {wallet}: {e}")
        return None

def extract_features(data):
    tokens = data.get("tokens", [])
    total_supply = sum(float(t.get("supplyBalanceUnderlying", 0) or 0) for t in tokens)
    total_borrow = sum(float(t.get("borrowBalanceUnderlying", 0) or 0) for t in tokens)
    net_position = total_supply - total_borrow
    ratio = (total_supply / (total_borrow + 1e-6)) if total_borrow > 0 else 10.0
    return [total_supply, total_borrow, net_position, ratio]

features = []
valid_wallets = []

for wallet in wallet_addresses:
    data = fetch_wallet_data(wallet)
    if data:
        features.append(extract_features(data))
        valid_wallets.append(wallet)
    else:
        print(f"Skipping wallet {wallet} due to missing data.")
    time.sleep(0.2)

if not features:
    raise RuntimeError("No wallet data fetched successfully. Please check the wallet list or subgraph coverage.")

features_df = pd.DataFrame(features, columns=["supply", "borrow", "net_position", "supply_borrow_ratio"])
scaler = MinMaxScaler()
normalized = scaler.fit_transform(features_df)
scores = (normalized.mean(axis=1) * 1000).astype(int)

result_df = pd.DataFrame({
    "wallet_id": valid_wallets,
    "score": scores
})

result_df.to_csv("wallet_risk_scores.csv", index=False)
print("✅ Risk scores saved to 'wallet_risk_scores.csv'")
