import logging
from typing import Any

logger = logging.getLogger("redrob")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def info(msg: str, *args: Any, **kwargs: Any) -> None:
    logger.info(msg.format(*args, **kwargs))

def debug(msg: str, *args: Any, **kwargs: Any) -> None:
    logger.debug(msg.format(*args, **kwargs))

def warning(msg: str, *args: Any, **kwargs: Any) -> None:
    logger.warning(msg.format(*args, **kwargs))
