from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
import json
import os
from redis.asyncio import Redis
from tenacity import retry, stop_after_attempt, wait_exponential

# --- Configuration ---------------------------------------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
RXNAV_URL = "https://rxnav.nlm.nih.gov/REST/interaction/list.json"
OPENFDA_URL = "https://api.fda.gov/drug/label.json"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))  # 24h

# --- App Init --------------------------------------------------------------
app = FastAPI(title="CheckMyMeds API", version="0.1.0")
redis = Redis.from_url(REDIS_URL, decode_responses=True)

# --- Pydantic Schemas ------------------------------------------------------
class CheckRequest(BaseModel):
    drugs: List[str]

class InteractionResponse(BaseModel):
    interactions: List[str]
    source: str

# --- Helper Functions ------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
async def _rxnav_request(drugs: List[str]) -> Optional[List[str]]:
    # RxNav expects a "+" separated string of RXCUIs or drug names.
    query = "+".join(drugs)
    url = f"{RXNAV_URL}?rxcuis={query}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    # TODO: Parse RxNav JSON to extract interaction descriptions
    # Return None if no interactions found
    # For now, just return empty list as placeholder
    return []

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
async def _openfda_fallback(drugs: List[str]) -> Optional[List[str]]:
    # Very naive fallback: search each drug label for "drug_interactions" section
    # In production, replace with more robust NLP / indexing
    interactions: List[str] = []
    async with httpx.AsyncClient(timeout=10) as client:
        for drug in drugs:
            params = {"search": f"openfda.generic_name:\"{drug}\"", "limit": 1}
            r = await client.get(OPENFDA_URL, params=params)
            if r.status_code == 200:
                doc = r.json()
                # Parse doc for interactions (drug_interactions field)
                sections = doc.get("results", [{}])[0].get("drug_interactions", [])
                interactions.extend(sections)
    return interactions if interactions else None

async def _cached_key(drugs: List[str]) -> str:
    return "|".join(sorted(drugs)).lower()

async def get_interactions(drugs: List[str]) -> InteractionResponse:
    key = await _cached_key(drugs)
    cached = await redis.get(key)
    if cached:
        cached_obj = json.loads(cached)
        return InteractionResponse(**cached_obj)

    interactions = await _rxnav_request(drugs)
    source = "rxnav"

    if not interactions:
        interactions = await _openfda_fallback(drugs)
        source = "openfda" if interactions else "none"

    response = InteractionResponse(interactions=interactions or [], source=source)
    await redis.set(key, response.json(), ex=CACHE_TTL_SECONDS)
    return response

# --- Routes ----------------------------------------------------------------
@app.post("/api/check", response_model=InteractionResponse)
async def check_endpoint(payload: CheckRequest):
    if len(payload.drugs) < 2:
        raise HTTPException(status_code=400, detail="Provide at least two drug names.")
    return await get_interactions(payload.drugs)

# --- Startup / Shutdown ----------------------------------------------------
@app.on_event("startup")
async def startup_event():
    # Ensure Redis connection is ready
    try:
        await redis.ping()
    except Exception as e:
        print("[WARN] Redis not available:", e)

@app.on_event("shutdown")
async def shutdown_event():
    await redis.aclose()

# To run locally:
# $ uvicorn backend.main:app --reload --port 8000
