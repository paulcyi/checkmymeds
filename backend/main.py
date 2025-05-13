from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import json
import redis.asyncio as redis
import asyncio

from services.drug_service import fetch_rxcui, fetch_interactions
from services.openfda_service import OpenFDAService


class CheckPayload(BaseModel):
    drugs: list[str]


app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    app.state.http = httpx.AsyncClient()
    app.state.openfda = OpenFDAService(app.state.http)
    app.state.redis = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    await app.state.http.aclose()
    await app.state.redis.close()

@app.post("/api/check")
async def check(payload: CheckPayload, request: Request):
    drugs = [d.lower() for d in payload.drugs]
    cache_key = "-".join(sorted(drugs))

    redis_client = request.app.state.redis
    openfda = request.app.state.openfda

    # 1. Check cache
    if cached := await redis_client.get(cache_key):
        return JSONResponse(content=json.loads(cached))

    # 2. Try RxNav via drug_service
    rxcuis = await asyncio.gather(*(fetch_rxcui(d) for d in drugs))
    rxcuis_clean = [r for r in rxcuis if r]
    interactions = await fetch_interactions(rxcuis_clean)
    source = "rxnav"

    # 3. Fallback to OpenFDA if RxNav fails
    if not interactions:
        interactions = await openfda.get_interactions(drugs)
        source = "openfda" if interactions else "none"

    result = {"interactions": interactions, "source": source}
    await redis_client.set(cache_key, json.dumps(result), ex=86_400)

    return JSONResponse(content=result)

@app.get("/api/ping")
async def ping():
    return {"status": "ok"}
