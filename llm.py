import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"

FALLBACK = {
    "severity": "unknown",
    "suggestion": "LLM unavailable — manual review recommended.",
}


def analyze_log(log_text: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return FALLBACK

    prompt = (
        "You are a log triage assistant. Read the log below and respond "
        "with ONLY a JSON object with two keys: "
        '"severity" (one of: info, warn, error, critical) and '
        '"suggestion" (one short sentence with the likely fix).\n\n'
        f"LOG:\n{log_text}"
    )

    try:
        response = httpx.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "temperature": 0.2,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        return {
            "severity": data.get("severity", "unknown"),
            "suggestion": data.get("suggestion", ""),
        }
    except Exception as e:
        print(f"[llm] error: {e}")
        return FALLBACK