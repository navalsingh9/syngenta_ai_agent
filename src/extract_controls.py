import os
import re
from load_data import extract_policy_texts

# Keywords that indicate control statements
CONTROL_KEYWORDS = [
    "must", "should", "shall", "required", "prohibited",
    "not allowed", "no tolerance", "only if", "ensure", "needs to"
]

def extract_control_statements(text):
    lines = text.split('\n')
    controls = []
    for line in lines:
        line = line.strip()
        if any(kw in line.lower() for kw in CONTROL_KEYWORDS) and 20 < len(line) < 300:
            controls.append(line)
    return controls

def process_all_policies():
    policy_docs = extract_policy_texts()
    extracted_controls = []

    for filename, text in policy_docs.items():
        control_lines = extract_control_statements(text)
        for line in control_lines:
            extracted_controls.append({
                "Source Document": filename,
                "Control Statement": line
            })

    print(f"✅ Extracted {len(extracted_controls)} control statements")
    return extracted_controls

if __name__ == "__main__":
    controls = process_all_policies()

    # Save to CSV (optional)
    import pandas as pd
    df_controls = pd.DataFrame(controls)
    df_controls.to_csv("outputs/control_statements.csv", index=False)
    print("✅ Saved to outputs/control_statements.csv")
