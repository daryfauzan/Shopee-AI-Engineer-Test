import re


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def build_vocabulary(documents: list[str]) -> list[str]:
    vocabulary: dict[str, None] = {}
    for doc in documents:
        for token in tokenize(doc):
            vocabulary.setdefault(token, None)
    return list(vocabulary)


def vectorize(text: str, vocabulary: list[str]) -> list[float]:
    """Bag-of-words term-frequency vector, one dimension per vocabulary word."""
    counts = {}
    for token in tokenize(text):
        counts[token] = counts.get(token, 0) + 1
    return [float(counts.get(word, 0)) for word in vocabulary]
