"""
Product Recommendation Scoring using Semantic Similarity and Heuristics

This module ranks products based on a combination of semantic similarity
and domain-specific heuristics. The system processes a user request and 
evaluates products using the following scoring components:

1. Semantic similarity: using SentenceTransformer to encode user queries and product titles.
2. Match Level score: based on predefined match levels provided by Claude.
3. Price score: Normalized price scores where lower prices yield higher scores.
4. Condition score: Based on predefined condition categories with associated scores.

The final recommendation score is a weighted aggregation of these components.
"""

from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Predefined score mappings for product condition
condition_scores = {
    "新品、未使用": 1.0,       # New, unused
    "未使用に近い": 0.9,       # Like new
    "目立った傷や汚れなし": 0.6,  # No noticeable scratches or stains (used but good)
    "やや傷や汚れあり": 0.5,    # Some scratches or stains
    "傷や汚れあり": 0.3,        # Noticeable damage
    "全体的に状態が悪い": 0.1,   # Bad condition overall
}

# Predefined score mappings for match quality provided by Claude
matching_scores = {
    "Excellent match": 1.0,
    "Good match": 0.8,
    "Partial match": 0.6,
    "Weak match": 0.3,
    "No match": 0.1
}

def normalize(x: np.ndarray) -> np.ndarray:
    """
    Normalize values using min-max normalization.
    This function scales the input array such that lower prices yield higher scores.
    """
    x = np.array(x)
    return (x.max() - x) / (x.max() - x.min() + 1e-8)


def complete_top_k_products(
    products: List[Dict[str, Any]],
    titles_en: List[str],
    match_reasons: List[str],
    final_scores: List[float],
    k: int = 3
) -> List[Dict[str, Any]]:
    
    """
    Selects top-k products based on final recommendation scores and 
    enriches the product information with score and reason metadata.
    """

    indexed = list(enumerate(zip(products, titles_en, match_reasons, final_scores)))
    top_k = sorted(indexed, key=lambda x: x[1][3], reverse=True)[:k]

    top_products = []
    for index, (product, title_en, reason, score) in top_k:
        complete_product = product.copy()
        complete_product["title_en"] = title_en
        complete_product["recommendation_reason"] = reason
        complete_product["recommendation_score"] = score
        top_products.append(complete_product)

    return top_products

def get_recommendation_scores(
    user_query: str,
    products_title_en: List[str],
    match_level: List[str],
    products: List[Dict[str, Any]]
) -> np.ndarray:
    """
    Computes a final recommendation score for each product by combining
    semantic similarity, rule-based keyword match, normalized price, and 
    product condition.
    """
    # Load the pre-trained SentenceTransformer model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Convert price strings to integers if necessary
    for p in products:
        if isinstance(p["price"], str):
            p["price"] = int(p["price"].replace(",", "").strip())

    # Encode the user query and product titles
    user_embedding = model.encode(user_query)
    product_embeddings = model.encode(products_title_en)

    # Compute cosine similarit and score components
    similarities = cosine_similarity([user_embedding], product_embeddings)[0]
    price_scores = normalize([p["price"] for p in products])
    cond_scores = np.array([condition_scores.get(p["condition"], 0.0) for p in products])
    match_scores = np.array([matching_scores.get(m, 0.0) for m in match_level])

    # Weighted aggregation of score components
    final_scores = (
        0.2 * similarities +
        0.4 * match_scores +
        0.3 * price_scores +
        0.1 * cond_scores
    )

    return final_scores