from fastapi import FastAPI
from pydantic import BaseModel
from sql_agent import ask_data_question
from document_agent import ask_documents, load_policy_vectorstore
from claude_client import ClaudeBedrockLLM
from langchain_ollama import OllamaLLM
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
api_key = os.getenv("CLAUDE_SECRET_ACCESS_KEY")
# Enable CORS for all origins (Android/web compatibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load policy vector index once at startup
vs = load_policy_vectorstore()

class QueryRequest(BaseModel):
    question: str
    model: str  # Expected values: "claude" or "ollama"

@app.post("/ask")
def ask_agent(request: QueryRequest):
    try:
        # Choose model based on request
        llm = ClaudeBedrockLLM(api_key) if "claude" in request.model.lower() else OllamaLLM(model="llama3")

        # Perform SQL + document-based QA
        sql, result = ask_data_question(request.question, llm)
        policy_answer = ask_documents(request.question, vs,llm)

        # Handle result formatting
        if not isinstance(result, str):
            try:
                result = result.to_string(index=False)
            except:
                result = str(result)

        return {
            "sql": sql,
            "result": result,
            "policy_answer": policy_answer
        }

    except Exception as e:
        return {"error": str(e)}
