from __future__ import annotations
import argparse
from pathlib import Path
from typing import Optional

from core.config import Settings
from core.logger import setup_logger
from queue.user_queue import UserQueue
from collectors.tiktok_comments import read_users_from_csv, write_sample_csv
from messaging.tiktok_dm import TikTokDM

def cmd_collect(args, settings, logger):
    csv_path = Path(args.csv)
    if args.sample:
        write_sample_csv(csv_path)
        logger.info(f"Sample CSV created at {csv_path.resolve()}")
    q = UserQueue(Path(settings.DATABASE_PATH))
    count = 0
    for row in read_users_from_csv(csv_path):
        if not row["user_id"]:
            continue
        q.enqueue(row["user_id"], {"source": "csv", "comment_text": row.get("comment_text", "")})
        count += 1
    logger.info(f"Enqueued {count} users from {csv_path}")

def cmd_queue(args, settings, logger):
    q = UserQueue(Path(settings.DATABASE_PATH))
    if args.size:
        print(q.size())

def cmd_send(args, settings, logger):
    q = UserQueue(Path(settings.DATABASE_PATH))
    dm = TikTokDM()
    limit = args.limit or 10
    sent = 0
    while sent < limit:
        item = q.dequeue()
        if not item:
            logger.info("Queue empty.")
            break
        try:
            ok = dm.send_message(item.user_id, args.message or settings.DEFAULT_MESSAGE)
            if ok:
                q.mark_sent(item.id)
                sent += 1
            else:
                q.mark_failed(item.id, "Permanent failure")
        except Exception as e:
            q.mark_failed(item.id, f"Retryable error: {e}")
    logger.info(f"Sent {sent} messages (simulated).")

def main(argv: Optional[list[str]] = None) -> int:
    settings = Settings()
    logger = setup_logger(settings.LOG_LEVEL)

    p = argparse.ArgumentParser(prog="social_dm", description="Social DM scaffold (compliant, placeholders only).")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_collect = sub.add_parser("collect", help="Enqueue users from CSV.")
    p_collect.add_argument("--csv", type=str, default="data/sample_users.csv", help="Path to CSV.")
    p_collect.add_argument("--sample", action="store_true", help="Write a sample CSV before collecting.")
    p_collect.set_defaults(func=lambda a: cmd_collect(a, settings, logger))

    p_queue = sub.add_parser("queue", help="Queue utilities.")
    p_queue.add_argument("--size", action="store_true", help="Print queue size.")
    p_queue.set_defaults(func=lambda a: cmd_queue(a, settings, logger))

    p_send = sub.add_parser("send", help="Simulate sending messages.")
    p_send.add_argument("--limit", type=int, default=5, help="Max items to send.")
    p_send.add_argument("--message", type=str, help="Message text (optional).")
    p_send.set_defaults(func=lambda a: cmd_send(a, settings, logger))

    args = p.parse_args(argv)
    args.func(args)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
