from fastapi import FastAPI
from pydantic import BaseModel

from vector_db import VectorDB

db = VectorDB("data/vectors.json")
app = FastAPI(title="Vector DB")


class UpsertRequest(BaseModel):
    id: int
    vector: list[float]
    payload: dict = {}


class SearchRequest(BaseModel):
    vector: list[float]
    top_k: int = 5


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/vectors")
def upsert_vector(request: UpsertRequest):
    db.upsert(request.id, request.vector, request.payload)
    db.save()
    return {"status": "ok"}


@app.post("/search")
def search_vectors(request: SearchRequest):
    results = db.search(request.vector, request.top_k)
    return [{"payload": payload, "score": score} for payload, score in results]
