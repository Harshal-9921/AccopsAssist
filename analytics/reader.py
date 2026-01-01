import csv
import os
from collections import Counter

CSV_FILE = "data/usage_logs.csv"


def usage_summary():
    if not os.path.exists(CSV_FILE):
        return {
            "total": 0,
            "hyworks": 0,
            "hysecure": 0
        }

    total = 0
    products = Counter()

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)   # ✅ IMPORTANT

        for row in reader:
            total += 1
            product = row.get("product", "Unknown")
            products[product] += 1

    return {
        "total": total,
        "hyworks": products.get("HyWorks", 0),
        "hysecure": products.get("HySecure", 0)
    }


def top_questions(limit=5):
    if not os.path.exists(CSV_FILE):
        return []

    counter = Counter()

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            q = row.get("question")
            if q:
                counter[q] += 1

    return counter.most_common(limit)
