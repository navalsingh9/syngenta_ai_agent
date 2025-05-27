import pandas as pd
import os
from pdfminer.high_level import extract_text

# Paths
DATA_PATH = "data/DataCoSupplyChainDataset.csv"
DOCS_PATH = "docs"

# Load CSV
def load_transaction_data():
    df = pd.read_csv(DATA_PATH, encoding='latin1')
    print(f"✅ Loaded {len(df)} transactions with {len(df.columns)} columns")
    return df

# Read all PDFs in docs folder
def extract_policy_texts():
    policy_texts = {}
    for filename in os.listdir(DOCS_PATH):
        if filename.endswith(".pdf"):
            full_path = os.path.join(DOCS_PATH, filename)
            try:
                text = extract_text(full_path)
                policy_texts[filename] = text
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
    print(f"✅ Loaded {len(policy_texts)} policy documents")
    return policy_texts

# Run check
if __name__ == "__main__":
    df = load_transaction_data()
    docs = extract_policy_texts()
