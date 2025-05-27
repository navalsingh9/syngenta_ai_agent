import pandas as pd
import re

# Load the CSV of extracted control statements
controls_path = "outputs/control_statements.csv"
df_controls = pd.read_csv(controls_path)

# Load the transaction dataset to get its columns
df_data = pd.read_csv("data/DataCoSupplyChainDataset.csv", encoding='latin1')
data_columns = [col.strip().lower().replace(" ", "_") for col in df_data.columns]

# Try mapping each control to relevant dataset columns
def find_related_fields(statement, columns):
    related = []
    for field in columns:
        keywords = field.split("_")
        if any(re.search(r'\b' + re.escape(word) + r'\b', statement.lower()) for word in keywords):
            related.append(field)
    return related

df_controls["Related Fields"] = df_controls["Control Statement"].apply(lambda x: find_related_fields(x, data_columns))

# Save the mapped file
df_controls.to_csv("outputs/mapped_controls.csv", index=False)
print(f"✅ Mapped control statements saved to outputs/mapped_controls.csv")
