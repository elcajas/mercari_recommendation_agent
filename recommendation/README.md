# Recommendation Module

This module is responsible for evaluating and scoring product listings retrieved from Mercari Japan using web scraping. It operates on structured inputs produced by other components of the system, namely, the user request, English-translated product titles, and semantic match levels provided by Claude.

Its role is to score and rank product candidates based on a combination of semantic similarity, product condition, and price normalization, and select the top 3 recommended products.

## Overview

The module performs two main operations:

1. **Product Scoring**: Scores the relevance and quality of each product based on several weighted criteria.
2. **Recommendation Selection**: Ranks the products and returns the top 3 with additional metadata for recommendation.

## Process Details

### 1. Product Scoring

Each product is scored on a normalized scale (0.0 to 1.0) based on four weighted components:

* **Semantic Similarity**: Computed using SentenceTransformer (`all-MiniLM-L6-v2`) embeddings and **cosine similarity** between the user query and English-translated product titles.
* **Match Level Score**: Based on categorical labels from Claude, each mapped to a predefined numerical value:

  ```python
  {
    "Excellent match": 1.0,
    "Good match": 0.8,
    "Partial match": 0.6,
    "Weak match": 0.3,
    "No match": 0.1,
  }
  ```

* **Condition Score**: Assigned according to a fixed mapping:

  ```python
  {
    "新品、未使用": 1.0,
    "未使用に近い": 0.9,
    "目立った傷や汚れなし": 0.6,
    "やや傷や汚れあり": 0.5,
    "傷や汚れあり": 0.3,
    "全体的に状態が悪い": 0.1,
  }
  ```
* **Price Score**: Derived through min-max normalization, assigning higher scores to lower prices.

The final recommendation score is computed as:

```python
final_score = 0.2 * semantic_similarity + 0.4 * match_level_score + 0.3 * price_score + 0.1 * condition_score
```

### 2. Recommendation Output

The `complete_top_k_products` function selects the top 3 products by score and augments them with additional metadata:

* Original title (Japanese)
* Translated title (English)
* Price
* Product condition
* Product URL
* Claude-generated match reason
* Final recommendation score
