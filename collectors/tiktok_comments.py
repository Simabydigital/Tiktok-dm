from __future__ import annotations
from pathlib import Path
import csv
from typing import Iterable, Dict, Any

def read_users_from_csv(csv_path: Path) -> Iterable[Dict[str, Any]]:
    csv_path = Path(csv_path)
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            yield {"user_id": row.get("user_id","").strip(),
                   "comment_text": row.get("comment_text","").strip()}

def write_sample_csv(csv_path: Path) -> None:
    csv_path = Path(csv_path); csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["user_id","comment_text"])
        w.writerow(["u123","Loved your video!"])
        w.writerow(["u456","Interested in your product."])
        w.writerow(["u789","How can I contact you?"])
