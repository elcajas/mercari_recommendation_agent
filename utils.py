import urllib

def build_mercari_url(keywords, filters=None):
    """
    Build a Mercari search URL based on provided keywords and filters.
    """

    # Prepare keywords for the Mercari search URL
    keyword_query = urllib.parse.quote(" ".join(keywords))
    url = f"https://jp.mercari.com/search?keyword={keyword_query}&status=on_sale&item_types=mercari"

    # Add filters if provided
    if filters:
        if filters.get("price_min") is not None:
            url += f"&price_min={int(filters['price_min'])}"
        if filters.get("price_max") is not None:
            url += f"&price_max={int(filters['price_max'])}"

    return url