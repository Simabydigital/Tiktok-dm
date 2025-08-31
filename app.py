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
                ok = dm.send_message(item.user_id, args.me
