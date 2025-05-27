import streamlit as st
import pandas as pd
import time
import difflib
import re

from deprecated.document_agentv0 import load_policy_vectorstore, ask_documents

from deprecated.sql_agentv1 import ask_data_question

st.set_page_config(page_title="AI Agent for Syngenta", layout="wide")

@st.cache_resource
def get_vectorstore():
    return load_policy_vectorstore()

vs = get_vectorstore()
df_controls = pd.read_csv("outputs/evaluated_controls.csv")

# Alias expansion for smarter matching
aliases = {
    "5 days shipping": "must not exceed 5 days",
    "late delivery": "delivery must be on time",
    "no movers": "no movement in 180 days",
    "obsolete": "obsolete inventory"
}

boost_keywords = {
    "5 days shipping": ["must not exceed 5 days", "more than 5 days", "shipping delay"],
    "late delivery": ["late_delivery_risk", "on-time delivery", "delivery delay"],
    "no movers": ["no movement in 180 days", "inventory not moved"],
    "obsolete": ["obsolete inventory", "aged stock"],
    "supplier": ["new supplier", "supplier onboarding"]
}

def intelligent_match(query, controls_df, threshold=0.6):
    query_clean = re.sub(r"[^a-z0-9\s]", "", query.lower())
    expanded_query = [query_clean]
    for key, expansions in boost_keywords.items():
        if key in query_clean:
            expanded_query.extend(expansions)
    matches = []
    for _, row in controls_df.iterrows():
        stmt_clean = re.sub(r"[^a-z0-9\s]", "", row["Control Statement"].lower())
        max_score = max(difflib.SequenceMatcher(None, q, stmt_clean).ratio() for q in expanded_query)
        if max_score > threshold:
            matches.append(row)
    return pd.DataFrame(matches)

st.title("🧠 AI Agent: Policy + Data Compliance Assistant")
user_query = st.text_input("Ask your question about policies or data:")

sql_query, result = ask_data_question(user_query)

for phrase, alias in aliases.items():
    if phrase in user_query.lower():
        user_query += " " + alias

if user_query:
    st.subheader("📊 Compliance Rule Matching")
    matching_rows = intelligent_match(user_query, df_controls)
    if not matching_rows.empty:
        for _, row in matching_rows.iterrows():
            st.markdown(f"**🔹 Control:** {row['Control Statement']}")
            st.markdown(f"**🟢 Compliance:** {row['Compliance Statement']}")
    else:
        st.warning("⚠️ No matching compliance control found.")

    if any(k in user_query.lower() for k in ["how many", "average", "more than", "less than", "orders over", "list all", "count", "show me", "total"]):
        st.subheader("📈 Structured Data (NL2SQL)")
        with st.spinner("Generating SQL with LLaMA..."):
            sql, result = ask_data_question(user_query)
            st.code(sql, language="sql")
            if isinstance(result, pd.DataFrame):
                st.dataframe(result)
            else:
                st.error(result)

    st.subheader("📄 Policy-Based Answer")
    with st.spinner("Searching policy documents..."):
        answer = ask_documents(user_query, vs)
        st.markdown(answer)
