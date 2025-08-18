from __future__ import annotations
import sqlite3, json, time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any, Dict

@dataclass
class QueueItem:
    id: int; user_id: str; payload: Dict[str, Any]; attempts: int; status: str

class UserQueue:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            con.execute("""CREATE TABLE IF NOT EXISTS queue(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id TEXT NOT NULL, payload TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'pending',
              attempts INTEGER NOT NULL DEFAULT 0,
              last_error TEXT, created_at REAL NOT NULL, updated_at REAL NOT NULL)""")
            con.commit()

    def _c(self): return sqlite3.connect(self.db_path)

    def enqueue(self, user_id: str, payload: Dict[str, Any]) -> int:
        ts = time.time()
        with self._c() as con:
            cur = con.execute(
                "INSERT INTO queue(user_id,payload,status,attempts,created_at,updated_at) VALUES(?,?,'pending',0,?,?)",
                (user_id, json.dumps(payload), ts, ts))
            con.commit(); return int(cur.lastrowid)

    def size(self, status: Optional[str] = None) -> int:
        with self._c() as con:
            sql = "SELECT COUNT(*) FROM queue" if not status else "SELECT COUNT(*) FROM queue WHERE status=?"
            row = con.execute(sql, (status,) if status else ()).fetchone()
        return int(row[0]) if row else 0

    def dequeue(self) -> Optional[QueueItem]:
        with self._c() as con:
            r = con.execute("SELECT id,user_id,payload,attempts,status FROM queue WHERE status='pending' ORDER BY id LIMIT 1").fetchone()
        return None if not r else QueueItem(id=r[0], user_id=r[1], payload=json.loads(r[2]), attempts=r[3], status=r[4])

    def mark_sent(self, item_id: int) -> None:
        with self._c() as con:
            con.execute("UPDATE queue SET status='sent', updated_at=? WHERE id=?", (time.time(), item_id)); con.commit()

    def mark_failed(self, item_id: int, error: str) -> None:
        with self._c() as con:
            con.execute("UPDATE queue SET status='failed', attempts=attempts+1, last_error=?, updated_at=? WHERE id=?",
                        (error, time.time(), item_id)); con.commit()
