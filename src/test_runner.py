import pandas as pd
from sql_agent import ask_data_question
from document_agent import ask_documents, load_policy_vectorstore
from claude_client import ClaudeBedrockLLM
from langchain_ollama import OllamaLLM
import datetime
import os

# Define test prompts
test_prompts = [
    "What was the total sales in Southwest region in the last quarter?",
    "Show all orders with shipping time greater than scheduled shipping time",
    "What is our company’s policy on obsolete inventory?",
    "How many late deliveries occurred in California?",
    "Which customer segments had the highest average sales?"
]

# Select model
model = ClaudeBedrockLLM(api_key="syn-8008f862-4c63-4bb5-a35d-fc0ea4684cb0")
vs = load_policy_vectorstore()

# Logging setup
log_file = "test_log.csv"
results = []

# Run tests
for prompt in test_prompts:
    sql, data = ask_data_question(prompt, model)
    try:
        df_out = data if isinstance(data, pd.DataFrame) else pd.DataFrame([{"error": data}])
    except:
        df_out = pd.DataFrame([{"error": str(data)}])

    policy_answer = ask_documents(prompt, vs, model)
    results.append({
        "Prompt": prompt,
        "SQL": sql,
        "SQL Result": df_out.to_string(index=False),
        "Policy Answer": policy_answer
    })

# Export to CSV
df_log = pd.DataFrame(results)
df_log.to_csv(log_file, index=False)
print(f"Test log saved to {log_file}")