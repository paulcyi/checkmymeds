from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os
from redis.asyncio import Redis
from services.drug_service import fetch_rxcui, fetch_interactions

app = FastAPI(title="CheckMyMeds API", version="0.1.0")
redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))

class CheckRequest(BaseModel):
    drugs: List[str]

class InteractionResponse(BaseModel):
    interactions: List[str]
    source: str

async def _cached_key(drugs: List[str]) -> str:
    return "|".join(sorted(drugs)).lower()

async def get_interactions(drugs: List[str]) -> InteractionResponse:
    key = await _cached_key(drugs)
    cached = await redis.get(key)
    if cached:
        return InteractionResponse(**json.loads(cached))

    # 🧠 NEW: Fetch RxCUIs and interactions
    rxcuis = []
    for name in drugs:
        rxcui = await fetch_rxcui(name)
        if rxcui:
            rxcuis.append(rxcui)

    interactions = await fetch_interactions(rxcuis)
    source = "rxnav" if interactions else "none"

    response = InteractionResponse(interactions=interactions or [], source=source)
    await redis.set(key, response.json(), ex=CACHE_TTL_SECONDS)
    return response

@app.post("/api/check", response_model=InteractionResponse)
async def check_endpoint(payload: CheckRequest):
    if len(payload.drugs) < 2:
        raise HTTPException(status_code=400, detail="Provide at least two drug names.")
    return await get_interactions(payload.drugs)

@app.on_event("startup")
async def startup_event():
    try:
        await redis.ping()
    except Exception as e:
        print("[WARN] Redis not available:", e)

@app.on_event("shutdown")
async def shutdown_event():
    await redis.aclose()
