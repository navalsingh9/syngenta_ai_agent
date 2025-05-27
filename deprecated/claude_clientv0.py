import requests
from langchain.llms.base import LLM
from pydantic import Field

class ClaudeBedrockLLM(LLM):
    api_key: str = Field(...)
    model_id: str = Field(default="claude-3.5-sonnet")
    url: str = "https://quchnti6xu7yzw7hfzt5yjqtvi0kafsq.lambda-url.eu-central-1.on.aws/"

    @property
    def _llm_type(self) -> str:
        return "claude-bedrock"

    def _call(self, prompt: str, stop: list[str] | None = None, run_manager=None, **kwargs) -> str:
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
        response = requests.post(self.url, headers=headers, json=payload)
        try:
            return response.json()["response"]["content"][0]["text"]
        except Exception as e:
            return f"[Error calling Claude API] {e}"
