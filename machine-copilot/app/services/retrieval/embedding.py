"""Embedding provider — swappable behind a tiny interface.

Default: a local TF-IDF vectorizer (scikit-learn). This runs with zero
network calls, which matters on a shop floor that may be offline, and is
sufficient to demonstrate exact-term matching against alarm codes and part
numbers (where lexical match often beats semantic embeddings anyway).

To upgrade to a semantic embedding model in production, implement the same
`fit`/`transform` interface using your provider of choice (Voyage, Gemini,
OpenAI, or a local sentence-transformers model) and swap it in
`qdrant_service.py` — nothing else in the pipeline needs to change.
"""
from sklearn.feature_extraction.text import TfidfVectorizer


class LocalTfidfEmbedder:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=20_000,
        )
        self._fitted = False

    def fit_transform(self, texts: list[str]):
        matrix = self.vectorizer.fit_transform(texts)
        self._fitted = True
        return matrix

    def transform(self, texts: list[str]):
        if not self._fitted:
            raise RuntimeError("Embedder not fitted — run ingestion first.")
        return self.vectorizer.transform(texts)
