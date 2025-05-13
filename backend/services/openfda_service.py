# backend/services/openfda_service.py
from __future__ import annotations

import asyncio
import re
from typing import List, Dict

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class OpenFDAService:
    """Pulls interaction text from the openFDA Drug Label API."""
    BASE_URL = "https://api.fda.gov/drug/label.json"
    LIMIT = 50  # grab a healthy slice in case the first result is a homeopathic dud

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    # ---------- low-level ---------- #
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())   # ← same pattern as api_utils.py
    async def _fetch_label(self, generic: str) -> dict | None:
        params = {
            "search": f'openfda.generic_name:"{generic}"',        # field documented by FDA :contentReference[oaicite:2]{index=2}
            "limit": self.LIMIT,
        }
        r = await self.client.get(self.BASE_URL, params=params, timeout=10)
        if r.status_code != 200:
            return None
        json = r.json()
        return (json.get("results") or [None])[0]

    async def _interaction_blob(self, generic: str) -> str:
        label = await self._fetch_label(generic)
        if not label:
            return ""
        # FDA puts section text in lists of strings
        section = label.get("drug_interactions") or []
        return " ".join(section).lower()

    # ---------- public API ---------- #
    async def get_interactions(
        self, generics: List[str]
    ) -> List[Dict[str, str]]:
        """Return pair-wise interaction summaries if any generic is mentioned in the other’s label."""
        blobs = await asyncio.gather(
            *[self._interaction_blob(g) for g in generics]
        )
        interactions: List[Dict[str, str]] = []

        for i, ga in enumerate(generics):
            for j in range(i + 1, len(generics)):
                gb = generics[j]
                hit_a = gb.lower() in blobs[i]
                hit_b = ga.lower() in blobs[j]

                if hit_a or hit_b:
                    raw = blobs[i] if hit_a else blobs[j]
                    snippet = self._extract_sentence(raw, gb if hit_a else ga)
                    interactions.append(
                        {
                            "drugA": ga,
                            "drugB": gb,
                            "summary": snippet,
                            "source": "openfda",
                        }
                    )
        return interactions

    # ---------- helpers ---------- #
    @staticmethod
    def _extract_sentence(text: str, needle: str, max_len: int = 300) -> str:
        """Grab up to one full sentence containing *needle*; hard-trim if gigantic."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for s in sentences:
            if needle.lower() in s:
                return (s[: max_len - 3] + "...") if len(s) > max_len else s
        return text[: max_len] + "..."
