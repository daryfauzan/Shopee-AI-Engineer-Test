from vector_db import VectorDB
from vectorize import build_vocabulary, vectorize

DOCUMENTS = [
    "the cat sat on the mat",
    "the dog played in the park",
    "cats and dogs are popular pets",
    "the stock market rose today",
    "investors watched the market closely",
]


def main():
    vocabulary = build_vocabulary(DOCUMENTS)

    db = VectorDB("data/vectors.json")
    for i, doc in enumerate(DOCUMENTS):
        db.upsert(i, vectorize(doc, vocabulary), payload={"text": doc})
    db.save()

    query = "the cat and the dog are pets"
    query_vector = vectorize(query, vocabulary)
    results = db.search(query_vector, top_k=len(DOCUMENTS))

    print(f"Query: {query!r}\n")
    for payload, score in results:
        print(f"  {score:.4f}  {payload['text']}")


if __name__ == "__main__":
    main()
