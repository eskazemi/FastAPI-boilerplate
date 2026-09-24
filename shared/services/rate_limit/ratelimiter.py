from shared.services.rate_limit.token_bucket import TokenBucket
import threading

class RateLimiterStore:
    """
    Manages per-user Token Buckets.

    Each unique client key (e.g., IP address) gets its own bucket
    with identical parameters.
    """

    def __init__(self, max_tokens: int, refill_rate: int, interval: float):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.interval = interval
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def get_bucket(self, key: str) -> TokenBucket:
        """
        Return the TokenBucket for a given client key.
        Creates a new bucket if one does not exist yet.
        """
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = TokenBucket(
                    max_tokens=self.max_tokens,
                    refill_rate=self.refill_rate,
                    interval=self.interval,
                )
            return self._buckets[key]