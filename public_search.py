import requests


def search_public_web(product):
    """
    Uses OpenFoodFacts public API for real product data.

    This is our first working public-data connector.
    Other retailer/category connectors will be added separately.
    """

    url = "https://world.openfoodfacts.org/cgi/search.pl"

    params = {
        "search_terms": product,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        results = []

        for item in data.get("products", []):
            name = item.get("product_name")

            if not name:
                continue

            results.append({
                "product_name": name,
                "brand": item.get("brands", "Unknown"),
                "quantity": item.get("quantity", "Unknown"),
                "barcode": item.get("code", ""),
                "source_type": "OPENFOODFACTS_PUBLIC_API"
            })

        return results

    except (requests.RequestException, ValueError):
        return []