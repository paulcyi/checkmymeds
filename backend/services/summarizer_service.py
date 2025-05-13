"""
summarizer_service.py
LLM-driven patient-friendly explanation of drug-label interaction text.
"""

import os
from functools import lru_cache
from typing import Optional

# Load environment config
PROVIDER = os.getenv("PROVIDER", "openai")
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
TIMEOUT = int(os.getenv("LLM_TIMEOUT", "15"))
DEBUG = os.getenv("DEBUG_SUMMARIZER", "0") == "1"

# Set up client
if PROVIDER == "openai":
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=TIMEOUT)
elif PROVIDER == "litellm":
    from litellm import completion
else:
    raise RuntimeError(f"Unsupported PROVIDER '{PROVIDER}'")

# Prompt engineering
_SYSTEM = (
    "You are a clinical-pharmacist assistant. "
    "Rewrite the following FDA drug-label interaction in 1–2 short sentences, "
    "at a 7th-grade reading level. Focus on what could go wrong and what the patient should do. "
    "Do not say you're an AI."
)

@lru_cache(maxsize=2048)
def summarise(drug_a: str, drug_b: str, interaction_text: str) -> Optional[str]:
    """Return a plain-language, safety-focused summary of the interaction."""
    interaction_text = interaction_text.strip()
    if not interaction_text:
        return None

    prompt = (
        f"Drug A: {drug_a}\n"
        f"Drug B: {drug_b}\n\n"
        f"FDA-label text:\n{interaction_text}"
    )

    if DEBUG:
        print(f"[DEBUG] Prompt to {PROVIDER} ({MODEL}):\n{prompt}\n")

    try:
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

    except Exception as e:
        if DEBUG:
            print(f"[ERROR] summarise() failed: {e}")
        return None

    raise RuntimeError("summarise() provider dispatch failed unexpectedly")
