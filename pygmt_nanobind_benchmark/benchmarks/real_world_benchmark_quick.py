#!/usr/bin/env python3
"""
Quick test of real-world benchmarks with reduced scale.
"""

import sys
from pathlib import Path

# Add pygmt_nb to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "python"))

# Import the full benchmark module
import real_world_benchmark as rwb

# Set random seed
import numpy as np
np.random.seed(42)

print("=" * 70)
print("REAL-WORLD WORKFLOW BENCHMARKS (Quick Test)")
print("Reduced scale for fast validation")
print("=" * 70)

results = []

# Quick tests with reduced parameters
print("\nRunning quick tests (reduced scale)...")

# Scenario 1: Animation (10 frames instead of 100)
print("\n[1/3] Animation test...")
speedup1 = rwb.benchmark_animation(num_frames=10)
results.append(("Animation (10 frames)", speedup1))

# Scenario 2: Batch Processing (5 datasets instead of 10)
print("\n[2/3] Batch processing test...")
speedup2 = rwb.benchmark_batch_processing(num_datasets=5)
results.append(("Batch Processing (5 datasets)", speedup2))

# Scenario 3: Parallel Processing (2 workers × 5 tasks instead of 4×10)
print("\n[3/3] Parallel processing test...")
speedup3 = rwb.benchmark_parallel_processing(num_workers=2, tasks_per_worker=5)
results.append(("Parallel Processing (2×5)", speedup3))

# Summary
print("\n" + "=" * 70)
print("QUICK TEST SUMMARY")
print("=" * 70)

for scenario, speedup in results:
    print(f"  {scenario:<40} {speedup:>6.2f}x faster")

avg_speedup = sum(s for _, s in results) / len(results)
print(f"\n  {'Average Speedup':<40} {avg_speedup:>6.2f}x faster")

print("\n✓ Quick test completed successfully!")
print("  Run 'python scripts/real_world_benchmark.py' for full benchmark")
