import logging, sys

def setup_logger(level: str = "INFO") -> logging.Logger:
    log = logging.getLogger("social_dm")
    if log.handlers:
        return log
    log.setLevel(getattr(logging, level.upper(), logging.INFO))
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s", "%H:%M:%S"))
    log.addHandler(h)
    return log
