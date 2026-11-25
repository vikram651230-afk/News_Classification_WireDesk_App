import csv
from datetime import datetime
from pathlib import Path

# Absolute path, so feeds are found no matter where the server is started from.
FEED_DIR = Path(__file__).resolve().parents[2] / "data" / "feeds"


def route_article(text, category):

    FEED_DIR.mkdir(parents=True, exist_ok=True)

    path = FEED_DIR / f"{category}.csv"

    new_file = not path.exists()

    with open(path, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        if new_file:
            writer.writerow(["timestamp", "category", "text"])

        writer.writerow([datetime.now().isoformat(), category, text])


def read_feed(category, limit=20):
    """Newest-first rows from one category feed."""

    path = FEED_DIR / f"{category}.csv"

    if not path.exists():
        return []

    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    return rows[::-1][:limit]


def feed_counts():
    """{category: number of routed articles} for every feed file."""

    counts = {}

    if not FEED_DIR.exists():
        return counts

    for path in FEED_DIR.glob("*.csv"):
        with open(path, newline="", encoding="utf-8") as f:
            counts[path.stem] = max(sum(1 for _ in f) - 1, 0)

    return counts
