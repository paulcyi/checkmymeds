"""
summarizer_service.py
LLM-driven patient-friendly explanation of drug-label interaction text.
"""

import os
from functools import lru_cache
from typing import Optional

# Load environment config
PROVIDER = os.getenv("PROVIDER", "openai")  # Can support grok, litellm, ollama later
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
TIMEOUT = int(os.getenv("LLM_TIMEOUT", "15"))

# Set up client based on provider
if PROVIDER == "openai":
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=TIMEOUT)
elif PROVIDER == "litellm":
    from litellm import completion
else:
    raise RuntimeError(f"Unsupported PROVIDER '{PROVIDER}'")

# System prompt to guide the model
_SYSTEM = (
    "You are a clinical-pharmacist assistant. "
    "Rewrite the following FDA drug-label interaction in 1–2 short sentences, "
    "at a 7th-grade reading level. Focus on what could go wrong and what the patient should do. "
    "Do not say you're an AI."
)

@lru_cache(maxsize=2048)
def summarise(drug_a: str, drug_b: str, interaction_text: str) -> str:
    """Return a plain-language, safety-focused summary of the interaction."""
    if not interaction_text.strip():
        return ""

    prompt = (
        f"Drug A: {drug_a}\n"
        f"Drug B: {drug_b}\n\n"
        f"FDA-label text:\n{interaction_text}"
    )

    if PROVIDER == "openai":
        resp = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.4
        )
        return resp.choices[0].message.content.strip()

    elif PROVIDER == "litellm":
        resp = completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.4,
            stream=False,
        )
        return resp["choices"][0]["message"]["content"].strip()

    raise RuntimeError("summarise() provider dispatch failed")
