import csv
import os
from datetime import datetime

DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "usage_logs.csv")

HEADERS = [
    "Date and Time",
    "User Query",
    "product",
    "ip_address"
]

def log_usage(question: str, product: str, ip: str):
    os.makedirs(DATA_DIR, exist_ok=True)

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(HEADERS)

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            question,
            product,
            ip
        ])
