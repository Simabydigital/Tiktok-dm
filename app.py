cat > app.py <<'PY'
from __future__ import annotations
import argparse
from pathlib import Path
from typing import Optional

from core.config import Settings
from core.logger import setup_logger
from dm_queue.user_queue import UserQueue
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
        if not row.get("user_id"):
            continue
        q.enqueue(row["user_id"], {"source": "csv", "comment_text": row.get("comment_text", "")})
        count += 1
    logger.info(f"Enqueued {count} users from {csv_path}")


def cmd_queue(args, settings, logger):
    q = UserQueue(Path(settings.DATABASE_PATH))
    if args.size:
        print(q.size())


def cmd_send(args, settings, logger):
    from time import sleep
    import random

    q = UserQueue(Path(settings.DATABASE_PATH))
    dm = TikTokDM()

    limit = args.limit or 10
    max_attempts = 3
    sent = 0

    while sent < limit:
        item = q.dequeue()
        if not item:
            logger.info("Queue empty.")
            break

        attempts = 0
        while attempts < max_attempts:
            try:
                ok = dm.send_message(item.user_id, args.message or settings.DEFAULT_MESSAGE)
                if ok:
                    q.mark_sent(item.id)
                    sent += 1
                    break
                raise RuntimeError("Permanent failure reported by sender")
            except Exception as e:
                attempts += 1
                if attempts >= max_attempts:
                    q.mark_failed(item.id, f"{type(e).__name__}: {e}")
                    logger.warning(f"Giving up after {attempts} attempts on {item.user_id}")
                    break
                backoff = min(2 ** attempts, 60) + random.uniform(0, 0.25)
                logger.info(f"Retrying {item.user_id} in {backoff:.1f}s (attempt {attempts}/{max_attempts-1})")
                sleep(backoff)

    logger.info(f"Sent {sent} messages (simulated).")


def cmd_assist(args, settings, logger):
    import webbrowser
    q = UserQueue(Path(settings.DATABASE_PATH))
    msg = args.message or settings.DEFAULT_MESSAGE
    limit = getattr(args, "limit", 50)

    handled = 0
    while handled < limit:
        item = q.dequeue()
        if not item:
            logger.info("No more pending.")
            break
        url = f"https://www.tiktok.com/@{item.user_id.lstrip('@')}"
        print("\nOpen:", url)
        print("Paste this message:\n", msg)
        try:
            webbrowser.open_new_tab(url)
        except Exception:
            pass
        choice = input("Type 's' sent, 'f' failed, 'q' quit: ").strip().lower()
        if choice == "s":
            q.mark_sent(item.id)
        elif choice == "f":
            q.mark_failed(item.id, "manual_failed")
        elif choice == "q":
            break
        handled += 1
    logger.info(f"Handled {handled} users.")


def main(argv: Optional[list[str]] = None) -> int:
    settings = Settings()
    logger = setup_logger(settings.LOG_LEVEL)

    p = argparse.ArgumentParser(
        prog="social_dm",
        description="Social DM scaffold (compliant, placeholders only).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # collect
    p_collect = sub.add_parser("collect", help="Enqueue users from CSV.")
    p_collect.add_argument("--csv", type=str, default="data/sample_users.csv", help="Path to CSV.")
    p_collect.add_argument("--sample", action="store_true", help="Write a sample CSV before collecting.")
    p_collect.set_defaults(func=lambda a: cmd_collect(a, settings, logger))

    # queue
    p_queue = sub.add_parser("queue", help="Queue utilities.")
    p_queue.add_argument("--size", action="store_true", help="Print queue size.")
    p_queue.set_defaults(func=lambda a: cmd_queue(a, settings, logger))

    # send (simulated)
    p_send = sub.add_parser("send", help="Simulate sending messages.")
    p_send.add_argument("--limit", type=int, default=5, help="Max items to send.")
    p_send.add_argument("--message", type=str, help="Message text (optional).")
    p_send.set_defaults(func=lambda a: cmd_send(a, settings, logger))

    # assist (manual)
    p_assist = sub.add_parser("assist", help="Open each profile; you DM manually; mark result.")
    p_assist.add_argument("--limit", type=int, default=50)
    p_assist.add_argument("--message", type=str)
    p_assist.set_defaults(func=lambda a: cmd_assist(a, settings, logger))

    args = p.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
