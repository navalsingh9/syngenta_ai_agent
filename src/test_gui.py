import streamlit as st
import pandas as pd
from sql_agent import ask_data_question
from document_agent import ask_documents, load_policy_vectorstore
from claude_client import ClaudeBedrockLLM
from langchain_ollama import OllamaLLM

st.set_page_config(page_title="🧪 LLM Test Runner", layout="wide")

st.title("🧪 Automated Test Runner for AI Agent")

# LLM Selection
model_choice = st.selectbox("Choose Model to Test:", ["Claude 3.5 Sonnet (Hackathon)", "Ollama (Local fallback)"])
if "Claude" in model_choice:
    llm = ClaudeBedrockLLM(api_key="${CLAUDE_SECRET_ACCESS_KEY}")
else:
    llm = OllamaLLM(model="llama3")

vs = load_policy_vectorstore()

# Test Prompt Options
test_prompts = [
    "What was the total sales in Southwest region in the last quarter?",
    "Show all orders with shipping time greater than scheduled shipping time",
    "What is our company’s policy on obsolete inventory?",
    "How many late deliveries occurred in California?",
    "Which customer segments had the highest average sales?"
]
selected = st.selectbox("Choose test prompt to run:", test_prompts)

if st.button("Run Test Prompt"):
    sql, result = ask_data_question(selected, llm)
    st.subheader("📜 SQL Query")
    st.code(sql, language="sql")
    st.subheader("📊 SQL Result")
    if isinstance(result, pd.DataFrame):
        st.dataframe(result)
    else:
        st.error(result)

    with st.spinner("Getting policy response..."):
        answer = ask_documents(selected, vs, llm)
        st.subheader("📄 Policy-Based Answer")
        st.markdown(answer)