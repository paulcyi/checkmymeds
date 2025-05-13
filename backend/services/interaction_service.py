# backend/services/interaction_service.py

from typing import List, Tuple
from backend.services import drug_service
from backend.services.openfda_service import OpenFDAService
import httpx

async def find_interactions(drugs: List[str]) -> Tuple[List[dict], str, str]:
    if len(drugs) < 2:
        print("[FIND] Too few drugs.")
        return [], "none", ""

    # --- RxNav Phase ---
    rxcuis = [await drug_service.fetch_rxcui(drug) for drug in drugs]
    rxcuis = [r for r in rxcuis if r is not None]
    print(f"[FIND] RxCUIs: {rxcuis}")

    if len(rxcuis) >= 2:
        descriptions = await drug_service.fetch_interactions(rxcuis)
        print(f"[FIND] RxNav Descriptions: {descriptions}")
        if descriptions:
            interactions = [{
                "drugA": drugs[0],
                "drugB": drugs[1],
                "summary": desc,
                "severity": "unknown"
            } for desc in descriptions]
            label_blob = "\n\n".join(desc for desc in descriptions)
            print("[FIND] Returning RxNav results")
            return interactions, "openfda-rxnav", label_blob

    print("[FIND] RxNav failed — trying OpenFDA fallback...")

    # --- OpenFDA Fallback ---
    async with httpx.AsyncClient() as client:
        service = OpenFDAService(client)
        interactions = await service.get_interactions(drugs)
        print(f"[FIND] OpenFDA interactions: {interactions}")

    if interactions:
        label_blob = "\n\n".join(i["summary"] for i in interactions)
        print("[FIND] Returning OpenFDA results")
        return interactions, "openfda", label_blob

    # --- Fallback: Mock forced interaction for demo/testing ---
    interactions = [{
        "drugA": drugs[0],
        "drugB": drugs[1],
        "summary": "Sertraline may increase the risk of serotonin syndrome when combined with tramadol.",
        "severity": "high"
    }]
    label_blob = interactions[0]["summary"]
    print("[FIND] Returning MOCK interaction for demo fallback")
    return interactions, "mock", label_blob
