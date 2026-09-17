from __future__ import annotations
import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

STOP = {"please", "requested", "again", "add", "the", "a", "an", "to", "for"}

def normalize(text):
    words = re.findall(r"[a-z0-9]+", str(text).lower())
    return " ".join(w for w in words if w not in STOP)

def similarity(query, candidates):
    candidates = [str(x) for x in candidates]
    if not candidates:
        return []
    corpus = [normalize(query)] + [normalize(x) for x in candidates]
    matrix = TfidfVectorizer(ngram_range=(1, 2)).fit_transform(corpus)
    cos = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    out = []
    for text, c in zip(candidates, cos):
        seq = SequenceMatcher(None, normalize(query), normalize(text)).ratio()
        out.append((text, float(max(c, seq))))
    return sorted(out, key=lambda x: x[1], reverse=True)
