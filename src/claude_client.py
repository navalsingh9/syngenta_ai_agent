import os
import requests
from typing import Optional
from pydantic import Field
from langchain.llms.base import LLM

class ClaudeBedrockLLM(LLM):
    api_key: Optional[str] = Field(default_factory=lambda: os.getenv("CLAUDE_SECRET_ACCESS_KEY"))
    model_id: str = Field(default="claude-3.5-sonnet")
    url: str = "https://quchnti6xu7yzw7hfzt5yjqtvi0kafsq.lambda-url.eu-central-1.on.aws/"

    @property
    def _llm_type(self) -> str:
        return "claude-bedrock"

    def _call(self, prompt: str, stop: Optional[list[str]] = None, run_manager=None, **kwargs) -> str:
        if not self.api_key:
            return "[Error] Claude API key is missing. Set CLAUDE_SECRET_ACCESS_KEY in .env or environment variables."

        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": self.api_key,
            "prompt": prompt,
            "model_id": self.model_id,
            "model_params": {
                "max_tokens": 1024,
                "temperature": 0.7
            }
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["response"]["content"][0]["text"]
        except Exception as e:
            return f"[Error calling Claude API] {e}"
