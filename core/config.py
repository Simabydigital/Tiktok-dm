from __future__ import annotations
import os
from pathlib import Path
from typing import Dict

def _parse_env_file(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists(): return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if not line or line.startswith("#"): continue
        if "=" in line:
            k,v=line.split("=",1)
            values[k.strip()]=v.strip().strip('"').strip("'")
    return values

class Settings:
    def __init__(self, env_path: Path | None = None) -> None:
        base = Path.cwd()
        self.env_path = env_path or base/".env"
        env = {**_parse_env_file(self.env_path), **os.environ}
        self.DATABASE_PATH = env.get("DATABASE_PATH", str(base/"data"/"social_dm.sqlite"))
        self.LOG_LEVEL = env.get("LOG_LEVEL", "INFO")
        self.DEFAULT_MESSAGE = env.get("DEFAULT_MESSAGE", "Hello from social_dm!")
