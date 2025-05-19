# backend/services/nlp_utils.py
import re
from functools import lru_cache
from typing import List

SYNONYMS: dict[str, List[str]] = {
    "tramadol": ["opioid", "analgesic"],
    "sertraline": ["ssri", "antidepressant"],
}

@lru_cache(maxsize=1024)
def _pattern(word: str) -> re.Pattern[str]:
    """
    Compile a case-insensitive whole-word regex that also allows
    a trailing plural 's' (ibuprofen / ibuprofens).
    """
    return re.compile(rf"\b{re.escape(word)}s?\b", re.I)

def mentions_drug(text: str, drug: str) -> bool:
    """
    True if `text` mentions `drug` (singular or plural) **or** any synonym.
    """
    txt = text.lower()
    if _pattern(drug.lower()).search(txt):
        return True

    for syn in SYNONYMS.get(drug.lower(), []):
        if _pattern(syn).search(txt):
            return True

    return False
