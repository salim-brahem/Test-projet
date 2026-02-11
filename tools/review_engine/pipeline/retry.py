import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")

def retry(fn: Callable[[], T], *, tries: int = 3, base_delay_s: float = 0.8, max_delay_s: float = 6.0,
          jitter: float = 0.25, logger=None) -> T:
    last = None
    for attempt in range(1, tries + 1):
        try:
            return fn()
        except Exception as e:
            last = e
            if logger:
                logger.info(f"retry attempt={attempt}/{tries} err={e}")
            if attempt == tries:
                break
            delay = min(max_delay_s, base_delay_s * (2 ** (attempt - 1)))
            delay *= (1.0 + random.uniform(-jitter, jitter))
            time.sleep(max(0.0, delay))
    raise last
