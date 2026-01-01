import csv
import os
from datetime import datetime

LOG_FILE = "data/usage_logs.csv"

HEADERS = [
    "timestamp",
    "ip_address",
    "question",
    "product",
    "source"
]


def log_usage(ip_address, question, product, source):
    os.makedirs("data", exist_ok=True)

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(HEADERS)

        writer.writerow([
            datetime.utcnow().isoformat(),
            ip_address,
            question,
            product,
            source
        ])
