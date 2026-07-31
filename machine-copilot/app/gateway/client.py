"""LLM gateway — routes to a cloud model when available, falls back to a
deterministic, fully-local templated responder when it isn't.

This is the piece that matters most for uptime on a factory floor: a
network blip or missing API key should never mean the assistant goes
completely silent, it should mean the assistant answers with less
elaboration but still grounded in the retrieved source text.
"""
from app.config import settings


def _offline_fallback(question: str, context_chunks: list[str]) -> str:
    """Extractive, template-based answer built only from retrieved chunks.
    No network call, no model — guaranteed to work air-gapped."""
    if not context_chunks:
        return (
            "I couldn't find anything in the indexed manuals or alarm tables "
            "for this question. Please check the machine's physical manual "
            "or contact support."
        )
    joined = "\n\n---\n\n".join(context_chunks)
    return (
        f"Based on the machine's documentation, here is the relevant "
        f"information for: \"{question}\"\n\n{joined}\n\n"
        f"(offline mode — showing retrieved source text directly; "
        f"connect to enable the full conversational assistant)"
    )


def generate(question: str, context_chunks: list[str], system_prompt: str) -> str:
    if settings.offline_mode or not settings.anthropic_api_key:
        return _offline_fallback(question, context_chunks)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        context_block = "\n\n---\n\n".join(context_chunks) if context_chunks else "(no matching documents found)"
        response = client.messages.create(
            model=settings.primary_model,
            max_tokens=600,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Retrieved source material:\n{context_block}\n\n"
                        f"Technician question: {question}\n\n"
                        "Answer using ONLY the retrieved material above. If it "
                        "doesn't contain the answer, say so explicitly rather "
                        "than guessing."
                    ),
                }
            ],
        )
        return "".join(block.text for block in response.content if hasattr(block, "text"))
    except Exception as exc:  # network error, bad key, rate limit, etc.
        fallback = _offline_fallback(question, context_chunks)
        return f"[cloud model unavailable — falling back to offline mode: {exc}]\n\n{fallback}"
