import csv
import os
from datetime import datetime

DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "usage_logs.csv")

# Use title-case headers to stay compatible with existing CSVs
HEADERS = [
    "Date and Time",
    "User Query",
    "Product",
    "IP Address",
    "feedback",
    "response_id",
    "confidence_score"
]


def ensure_schema():
    """Ensure CSV exists and has the expected headers/columns.
    If an older CSV is present (e.g., without feedback/response_id or with emoji header),
    rewrite it to the new schema while preserving data.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
        return

    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Detect if schema already matches
    if reader.fieldnames and set(reader.fieldnames) == set(HEADERS):
        return

    # Rebuild rows into the new schema
    normalized = []
    for row in rows:
        normalized.append([
            row.get("Date and Time") or row.get("Date") or row.get("datetime") or "",
            row.get("User Query") or row.get("question") or "",
            row.get("Product") or row.get("product") or "Unknown",
            row.get("IP Address") or row.get("ip") or row.get("ip_address") or "",
            row.get("feedback") or row.get("👍👎") or "",
            row.get("response_id") or "",
            row.get("confidence_score") or ""
        ])

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(normalized)


def log_usage(question: str, product: str, ip: str, confidence_score: float = 0.0):
    ensure_schema()

    # Generate unique response ID
    response_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{os.urandom(3).hex()}"

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            question,
            product,
            ip,
            "",  # feedback (empty initially)
            response_id,
            confidence_score
        ])

    return response_id


def log_feedback(response_id: str, feedback: str):
    """Update feedback for a specific response_id"""
    if not os.path.exists(CSV_FILE):
        return

    ensure_schema()

    rows = []
    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Update matching row
    updated = False
    for row in rows:
        if row.get("response_id") == response_id:
            row["feedback"] = feedback
            updated = True
            break

    if not updated:
        return

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)
