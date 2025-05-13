# backend/services/interaction_service.py

from typing import List, Tuple
from backend.services import drug_service

async def find_interactions(drugs: List[str]) -> Tuple[List[dict], str, str]:
    """Fetch drug interaction descriptions and return with metadata for LLM summarization."""

    if len(drugs) < 2:
        return [], "none", ""

    # Fetch RxCUIs for input drugs
    rxcuis = [await drug_service.fetch_rxcui(drug) for drug in drugs]
    rxcuis = [r for r in rxcuis if r is not None]

    if len(rxcuis) < 2:
        return [], "none", ""

    # Fetch interaction descriptions
    descriptions = await drug_service.fetch_interactions(rxcuis)
    if not descriptions:
        return [], "none", ""

    # Build individual interactions
    interactions = [{
        "drugA": drugs[0],
        "drugB": drugs[1],
        "summary": desc,
        "severity": "unknown"
    } for desc in descriptions]

    # Combine into single blob for LLM summarization
    label_blob = "\n\n".join(descriptions)

    return interactions, "openfda", label_blob
