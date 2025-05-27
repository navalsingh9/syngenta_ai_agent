import pandas as pd

# Load mapped controls and transaction data
controls_df = pd.read_csv("outputs/mapped_controls.csv")
data_df = pd.read_csv("data/DataCoSupplyChainDataset.csv", encoding='latin1')
data_df.columns = [col.strip().lower().replace(" ", "_") for col in data_df.columns]

# Evaluate simple rules using keyword + numeric patterns
def evaluate_control(row):
    statement = row['Control Statement'].lower()
    fields = eval(row['Related Fields']) if isinstance(row['Related Fields'], str) else []
    
    if not fields:
        return "No matching field", None

    # Example: detect and apply a "must be positive" rule
    if "must be positive" in statement:
        for field in fields:
            if field in data_df.columns:
                nonpositive = (data_df[field] <= 0).sum()
                if nonpositive > 0:
                    return f"Non-compliant: {nonpositive} rows in {field} ≤ 0", nonpositive
                return f"Compliant: all values in {field} > 0", 0

    # Example: threshold like "must not exceed 5 days"
    if "must not exceed" in statement or "must be less than" in statement:
        import re
        numbers = re.findall(r'\d+', statement)
        if numbers:
            threshold = int(numbers[0])
            for field in fields:
                if field in data_df.columns:
                    too_high = (data_df[field] > threshold).sum()
                    if too_high > 0:
                        return f"Non-compliant: {too_high} records in {field} > {threshold}", too_high
                    return f"Compliant: all values in {field} ≤ {threshold}", 0

    return "Not automatically evaluable", None

# Apply evaluation
controls_df["Compliance Statement"], controls_df["Violation Count"] = zip(
    *controls_df.apply(evaluate_control, axis=1)
)

# Save result
controls_df.to_csv("outputs/evaluated_controls.csv", index=False)
print("✅ Evaluated compliance for measurable controls.")
