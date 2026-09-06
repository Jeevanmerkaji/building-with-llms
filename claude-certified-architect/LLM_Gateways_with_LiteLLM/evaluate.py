"""
Minimal eval harness for the LiteLLM gateway (config.yaml).

Runs a small set of prompt/check pairs against each configured model
through the proxy. Exits non-zero if any case fails, so this can gate
a build the way machine-copilot's eval gate does.
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROXY_URL = os.environ.get("PROXY_URL", "http://localhost:4000")
MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "")
MODELS = ["claude-haiku-4-5", "gpt-4o-mini"]

CASES = [
    {
        "prompt": "Reply with exactly one word: hello",
        "check": lambda reply: "hello" in reply.lower(),
    },
    {
        "prompt": "What is 12 + 30? Reply with only the number.",
        "check": lambda reply: "42" in reply,
    },
]

client = OpenAI(api_key=MASTER_KEY, base_url=PROXY_URL)


def run_eval() -> bool:
    all_passed = True
    for model in MODELS:
        print(f"\n== {model} ==")
        for case in CASES:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": case["prompt"]}],
                )
                reply = response.choices[0].message.content
                passed = case["check"](reply)
            except Exception as e:
                reply = f"ERROR: {e}"
                passed = False

            status = "PASS" if passed else "FAIL"
            all_passed = all_passed and passed
            print(f"  [{status}] {case['prompt']!r} -> {reply!r}")

    return all_passed


if __name__ == "__main__":
    ok = run_eval()
    sys.exit(0 if ok else 1)
