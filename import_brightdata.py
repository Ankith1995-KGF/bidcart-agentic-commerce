import csv

from connectors import (
    is_matching_product,
    normalize_product_key,
    save_commerce_observation,
)

PRODUCT = "Sony WH-1000XM5"
CSV_FILE = "sd_muiq0ajrffmym646t.csv"

saved = 0

with open(CSV_FILE, encoding="utf-8-sig", newline="") as file:
    for row in csv.DictReader(file):
        title = row.get("title", "")

        if not is_matching_product(PRODUCT, title):
            continue

        price_text = (
            row.get("price", "")
            .replace("₹", "")
            .replace(",", "")
            .strip()
        )

        if not price_text:
            continue

        try:
            price = float(price_text)
        except ValueError:
            continue

        save_commerce_observation(
            product_key=normalize_product_key(PRODUCT),
            product_name=title,
            retailer=row.get("store_name")
            or row.get("seller_name")
            or "Unknown",
            price=price,
            rating=float(row["rating"])
            if row.get("rating")
            else None,
            review_count=int(row["reviews_count"])
            if row.get("reviews_count")
            else None,
            availability=row.get("availability"),
            product_url=row.get("url"),
        )

        saved += 1

print(f"Saved {saved} real commerce observations.")