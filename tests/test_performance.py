"""
Performance & Benchmark Tests for JARVIS Engine Optimization.
"""
import unittest
import time
from core import JARVISCore
from engines.shared.cache import TTLCache

class TestPerformanceOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = JARVISCore()

    def test_lru_intent_cache_speed(self):
        # First query (populates cache)
        t0 = time.perf_counter()
        res1 = self.core.process_request("system status")
        t1 = time.perf_counter()

        # Second identical query (uses LRU fast-path cache)
        t2 = time.perf_counter()
        res2 = self.core.process_request("system status")
        t3 = time.perf_counter()

        cached_duration = t3 - t2
        self.assertLess(cached_duration, 0.05, f"Cached intent resolution should take <50ms (actual: {cached_duration*1000:.2f}ms)")
        self.assertEqual(res1, res2)

    def test_ttl_cache_memoization(self):
        cache = TTLCache()
        counter = {"count": 0}

        def expensive_call():
            counter["count"] += 1
            return "data"

        # First call executes function
        r1 = cache.memoize("key1", 2.0, expensive_call)
        self.assertEqual(counter["count"], 1)

        # Second call within TTL returns cached result without incrementing counter
        r2 = cache.memoize("key1", 2.0, expensive_call)
        self.assertEqual(counter["count"], 1)
        self.assertEqual(r1, r2)

if __name__ == "__main__":
    unittest.main()
