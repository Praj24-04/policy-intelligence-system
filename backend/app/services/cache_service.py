import time
from threading import Lock

class SimpleInMemoryCache:
    def __init__(self, default_ttl=1800):
        self.store = {}
        self.default_ttl = default_ttl
        self.lock = Lock()

    def get(self, key):
        with self.lock:
            entry = self.store.get(key)
            if entry:
                val, expiry = entry
                if time.time() < expiry:
                    return val
                else:
                    del self.store[key]
            return None

    def set(self, key, value, ttl=None):
        ttl = ttl if ttl is not None else self.default_ttl
        with self.lock:
            self.store[key] = (value, time.time() + ttl)

    def clear(self):
        with self.lock:
            self.store.clear()

# Global backend cache instance (30-minute TTL by default)
backend_cache = SimpleInMemoryCache(default_ttl=1800)
