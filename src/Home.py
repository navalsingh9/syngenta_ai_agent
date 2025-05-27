import streamlit as st
import pandas as pd
from document_agent import load_policy_vectorstore, ask_documents
from sql_agent import ask_data_question
from claude_client import ClaudeBedrockLLM
from langchain_ollama import OllamaLLM
import datetime
import os

st.set_page_config(page_title="AI Agent for Syngenta", layout="wide")

# Sidebar: Model and options
model_choice = st.sidebar.selectbox("Choose Language Model:", ["Claude 3.5 Sonnet (Hackathon)", "Ollama (Local fallback)"])
debug_mode = st.sidebar.checkbox("🔍 Enable Debug Mode")
if st.sidebar.button("🔄 Refresh Policy Vector Store"):
    st.cache_resource.clear()
if st.sidebar.button("🧹 Clear Debug Log"):
    if os.path.exists("debug_log.txt"):
        os.remove("debug_log.txt")
        st.sidebar.success("Log cleared.")

# Log viewer and download
if os.path.exists("debug_log.txt"):
    with st.sidebar.expander("📜 View Debug Log"):
        with open("debug_log.txt", "r",encoding="utf-8") as f:
            log_content = f.read()
            st.text(log_content)
            st.download_button("⬇️ Download Log", log_content, file_name="debug_log.txt")

# Debug log writer
def log(message):
    if debug_mode:
        with open("debug_log.txt", "a", encoding="utf-8") as f:  
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")


def get_llm(model_choice: str):
    if "Claude" in model_choice:
        return ClaudeBedrockLLM(api_key="${CLAUDE_SECRET_ACCESS_KEY}")
    else:
        return OllamaLLM(model="llama3")

llm = get_llm(model_choice)
vs = load_policy_vectorstore()



st.title("🧠 AI Agent: Policy + Data Compliance Assistant")
user_query = st.text_input("Ask your question about policies or data:")

matching_rows = pd.DataFrame()
if user_query:
    try:
        df_controls = pd.read_csv("outputs/evaluated_controls.csv")
        matching_rows = df_controls[df_controls["Control Statement"].str.lower().str.contains(user_query.lower())]
        if not matching_rows.empty:
            st.subheader("📋 Matched Control Statements")
            for _, row in matching_rows.iterrows():
                st.markdown(f"**🔹 Control:** {row['Control Statement']}\n**🟢 Compliance:** {row['Compliance Statement']}")
    except Exception as e:
        log(f"⚠️ Control compliance file error: {str(e)}")
        if debug_mode:
            st.warning("⚠️ Control compliance file not found or unreadable.")

    sql_query, result = ask_data_question(user_query, llm)
    st.subheader("📈 Structured Data (NL2SQL)")
    if debug_mode:
        st.code(sql_query, language='sql')
        log(f"Generated SQL: {sql_query}")
    st.dataframe(result if isinstance(result, pd.DataFrame) else pd.DataFrame([{"error": result}]))
    log(f"Query Result: {result if isinstance(result, str) else result.to_string(index=False)}")

    if matching_rows.empty or "policy" in user_query.lower():
        with st.spinner("Searching policy documents..."):
            answer = ask_documents(user_query, vs, llm)
            st.subheader("📄 Policy-Based Answer")
            st.markdown(answer)
            log(f"Policy Answer: {answer}")
