import streamlit as st
import pandas as pd
from document_agent import load_policy_vectorstore, ask_documents
from sql_agent import ask_data_question
from claude_client import ClaudeBedrockLLM
from langchain_ollama import OllamaLLM
import datetime
import os
import time
from sql_agent import get_ground_truth
from metrics_tracker import init_db, record_metrics
init_db()
from metrics_tracker import get_recent_metrics


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

with st.sidebar.expander("📊 Performance Metrics"):
    try:
        df = get_recent_metrics()
        total = len(df)
        if total:
            st.metric("🔢 Benchmarked Queries", total)
            st.metric("⏱️ Avg Latency (s)", f"{df['latency'].mean():.2f}")
            st.metric("🔁 Avg Levenshtein", f"{df['levenshtein_distance'].mean():.2f}")
            st.metric("✅ Exact Match", f"{100 * df['exact_match'].mean():.1f}%")
            st.metric("🧠 Semantic Match", f"{100 * df['semantic_match'].mean():.1f}%")

            if st.checkbox("Show last 50 logs"):
                st.dataframe(df[["timestamp", "llm_name", "nl_query", "exact_match", "semantic_match", "latency"]])
                import altair as alt

                # Make sure timestamp is datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date

                st.markdown("### 📈 Trend Charts")

                # ✅ 1. Exact Match % over Time
                match_df = df.groupby("date")["exact_match"].mean().reset_index()
                match_df["Exact Match %"] = match_df["exact_match"] * 100

                chart = alt.Chart(match_df).mark_line(point=True).encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y("Exact Match %:Q", scale=alt.Scale(domain=[0, 100])),
                    tooltip=["date:T", "Exact Match %:Q"]
                ).properties(
                    title="✅ Exact Match Trend", height=200
                )
                st.altair_chart(chart, use_container_width=True)

                # ✅ 2. Avg Latency
                latency_df = df.groupby("date")["latency"].mean().reset_index()
                chart2 = alt.Chart(latency_df).mark_line(point=True).encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y("latency:Q", title="Avg Latency (s)"),
                    tooltip=["date:T", "latency:Q"]
                ).properties(
                    title="⏱️ Latency Trend", height=200
                )
                st.altair_chart(chart2, use_container_width=True)

                # ✅ 3. Avg Levenshtein Distance
                lev_df = df.groupby("date")["levenshtein_distance"].mean().reset_index()
                chart3 = alt.Chart(lev_df).mark_line(point=True).encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y("levenshtein_distance:Q", title="Levenshtein Distance"),
                    tooltip=["date:T", "levenshtein_distance:Q"]
                ).properties(
                    title="🔁 Levenshtein Distance Trend", height=200
                )
                st.altair_chart(chart3, use_container_width=True)

        else:
            st.write("No metrics yet. Ask something from test set.")
    except Exception as e:
        st.error(f"⚠️ Failed to load metrics: {e}")


# Debug log writer
def log(message):
    if debug_mode:
        with open("debug_log.txt", "a", encoding="utf-8") as f:  
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")


def get_llm(model_choice: str):
    if "Claude" in model_choice:
        api_key = os.getenv("CLAUDE_BEDROCK_API_KEY")
        if not api_key:
            st.error("Claude Bedrock API key not found in .env")
            st.stop()
        return ClaudeBedrockLLM(api_key=api_key)
    else:
        return OllamaLLM(model="llama3")

llm = get_llm(model_choice)
init_db()
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
    # ⏱️ Measure latency
    start = time.time()
    sql_query, result = ask_data_question(user_query, llm)
    latency = time.time() - start

    # 🧠 Ground truth SQL (if available)
    expected_sql = get_ground_truth(user_query)

    # 📈 Show structured result
    st.subheader("📈 Structured Data (NL2SQL)")
    if debug_mode:
        st.code(sql_query, language='sql')
        log(f"Generated SQL: {sql_query}")

    st.dataframe(result if isinstance(result, pd.DataFrame) else pd.DataFrame([{"error": result}]))

    # 📊 Log evaluation if test case exists
    if expected_sql:
        record_metrics(
            llm_name=llm.name if hasattr(llm, "name") else "Unknown",
            nl_query=user_query,
            generated_sql=sql_query,
            expected_sql=expected_sql,
            result_match=(
                sql_query is not None and expected_sql is not None and
                sql_query.strip().lower() == expected_sql.strip().lower()
            ),
            latency=latency
        )

    if matching_rows.empty or "policy" in user_query.lower():
        with st.spinner("Searching policy documents..."):
            answer = ask_documents(user_query, vs, llm)
            st.subheader("📄 Policy-Based Answer")
            st.markdown(answer)
            log(f"Policy Answer: {answer}")
