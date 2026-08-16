import json
from pathlib import Path

from cosine_similarity import cosine_similarity


class VectorDB:
    """A minimal vector database: in-memory storage, JSON-file persistence, cosine-similarity search."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.records: dict[int, dict] = {}
        if self.path.exists():
            raw = json.loads(self.path.read_text())
            self.records = {int(id_): record for id_, record in raw.items()}

    def upsert(self, id: int, vector: list[float], payload: dict | None = None):
        self.records[id] = {"vector": vector, "payload": payload or {}}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.records))

    def search(self, query_vector: list[float], top_k: int = 5) -> list[tuple[dict, float]]:
        scored = [
            (record["payload"], cosine_similarity(query_vector, record["vector"]))
            for record in self.records.values()
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]
