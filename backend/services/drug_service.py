from typing import List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

RXNAV_BASE_URL = "https://rxnav.nlm.nih.gov/REST"

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def fetch_rxcui(drug: str) -> str:
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(f"{RXNAV_BASE_URL}/rxcui.json", params={"name": drug})
        res.raise_for_status()
        data = res.json()
        rxcui = data.get("idGroup", {}).get("rxnormId", [None])[0]
        print(f"[DEBUG] RxCUI for '{drug}':", rxcui)
        return rxcui


@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def fetch_interactions(rxcuis: List[str]) -> List[str]:
    if len(rxcuis) < 2:
        print("[DEBUG] Not enough RxCUIs for interaction check:", rxcuis)
        return []

    rxcui_str = "+".join(rxcuis)
    url = f"{RXNAV_BASE_URL}/interaction/list.json"
    print(f"[DEBUG] Fetching interactions for: {rxcui_str}")

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(url, params={"rxcuis": rxcui_str})
        print("[DEBUG] Raw status code:", res.status_code)
        print("[DEBUG] Response text:", await res.aread())
        if res.status_code == 404:
            return []
        res.raise_for_status()
        data = res.json()

    results = []
    groups = data.get("fullInteractionTypeGroup", [])
    for group in groups:
        for interaction_type in group.get("fullInteractionType", []):
            for interaction_pair in interaction_type.get("interactionPair", []):
                desc = interaction_pair.get("description")
                if desc:
                    results.append(desc)

    return results
