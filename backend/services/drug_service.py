from typing import List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

RXNAV_BASE_URL = "https://rxnav.nlm.nih.gov/REST"

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def fetch_rxcui(drug: str) -> str:
    """Get RxCUI (RxNorm Concept Unique Identifier) for a drug name."""
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{RXNAV_BASE_URL}/rxcui.json", params={"name": drug})
        res.raise_for_status()
        data = res.json()
        return data.get("idGroup", {}).get("rxnormId", [None])[0]

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def fetch_interactions(rxcuis: List[str]) -> List[str]:
    """Fetch interaction descriptions for a list of RxCUIs."""
    if len(rxcuis) < 2:
        return []

    rxcui_str = "+".join(rxcuis)
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{RXNAV_BASE_URL}/interaction/list.json", params={"rxcuis": rxcui_str})
        res.raise_for_status()
        data = res.json()

    results = []
    interactions = data.get("fullInteractionTypeGroup", [])
    for group in interactions:
        for interactionType in group.get("fullInteractionType", []):
            for interactionPair in interactionType.get("interactionPair", []):
                desc = interactionPair.get("description")
                if desc:
                    results.append(desc)

    return results
