# 🧠 Syngenta AI Compliance Agent

> An intelligent, multimodal AI agent for supply chain policy compliance — built for the **Paradox 2025 Hackathon** by Team IdliWadaSambhar.

[![Watch on YouTube](https://img.youtube.com/vi/2bpAn2gPxyU/0.jpg)](https://www.youtube.com/watch?v=2bpAn2gPxyU)

➡️ [Watch the full 10-minute demo on YouTube](https://www.youtube.com/watch?v=2bpAn2gPxyU)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the App](#running-the-app)
- [Configuration](#configuration)
- [Example Queries](#example-queries)
- [Policy Documents](#policy-documents)
- [Testing](#testing)
- [Security](#security)
- [Team](#team)

---

## Overview

The Syngenta AI Compliance Agent is a hybrid assistant that helps organizations stay audit-ready by answering compliance-related questions using both:

- 📑 **Unstructured data** — PDF policy documents (ingested, chunked, and searched via vector embeddings)
- 📊 **Structured data** — A 180k-row SQLite supply chain transaction database (queried via natural language to SQL)

The agent extracts control statements from policy documents, evaluates compliance against real transaction data, and surfaces violations through an interactive Streamlit dashboard.

---

## Key Features

| Feature | Description |
|---|---|
| 🔍 Natural Language to SQL (NL2SQL) | Ask questions in plain English; the agent generates and runs SQL on a live SQLite database |
| 📄 Policy Document QA | Semantic search over 25+ supply chain PDFs using FAISS + sentence transformers |
| 🧠 Dual LLM Support | Claude 3.5 Sonnet (via AWS Bedrock) for enterprise accuracy; LLaMA 3 via Ollama as a local fallback |
| 📌 Control Rule Extraction | Automatically extracts and evaluates policy control statements against transaction data |
| 🔁 Hybrid Query Mode | Combines policy documents and transactional data for complex compliance questions |
| 📅 Date-Aware Querying | Resolves relative dates like "last quarter" using live min/max ranges from the database |
| ⚖️ Role & Region Access Control | Simulated RBAC with configurable user roles (Planner, Finance, Admin) and regions |
| 📊 Compliance Dashboard | Visual summary of control violations across all evaluated policies |
| 🧪 QA / Testing Suite | CLI and Streamlit test runner with Levenshtein distance, exact match, and semantic match metrics |
| 📜 Debug Log Viewer | Downloadable debug logs with timestamped query traces |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Streamlit Frontend                     │
│   (Home.py — chat UI, sidebar metrics, debug log)        │
└────────────────────┬─────────────────────────────────────┘
                     │ User Query
          ┌──────────▼──────────┐
          │    LLM Router       │
          │  Claude 3.5 Sonnet  │◄── AWS Bedrock (.env key)
          │  LLaMA 3 (Ollama)   │◄── Local fallback
          └──────┬───────┬──────┘
                 │       │
     ┌───────────▼─┐   ┌─▼────────────────┐
     │  SQL Agent  │   │  Document Agent  │
     │  (NL2SQL)   │   │  (PDF Vector QA) │
     └──────┬──────┘   └───────┬──────────┘
            │                  │
     ┌──────▼──────┐   ┌───────▼──────────┐
     │  SQLite DB  │   │  FAISS Vectorstore│
     │ (180k rows) │   │  (25+ PDFs)       │
     └─────────────┘   └──────────────────┘
                 │
     ┌───────────▼──────────────┐
     │  Control Evaluator       │
     │  extract_controls.py     │
     │  evaluate_controls.py    │
     │  map_controls.py         │
     └──────────────────────────┘
```

- **Frontend:** Streamlit UI with natural language input, response display, and performance metrics
- **LLM Routing:** Automatically switches between Claude (enterprise) and Ollama (local) based on user selection
- **Documents:** LangChain + FAISS + `sentence-transformers/all-MiniLM-L6-v2` for PDF chunking, embedding, and retrieval
- **Structured Data:** Dynamic NL2SQL pipeline with schema-awareness and date inference
- **Control Matching:** Pre-extracted policy controls evaluated against the transaction database

---

## Project Structure

```
syngenta_ai_agent/
├── docs/                              # 25+ supply chain policy PDFs
│   ├── COC.pdf
│   ├── Data Security.pdf
│   ├── Risk Management.pdf
│   └── ...
├── src/
│   ├── Home.py                        # Main Streamlit app entry point
│   ├── pages/
│   │   └── 1_Compliance_Dashboard.py  # Policy control violation dashboard
│   ├── document_agent.py              # PDF loading, FAISS vectorstore, document QA
│   ├── sql_agent.py                   # NL2SQL pipeline with date-aware prompting
│   ├── claude_client.py               # AWS Bedrock Claude 3.5 Sonnet LLM client
│   ├── extract_controls.py            # Extracts control statements from PDFs
│   ├── evaluate_controls.py           # Evaluates controls against transaction data
│   ├── map_controls.py                # Maps controls to database fields
│   ├── generate_sql_db.py             # Generates the SQLite transaction database
│   ├── load_data.py                   # Data loading utilities
│   ├── metrics_tracker.py             # Tracks latency, exact match, semantic match
│   ├── generate_test_cases.py         # Generates NL2SQL test cases
│   ├── test_runner.py                 # CLI test runner
│   ├── test_gui.py                    # Streamlit test runner UI
│   ├── user_config.py                 # RBAC user profile configuration
│   ├── api_server.py                  # Optional REST API server
│   └── performance_metrics.db         # SQLite DB for metrics tracking
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com/) installed and running (for local LLM fallback)
- AWS credentials with access to Claude 3.5 Sonnet via Bedrock (for enterprise mode)

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/navalsingh9/syngenta_ai_agent.git
cd syngenta_ai_agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
CLAUDE_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_DEFAULT_REGION=us-east-1
```

> ⚠️ Never commit your `.env` file. It is already listed in `.gitignore`.

### 5. Pull the LLaMA 3 model via Ollama (local fallback)

```bash
ollama pull llama3
ollama run llama3
```

### 6. Generate the transaction database (first-time setup)

```bash
python src/generate_sql_db.py
```

### 7. Extract and evaluate policy controls (first-time setup)

```bash
python src/extract_controls.py
python src/map_controls.py
python src/evaluate_controls.py
```

---

## Running the App

```bash
streamlit run src/Home.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Configuration

### User Role & Region (RBAC)

Edit `src/user_config.py` to simulate different users:

```python
USER_METADATA = {
    "user_id": "rahul123",
    "role": "Planner",   # Options: "Planner", "Finance", "Admin"
    "region": "India"    # Options: "India", "Global", "EU", "US"
}
```

### Sidebar Options

| Option | Description |
|---|---|
| **Choose Language Model** | Switch between Claude 3.5 Sonnet and Ollama (LLaMA 3) |
| **Enable Debug Mode** | Logs all SQL queries and policy answers to `debug_log.txt` |
| **Refresh Policy Vector Store** | Rebuilds the FAISS index from the `docs/` folder |
| **Clear Debug Log** | Wipes the current debug log file |
| **Performance Metrics** | View latency, exact match %, and semantic match % trends |

---

## Example Queries

### Structured Data (NL2SQL)

- *"What is the total sales in the Southwest region last quarter?"*
- *"Which orders had the highest shipping delay in the past year?"*
- *"What are the top 10 products by return volume?"*
- *"Are we using the right shipping modes for high-value international orders?"*

### Policy Documents

- *"What's the definition of slow-moving inventory in our policy?"*
- *"What are the ethical sourcing requirements for suppliers?"*
- *"What does the Data Security policy say about access control?"*

### Hybrid (Policy + Data)

- *"Which suppliers fail to meet ethical sourcing standards based on recent transactions?"*
- *"Are our current inventory levels compliant with the Inventory policy?"*

---

## Policy Documents

The `docs/` folder contains 25+ PDF policy documents covering:

- Code of Conduct (COC)
- Data Security
- Risk Management
- Inventory Management
- Environmental Sustainability
- Supplier Relationship Management (SRM)
- Trade Compliance
- Transportation & Logistics
- Health, Safety & Environment (HSE)
- Demand Forecasting & Planning
- Capacity Planning
- Contract Management & Negotiation
- Warehouse & Storage
- Order Management
- And many more…

To add new policies, drop PDF files into the `docs/` folder and click **Refresh Policy Vector Store** in the sidebar.

---

## Testing

### Run the CLI test suite

```bash
python src/test_runner.py
```

### Run the Streamlit test UI

```bash
streamlit run src/test_gui.py
```

Test cases are stored in `src/test_cases.jsonl`. Metrics tracked per query:

| Metric | Description |
|---|---|
| **Exact Match** | Generated SQL matches expected SQL exactly |
| **Semantic Match** | Cosine similarity between generated and expected SQL embeddings |
| **Levenshtein Distance** | Edit distance between generated and expected SQL |
| **Latency** | Time taken to generate and execute the query |

---

## Security

- All API keys are stored in `.env` and never committed to the repository
- `.gitignore` excludes `.env`, `outputs/`, `data/`, and local cache files
- Role-based and region-based access control is enforced via `user_config.py`

---

## Team

**Team IdliWadaSambhar** — Paradox 2025 Hackathon

| Name | Email |
|---|---|
| Naval Singh | 21f1006368@ds.study.iitm.ac.in |

---
