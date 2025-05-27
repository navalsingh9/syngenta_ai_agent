import streamlit as st
import pandas as pd
from deprecated.document_agentv0 import load_policy_vectorstore, ask_documents
from deprecated.sql_agentv1 import ask_data_question
from deprecated.claude_clientv0 import ClaudeBedrockLLM
from langchain_community.llms import Ollama

matching_rows = pd.DataFrame()
st.set_page_config(page_title="AI Agent for Syngenta", layout="wide")

model_choice = st.selectbox("Choose Language Model:", ["Claude 3.5 Sonnet (Hackathon)", "Ollama (Local fallback)"])

def get_llm(model_choice: str):
    if "Claude" in model_choice:
        return ClaudeBedrockLLM(api_key="syn-8008f862-4c63-4bb5-a35d-fc0ea4684cb0")
    else:
        return Ollama(model="llama3")

llm = get_llm(model_choice)
vs = load_policy_vectorstore()

st.title("🧠 AI Agent: Policy + Data Compliance Assistant")
user_query = st.text_input("Ask your question about policies or data:")

if user_query:
    try:
        df_controls = pd.read_csv("outputs/evaluated_controls.csv")
        matching_rows = df_controls[df_controls["Control Statement"].str.lower().str.contains(user_query.lower())]
        if not matching_rows.empty:
            st.subheader("📋 Matched Control Statements")
            for _, row in matching_rows.iterrows():
                st.markdown(f"**🔹 Control:** {row['Control Statement']}\n**🟢 Compliance:** {row['Compliance Statement']}")
    except:
        st.warning("⚠️ Control compliance file not found or unreadable.")

    sql_query, result = ask_data_question(user_query, llm)
    st.subheader("📈 Structured Data (NL2SQL)")
    st.code(sql_query, language='sql')
    st.dataframe(result if isinstance(result, pd.DataFrame) else pd.DataFrame([{"error": result}]))

    if matching_rows.empty or "policy" in user_query.lower():
        with st.spinner("Searching policy documents..."):
            answer = ask_documents(user_query, vs)
            st.subheader("📄 Policy-Based Answer")
            st.markdown(answer)