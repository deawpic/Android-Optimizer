# -*- coding: utf-8 -*-
"""
Cache Latency, Hit Ratio & Token Savings Performance Benchmark
Abides strictly by the Speed Test Probe Guard (<= 3 live external requests).
"""

import logging
from pathlib import Path
import sys
import time

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from harness.cache import DualLayerCache

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("PerformanceBenchmark")


def main():
    print("=" * 60)
    print("⚡ TIER-0 DUAL-LAYER CACHE PERFORMANCE BENCHMARK")
    print("=" * 60)

    cache = DualLayerCache()

    # Synthetic probe payloads (Cap <= 3 live probes)
    probes = [
        ("adb", "getprop", {"prop": "ro.product.manufacturer"}, {"manufacturer": "Samsung", "brand": "samsung"}),
        ("adb", "dumpsys", {"service": "battery"}, {"level": 85, "temperature_raw": 340, "is_charging": False}),
        ("adb", "pm", {"cmd": "list_packages", "user": 0}, {"packages": ["com.samsung.android.bixby.agent", "com.android.systemui"]})
    ]

    # Clear previous bench tag to ensure true cold miss and write measurement
    with cache._get_connection() as conn:
        conn.execute("DELETE FROM mcp_cache WHERE tag = 'bench'")
        conn.commit()
    with cache._l1_lock:
        cache._l1.clear()

    print(f"Executing {len(probes)} benchmark probes (Strict Probe Guard: <= 3 requests)...")

    # 1. First Pass: Cache Miss & Write to L1/L2
    miss_latencies = []
    for provider, cmd, args, payload in probes:
        key = cache.generate_cache_key(provider, cmd, args)
        t0 = time.perf_counter()
        # Simulate retrieval / miss
        val = cache.get(key)
        if val is None:
            cache.set(key, payload, tag="bench", query_raw=f"{provider}:{cmd}")
        t1 = time.perf_counter()
        miss_latencies.append((t1 - t0) * 1000)

    # 2. Second Pass: L1 In-Memory Retrieval (<0.2ms target)
    l1_latencies = []
    for provider, cmd, args, _ in probes:
        key = cache.generate_cache_key(provider, cmd, args)
        t0 = time.perf_counter()
        val = cache.get(key)
        t1 = time.perf_counter()
        l1_latencies.append((t1 - t0) * 1000)

    # 3. Third Pass: Clear L1 to test L2 Compressed Disk Read (<2.0ms target)
    with cache._l1_lock:
        cache._l1.clear()

    l2_latencies = []
    for provider, cmd, args, _ in probes:
        key = cache.generate_cache_key(provider, cmd, args)
        t0 = time.perf_counter()
        val = cache.get(key)
        t1 = time.perf_counter()
        l2_latencies.append((t1 - t0) * 1000)

    stats = cache.get_stats()

    avg_miss = sum(miss_latencies) / len(miss_latencies)
    avg_l1 = sum(l1_latencies) / len(l1_latencies)
    avg_l2 = sum(l2_latencies) / len(l2_latencies)

    print("\n📊 BENCHMARK METRICS:")
    print(f"L1 In-Memory Avg Latency : {avg_l1:.3f} ms (Target: <0.200 ms)")
    print(f"L2 SQLite WAL Avg Latency: {avg_l2:.3f} ms (Target: <2.000 ms)")
    print(f"Cold Cache Miss Latency  : {avg_miss:.3f} ms")
    print(f"Cache Hit Ratio          : {stats['hit_ratio'] * 100:.1f}%")
    print(f"Total Cached Writes      : {stats['writes']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
