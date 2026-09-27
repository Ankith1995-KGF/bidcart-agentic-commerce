import os
import json

from google import genai
from google.genai.errors import ServerError, ClientError


MODEL_NAME = "gemini-3.8-flash"


def find_product_candidates(user_query):
    """
    Use Gemini only to resolve the product the customer means.

    This happens BEFORE Bright Data is called.
    It does not recommend alternative products or retrieve prices.
    """

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    prompt = f"""
You are the Product Identity Resolver for BidCart.

The customer entered:
"{user_query}"

Your only task is to resolve product identity.

Rules:
1. Do NOT recommend alternative products.
2. Do NOT suggest competing brands.
3. Do NOT provide prices, retailers, reviews or buying advice.
4. Return only plausible product identities represented by the
   customer's wording.
5. If the wording clearly identifies one product, return one candidate.
6. If it is ambiguous, return the distinct products the customer
   could reasonably mean.
7. Keep the list concise. Do not invent unnecessary variants.
8. Do not treat accessories as the requested main product.

Return ONLY valid JSON in this format:

{{
  "candidates": [
    {{
      "canonical_name": "Exact product identity",
      "product_type": "Short product type"
    }}
  ]
}}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
    except (ServerError, ClientError):
        return []

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    result = json.loads(text)

    return result.get("candidates", [])