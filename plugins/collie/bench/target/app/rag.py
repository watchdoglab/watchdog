"""Knowledge base: every tenant's uploaded docs live in one index."""
import numpy as np

INDEX = []  # (tenant_id, text, vector)


def ingest(tenant_id, text, embed):
    INDEX.append((tenant_id, text, embed(text)))


def search(query, embed=lambda t: np.ones(8), k=5):
    q = embed(query)
    scored = sorted(INDEX, key=lambda d: -float(q @ d[2]))
    return "\n---\n".join(text for _, text, _ in scored[:k])
