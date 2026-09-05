"""
Minimal LiteLLM gateway starter.

LiteLLM gives one unified, OpenAI-compatible call shape across providers,
so switching or falling back between models doesn't change calling code.
"""

import litellm
from dotenv import load_dotenv

load_dotenv()

PRIMARY_MODEL = "claude-haiku-4-5"
FALLBACK_MODELS = ["gpt-4o-mini"]


def chat(prompt: str) -> str:
    """Send a prompt through LiteLLM, falling back to another provider on failure."""
    response = litellm.completion(
        model=PRIMARY_MODEL,
        messages=[{"role": "user", "content": prompt}],
        fallbacks=FALLBACK_MODELS,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print(chat("Say hello in one sentence."))
