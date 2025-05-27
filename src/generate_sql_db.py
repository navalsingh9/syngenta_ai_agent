import pandas as pd
import sqlite3
import re

# Load CSV
df = pd.read_csv("data/DataCoSupplyChainDataset.csv", encoding="latin1")

# Normalize column names for SQL compatibility
def normalize(col):
    return re.sub(r"[^\w]+", "_", col.strip().lower())

df.columns = [normalize(c) for c in df.columns]

# Save to SQLite
conn = sqlite3.connect("data/transactions.db")
df.to_sql("transactions", conn, if_exists="replace", index=False)
conn.close()

print("✅ SQLite DB created with normalized column names.")
