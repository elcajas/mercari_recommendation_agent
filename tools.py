extract_keywords_filters_tool = {
    "name": "extract_keywords_filters",
    "description": "Extract search keywords and filters for Mercari Japan.",
    "input_schema": {
        "type": "object",
        "properties": {
            "keywords_en": {
                "type": "array",
                "items": {"type": "string"}
            },
            "keywords_ja": {
                "type": "array",
                "items": {"type": "string"}
            },
            "filters": {
                "type": "object",
                "properties": {
                    "condition": {
                        "type": "string",
                        "enum": ["new", "used"]
                    },
                    "price_min": {"type": "number"},
                    "price_max": {"type": "number"},
                    "brand": {"type": "string"},
                    "category": {"type": "string"}
                },
                "additionalProperties": False
            }
        },
        "required": ["keywords_en", "keywords_ja"]
    }
}

recommendation_tool = {
    "name": "recommendation_tool",
    "description": "Select the top 3 recommended products based on match level and reasons.",
    "input_schema": {
        "type": "object",
        "properties": {
            "titles_en": {
                "type": "array",
                "items": {"type": "string"}
            },
            "match_levels": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["Excellent match", "Good match", "Partial match", "Weak match", "No match"]
                }
            },
            "match_reasons": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["titles_en", "match_levels", "match_reasons"]
    }
}

tools = [extract_keywords_filters_tool, recommendation_tool]