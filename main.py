"""
Mercari Product Recommendation Agent

This program processes a user's natural language shopping request, extracts search parameters
(keywords and filters), retrieves relevant product listings from Mercari Japan, evaluates
them for match quality, scores them, and returns a user-friendly recommendation message with
top 3 products.

The agent leverages the Claude 3.5 Sonnet language model with tool-calling support, and Selenium and BeautifulSoup
for dynamic web scraping. The full recommendation pipeline is composed of the following steps:

1. Keyword and Filter Extraction: Uses Claude's tool to extract keywords and filters from the user's request.
2. Web Scraping: Constructs a Mercari search URL and scrapes product listings using Selenium.
3. Product Evaluation: Translates product titles, evaluates match quality against the user's request, and prepares recommendations.
4. Scoring and Ranking: Scores products based on relevance, price, condition, and match level, then ranks them.
5. Final Recommendation: Generates a friendly message with the top 3 recommended products.
"""

import json
import argparse
import anthropic
from dotenv import load_dotenv

from tools import tools, extract_keywords_filters_tool, recommendation_tool
from utils import build_mercari_url
from web_scrapping import get_items, list_details
from recommendation import get_recommendation_scores, complete_top_k_products

# Set up command-line argument parser
parser = argparse.ArgumentParser(description="Mercari Product Recommendation Agent")
parser.add_argument("--request", type=str, required=True, help="User's shopping request in natural language")
args = parser.parse_args()


# Load API key from .env file and initialize Claude client
load_dotenv()
client = anthropic.Anthropic()

# Define the user request and Claude model configuration
# USER_REQUEST = "I'm looking for wireless Sony headphones in black color, preferably new, and under 8000 yen."
USER_REQUEST = args.request  # Use the request from command line argument
MODEL = "claude-3-5-sonnet-latest"
MAX_TOKENS = 1024

#################### STEP 1 ########################
# Extract keywords and filters from the user request using Claude tool

extract_keywords_prompt = f"""
Please extract search information for a Mercari Japan query from the following user request:

"{USER_REQUEST.strip()}"

Your output must include:
- 'keywords_en': English keywords only (e.g. item, brand, color, size)
- 'keywords_ja': Japanese keywords only (translated from the English terms, including colors and units)
- 'filters': A dictionary with any available filters like 'condition', 'price_min', 'price_max', 'brand', and 'category'
Only return a tool call output.
"""

response_1 = client.messages.create(
    model=MODEL,
    max_tokens=MAX_TOKENS,
    tools=[extract_keywords_filters_tool],
    messages=[{"role": "user", "content": extract_keywords_prompt}]
)

# Extract structured keyword and filter info from Claude's tool response
tool_call_1 = response_1.content[0]
tool_args_1 = tool_call_1.input

# Build the Mercari URL using extracted Japanese keywords and filters
keywords_ja = tool_args_1["keywords_ja"]
filters = tool_args_1["filters"]
url = build_mercari_url(keywords_ja, filters)

#################### STEP 2 ########################
# Scrape Mercari results using the constructed URL

product_urls = get_items(url)
products = list_details(product_urls[:20])
product_titles_ja = [p["title"] for p in products]

#################### STEP 3 ########################
# Evaluate how well the products match the user request

match_and_recommend_prompt = f"""
You are helping a user find products on Mercari Japan.

User request:
"{USER_REQUEST.strip()}"

Here is a list of product titles in Japanese:
{product_titles_ja}

Please:
1. Translate each title to English.
2. Evaluate how well it matches the user's request.
   Use one of the following match levels:
   - Excellent match
   - Good match
   - Partial match
   - Weak match
   - No match
3. Give a short reason for each match level.

Finally, use the `recommendation_tool` with the following structure:
- titles_en: English titles in the same order
- match_levels: List of match levels
- match_reasons: List of match reasons
Only return a tool call output.
"""

response_2 = client.messages.create(
    model=MODEL,
    max_tokens=MAX_TOKENS,
    tools=[recommendation_tool],
    messages=[
        {"role": "user", "content": match_and_recommend_prompt}
    ]
)

# Extract the tool call output containing product recommendations
tool_call_2 = response_2.content[1]
products_title_en = tool_call_2.input["titles_en"]
match_levels = tool_call_2.input["match_levels"]
match_reasons = tool_call_2.input["match_reasons"]

###################### STEP 4 ########################
# Score the products and get the top 3 recommendations

recommendation_scores = get_recommendation_scores(USER_REQUEST, products_title_en, match_levels, products)
final_top_3 = complete_top_k_products(products, products_title_en, match_reasons, recommendation_scores)

##################### STEP 5 ########################
# Generate a user-friendly recommendation message

content = f"""
Please write a clear, friendly product recommendation message in English based on the following 3 Mercari Japan products. Each product is a good match for the user's shopping request.
User request:
"{USER_REQUEST.strip()}"

Here are the products (in JSON format):
{json.dumps(final_top_3, ensure_ascii=False, indent=2)}

For each product, include:
- The English title
- Price in yen
- Condition
- The recommendation reason
- A clickable product URL

Format the response as a numbered list or bullet points for clarity.
Make the tone friendly and helpful for someone shopping online.
"""

final_response = client.messages.create(
    model=MODEL,
    max_tokens=MAX_TOKENS,
    temperature=0,
    messages=[
        {"role": "user", "content": content}
    ]
)

# Print the final generated recommendation message
print(final_response.content[0].text)