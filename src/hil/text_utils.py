from __future__ import annotations
import unicodedata, hashlib

def ascii7(s: str) -> str:
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")

def hash_preview(text: str, prefix_len: int = 40) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    prefix = text[:prefix_len].replace("\n", " ")
    return f"{prefix}...|{h}" if len(text) > prefix_len else f"{text}|{h}"
