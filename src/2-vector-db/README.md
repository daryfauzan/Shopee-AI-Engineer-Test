# Vector DB from Scratch + Cosine Similarity

A minimal vector database built from scratch (no vector-DB software, no ML/vector libraries) —
in-memory storage with JSON-file persistence, and search powered by a hand-written cosine
similarity function. The core (`vector_db.py`, `cosine_similarity.py`, `vectorize.py`) has zero
dependencies; `app.py` adds FastAPI/uvicorn only to expose it as a deployable HTTP service.

## Project structure

```
2-vector-db/
├── vector_db.py           # The "database": upsert, save/load, search
├── cosine_similarity.py   # Manual cosine similarity (no numpy/scipy/sklearn)
├── vectorize.py           # Tiny bag-of-words text -> vector helper (also no libraries)
├── main.py                # CLI demo: stores vectors, queries, prints ranked results
├── app.py                 # HTTP API exposing the same VectorDB (for deployment)
├── Dockerfile             # Containerizes app.py as a standalone service
└── pyproject.toml
```

## Setup

Requires Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
uv sync
```

## Usage

```bash
uv run main.py
```

This will:
1. Build a bag-of-words vector for a handful of toy documents (`vectorize.py`).
2. Store them in `VectorDB` (`vector_db.py`), persisted to `data/vectors.json`.
3. Vectorize a query and rank every stored vector against it using `cosine_similarity()`.

Example output:

```
Query: 'the cat and the dog are pets'

  0.5893  the cat sat on the mat
  0.5893  the dog played in the park
  0.4082  cats and dogs are popular pets
  0.2981  the stock market rose today
  0.2981  investors watched the market closely
```

## Deployment (`app.py` + Docker)

`vector_db.py` is storage/search logic only — it has no server. `app.py` wraps it in a small
FastAPI service so it can run as a standalone, self-hosted deployment (no vendor, no managed
service), and `Dockerfile` containerizes that service.

```bash
docker build -t vector-db .
docker run -d --name vector-db -p 8000:8000 vector-db
```

Endpoints:

| Method | Path       | Body                                          | Description                    |
|--------|------------|------------------------------------------------|---------------------------------|
| GET    | `/health`  | —                                              | Liveness check                  |
| POST   | `/vectors` | `{"id": 0, "vector": [...], "payload": {...}}` | Upsert a vector                 |
| POST   | `/search`  | `{"vector": [...], "top_k": 5}`                | Rank stored vectors by cosine similarity |

```bash
curl -X POST localhost:8000/vectors \
  -H "Content-Type: application/json" \
  -d '{"id": 0, "vector": [1, 0, 1], "payload": {"text": "hello"}}'

curl -X POST localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"vector": [1, 0, 1], "top_k": 1}'
```

The container stores data at `data/vectors.json` inside its own filesystem, so data is lost when
the container is removed. Mount a volume to persist it across restarts:

```bash
docker run -d --name vector-db -p 8000:8000 -v "$(pwd)/data:/app/data" vector-db
```

To run it locally without Docker: `uv run uvicorn app:app --reload`.

## How the database works (`vector_db.py`)

`VectorDB` is a dict of `id -> {vector, payload}`, loaded from / saved to a JSON file so data
survives across runs — no server, no external process.

- `upsert(id, vector, payload)` — store or replace a vector.
- `save()` — persist the store to disk as JSON.
- `search(query_vector, top_k)` — score every stored vector against the query with
  `cosine_similarity()` and return the `top_k` highest matches.

Search is a brute-force linear scan (O(n) per query) — the right trade-off at this scale; a real
deployment would add an index (e.g. HNSW) once brute force stops being fast enough.

## Cosine similarity (`cosine_similarity.py`)

```python
def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sqrt(sum(x * x for x in a))
    norm_b = sqrt(sum(y * y for y in b))
    return dot_product / (norm_a * norm_b)
```

`cos(θ) = (a · b) / (‖a‖ · ‖b‖)` — the dot product of two vectors divided by the product of their
magnitudes. Result ranges from -1 (opposite) to 1 (identical direction), with 0 meaning orthogonal
(unrelated). Run `uv run cosine_similarity.py` for a few sanity checks against known vectors.
