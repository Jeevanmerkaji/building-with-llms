# Multi-Agent Customer Support

A small, self-contained customer-support demo built with Claude. It demonstrates an agentic tool-use loop, a coordinator that delegates work to subagents, structured context passing, and safe escalation to a human agent.

## Prerequisites

- Python 3.9+
- An Anthropic API key

## Run

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
python Agent.py
```

The script uses `claude-haiku-4-5` and simulated customer/order tools, so no external backend is required.
