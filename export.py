import argparse, sqlite3, json, csv
from pathlib import Path
from core.config import Settings

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/todo.csv")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--message", default=None)
    args = ap.parse_args()

    s = Settings()
    msg = args.message or s.DEFAULT_MESSAGE
    db = Path(s.DATABASE_PATH)
    out = Path(args.csv); out.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(db)
    rows = con.execute(
        "SELECT user_id, payload FROM queue WHERE status='pending' ORDER BY id LIMIT ?",
        (args.limit,),
    ).fetchall()

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["user_id","profile_url","message","comment_text"])
        w.writeheader()
        for user_id, payload in rows:
            try: payload = json.loads(payload)
            except Exception: payload = {}
            w.writerow({
                "user_id": user_id,
                "profile_url": f"https://www.tiktok.com/@{user_id.lstrip('@')}",
                "message": msg,
                "comment_text": payload.get("comment_text",""),
            })
    print(f"Exported {len(rows)} to {out}")

if __name__ == "__main__":
    main()
