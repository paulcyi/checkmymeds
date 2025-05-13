# --- Env config ---
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

# --- FastAPI setup ---
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from backend.services.interaction_service import find_interactions
from backend.services.summarizer_service import summarise


app = FastAPI()

# --- Pydantic models ---

class Interaction(BaseModel):
    drugA: str
    drugB: str
    summary: str
    severity: str

class InteractionRequest(BaseModel):
    drugs: List[str]

class InteractionResponse(BaseModel):
    interactions: List[Interaction]
    source: str
    ai_summary: str | None = None  # New field for GPT summary


# --- Routes ---

@app.post("/api/check", response_model=InteractionResponse)
async def check(payload: InteractionRequest):
    # Get pairwise interactions + source + any fallback label_blob
    try:
        interactions, source, label_blob = await find_interactions(payload.drugs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Trigger AI summary only if OpenFDA provided label text
    ai_summary: str | None = None
    if label_blob:
        ai_summary = summarise(
            payload.drugs[0],  # assume pairwise
            payload.drugs[1],
            label_blob
        )

    return InteractionResponse(
        interactions=interactions,
        source=source,
        ai_summary=ai_summary
    )
