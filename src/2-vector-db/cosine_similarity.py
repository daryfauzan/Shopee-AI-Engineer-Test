import math


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """cos(theta) = (a . b) / (||a|| * ||b||), computed with plain loops/math only."""
    if len(a) != len(b):
        raise ValueError("vectors must have the same dimension")

    dot_product = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for x, y in zip(a, b):
        dot_product += x * y
        norm_a += x * x
        norm_b += y * y

    norm_a = math.sqrt(norm_a)
    norm_b = math.sqrt(norm_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


if __name__ == "__main__":
    identical = cosine_similarity([1, 2, 3], [1, 2, 3])
    orthogonal = cosine_similarity([1, 0], [0, 1])
    opposite = cosine_similarity([1, 2], [-1, -2])

    print(f"identical vectors  -> {identical:.4f} (expected 1.0)")
    print(f"orthogonal vectors -> {orthogonal:.4f} (expected 0.0)")
    print(f"opposite vectors   -> {opposite:.4f} (expected -1.0)")
