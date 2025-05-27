import streamlit as st
import pandas as pd

st.set_page_config(page_title="Compliance Dashboard", layout="wide")
st.title("📊 Compliance Control Summary")

try:
    df_controls = pd.read_csv("outputs/evaluated_controls.csv")

    numeric_controls = df_controls[pd.to_numeric(df_controls["Violation Count"], errors='coerce').notnull()]

    if not numeric_controls.empty:
        for _, row in numeric_controls.iterrows():
            control = row["Control Statement"]
            field = row.get("Related Field", "N/A")
            violations = int(row["Violation Count"])
            status = "NON-COMPLIANT" if violations > 0 else "COMPLIANT"

            st.markdown(f"""
**Control**: {control}  
**Status**: **{status}**  
**Related Field**: {field}  
**Violations**: {violations}
""")
            st.markdown("---")
    else:
        st.info("No evaluated controls with numeric violation counts found.")

except Exception as e:
    st.error("Failed to load evaluated_controls.csv")
    st.exception(e)
