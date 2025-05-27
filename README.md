# Syngenta AI Agent – Hackathon Submission

This app is a multimodal intelligent agent that:
- Extracts control statements from policy documents
- Evaluates compliance from supply chain transaction data
- Supports document/data/hybrid queries via chat
- Enforces role-based and region-based access control

## Setup Instructions

1. Clone repo and install dependencies
2. Start Ollama: `ollama run llama3`
3. Run the app: `streamlit run src/chat_app.py`

## Example Users

Edit `src/user_config.py` to simulate:
- Role: `Finance`, `Planner`, `Admin`
- Region: `India`, `Global`, `EU`, etc.

## Demo Video

Watch our full 10-minute demo on YouTube:

[![Watch on YouTube](https://img.youtube.com/vi/2bpAn2gPxyU/0.jpg)](https://www.youtube.com/watch?v=2bpAn2gPxyU)

➡️ [Click here to watch](https://www.youtube.com/watch?v=2bpAn2gPxyU)


## Team IdliWadaSambhar
- (Member) Naval Singh (21f1006368@ds.study.iitm.ac.in)

🧠 Syngenta Policy + Data Compliance AI Agent
Built for Paradox 2025 Hackathon

🚀 Core Capabilities:
🔍 Natural Language Compliance Queries across:

📑 Policy documents (PDF ingestion)

📊 Structured transaction data (SQLite)

🧠 Dual LLM Integration:

Claude 3.5 Sonnet – Advanced control detection, date inference, and SQL generation

Ollama (LLaMA 3) – Local fallback ensuring resilience post-hackathon

📌 Control Rule Extraction with semantic matching

🧾 Dynamic NL2SQL Engine:

Date-aware

Schema-aware

Claude uses raw schema; Ollama uses mapped aliases

🧪 QA/Testing Suite:
CLI + Streamlit Test Runner

⚖️ Debug Log Viewer, Clearer & Downloadable Logs

🖥️ Fully interactive Streamlit front end

📂 Easy plug-in of new policy documents and transaction datasets

🎯 Engineering Highlights:
🔁 Refreshable vector store

📅 Automatic dataset range detection

📋 Control rule matching using evaluated controls

🧠 Claude prompt scaffolding minimized to prove its understanding

🔄 Ollama prompt safely scaffolded for fallback execution

Architecture Overview:
- Frontend: Streamlit UI for natural language input and response.
- LLM Routing: Supports both Claude on Bedrock and LLaMA 3 via Ollama.
- Documents: Uses LangChain to chunk, embed, and search PDFs using FAISS + sentence transformers.
- Structured Data: NL2SQL pipeline to query a 180k-row SQLite database using dynamically generated SQL.
- Control Matching: Pre-evaluated policy controls mapped against questions.
- Hybrid Mode: Combines policy documents and transactional data for complex compliance queries.

Key Innovations:
- Dynamic date parsing from DB
- Verbose aliasing for LLM alignment
- Dual-Language Model Compatibility

Challenges:
- Mapping vague queries like 'last quarter'
- Aligning user-friendly terms to schema

All resolved with preprocessing, dynamic inference, and field aliasing.
