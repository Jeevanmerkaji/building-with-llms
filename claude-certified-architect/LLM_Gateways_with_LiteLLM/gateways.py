"""
Client for the LiteLLM proxy — see config.yaml for the provider setup and
"Run the proxy" in README.md for how to start it.

The proxy holds each provider's real API key server-side. This client only
ever uses LITELLM_MASTER_KEY, so switching or adding providers doesn't
change any application code.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROXY_URL = "http://localhost:4000"
PRIMARY_MODEL = "claude-haiku-4-5"

client = OpenAI(api_key=os.environ["LITELLM_MASTER_KEY"], base_url=PROXY_URL)


def chat(prompt: str, model: str = PRIMARY_MODEL) -> str:
    """Send a prompt to the LiteLLM proxy. Fallback to gpt-4o-mini is configured server-side."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print(chat("Say hello in one sentence."))
