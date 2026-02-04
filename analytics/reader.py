import csv
import os
from collections import Counter

CSV_FILE = "data/usage_logs.csv"


def normalize_product(product: str) -> str:
    
    if not product:
        return "Unknown"
    product_lower = product.lower()
    if "hyworks" in product_lower:
        return "HyWorks"
    elif "hysecure" in product_lower:
        return "HySecure"
    return product


def usage_summary():
    if not os.path.exists(CSV_FILE):
        return {
            "total_queries": 0,
            "by_product": {"HyWorks": 0, "HySecure": 0}
        }

    total = 0
    products = Counter()

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            total += 1
            # support multiple possible header names for product
            product = row.get("product") or row.get("Product") or row.get("product_name") or "Unknown"
            product = normalize_product(product)
            products[product] += 1

    return {
        "total_queries": total,
        "by_product": {
            "HyWorks": products.get("HyWorks", 0),
            "HySecure": products.get("HySecure", 0)
        }
    }


def top_questions(limit=5):

    if not os.path.exists(CSV_FILE):
        return []

    q_counter = Counter()
    q_products = {}

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # support multiple header names for question column
            q = (row.get("question") or row.get("User Query") or row.get("User query") or row.get("UserQuery") or row.get("User_Query"))
            if not q:
                continue

            product = row.get("product") or row.get("Product") or "Unknown"

            q_counter[q] += 1
            q_products.setdefault(q, Counter())[product] += 1

    most_common = q_counter.most_common(limit)

    results = []
    for q, cnt in most_common:
        prod_counts = q_products.get(q, {})
        # pick the most common product for this question (or Unknown)
        product = prod_counts.most_common(1)[0][0] if prod_counts else "Unknown"
        results.append({"question": q, "product": product, "count": cnt})

    return results


def recent_logs(limit=10):

    if not os.path.exists(CSV_FILE):
        return []

    rows = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = (row.get("Date and Time") or row.get("date and time") or row.get("Date") or row.get("datetime") or row.get("DateTime") or "")
            q = (row.get("User Query") or row.get("User query") or row.get("question") or row.get("UserQuery") or "")
            product = row.get("Product") or row.get("product") or "Unknown"
            product = normalize_product(product)
            ip = (row.get("IP Address") or row.get("ip") or row.get("IP") or row.get("ip_address") or "")
            feedback = row.get("feedback") or row.get("Feedback") or row.get("👍👎") or ""
            confidence_score_str = row.get("confidence_score") or row.get("Confidence Score") or ""
            confidence_score = float(confidence_score_str) if confidence_score_str else 0.0
            rows.append({"datetime": dt, "question": q, "product": product, "ip": ip, "feedback": feedback, "confidence_score": confidence_score})

    # Return the latest `limit` rows, preserving order newest->oldest
    latest = rows[-limit:][::-1] if limit and len(rows) > limit else rows[::-1]
    return latest
