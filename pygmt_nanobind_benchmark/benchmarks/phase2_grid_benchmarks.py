#!/usr/bin/env python3
"""
Phase 2 Benchmarks: Grid + NumPy Integration

Compares performance between pygmt_nb and PyGMT for:
1. Grid loading from file
2. NumPy data access
3. Memory usage
4. Data manipulation operations
"""

import sys
import time
import tracemalloc
import statistics
from pathlib import Path
from typing import Callable, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pygmt
    PYGMT_AVAILABLE = True
except ImportError:
    PYGMT_AVAILABLE = False
    print("⚠️  PyGMT not installed - will only benchmark pygmt_nb")

import pygmt_nb
import numpy as np


class GridBenchmarkRunner:
    """Benchmark runner for Grid operations."""

    def __init__(self, grid_file: str, warmup: int = 3, iterations: int = 50):
        self.grid_file = grid_file
        self.warmup = warmup
        self.iterations = iterations

    def run(
        self,
        func: Callable[[], Any],
        name: str,
        measure_memory: bool = False
    ) -> dict:
        """
        Run a benchmark.

        Args:
            func: Function to benchmark
            name: Benchmark name
            measure_memory: Whether to measure memory usage

        Returns:
            dict: Benchmark results
        """
        # Warmup
        for _ in range(self.warmup):
            try:
                result = func()
                # Clean up result to avoid memory accumulation
                del result
            except Exception as e:
                print(f"❌ Warmup failed for {name}: {e}")
                return None

        # Measure iterations
        times = []
        memory_peak = 0

        for i in range(self.iterations):
            if measure_memory:
                tracemalloc.start()

            start = time.perf_counter()
            try:
                result = func()
                end = time.perf_counter()
                times.append(end - start)

                # Clean up
                del result

                if measure_memory:
                    current, peak = tracemalloc.get_traced_memory()
                    memory_peak = max(memory_peak, peak)
                    tracemalloc.stop()
            except Exception as e:
                print(f"❌ Iteration {i} failed for {name}: {e}")
                if measure_memory:
                    tracemalloc.stop()
                return None

        if not times:
            return None

        mean_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0

        return {
            "name": name,
            "mean_time_ms": mean_time * 1000,
            "std_dev_ms": std_dev * 1000,
            "ops_per_sec": 1.0 / mean_time if mean_time > 0 else 0,
            "memory_peak_mb": memory_peak / (1024 * 1024) if measure_memory else 0,
            "iterations": len(times)
        }


def benchmark_grid_loading(runner: GridBenchmarkRunner) -> dict:
    """Benchmark grid loading from file."""
    results = {}

    print("\n" + "="*70)
    print("Benchmark 1: Grid Loading from File")
    print("="*70)

    # pygmt_nb
    def load_pygmt_nb():
        with pygmt_nb.Session() as session:
            grid = pygmt_nb.Grid(session, runner.grid_file)
            # Return something to ensure it's not optimized away
            return grid.shape

    print("\n📊 Running pygmt_nb grid loading...")
    result = runner.run(load_pygmt_nb, "pygmt_nb_grid_load", measure_memory=True)
    if result:
        results["pygmt_nb"] = result
        print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
        print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
        print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    # PyGMT
    if PYGMT_AVAILABLE:
        def load_pygmt():
            grid = pygmt.load_dataarray(runner.grid_file)
            return grid.shape

        print("\n📊 Running PyGMT grid loading...")
        result = runner.run(load_pygmt, "pygmt_grid_load", measure_memory=True)
        if result:
            results["pygmt"] = result
            print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
            print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
            print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    return results


def benchmark_data_access(runner: GridBenchmarkRunner) -> dict:
    """Benchmark NumPy data access."""
    results = {}

    print("\n" + "="*70)
    print("Benchmark 2: NumPy Data Access")
    print("="*70)

    # pygmt_nb - pre-load grid once
    with pygmt_nb.Session() as session:
        grid_nb = pygmt_nb.Grid(session, runner.grid_file)

        def access_pygmt_nb():
            data = grid_nb.data()
            # Do a simple operation to ensure data is accessed
            return data.mean()

        print("\n📊 Running pygmt_nb data access...")
        result = runner.run(access_pygmt_nb, "pygmt_nb_data_access", measure_memory=True)
        if result:
            results["pygmt_nb"] = result
            print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
            print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
            print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    # PyGMT
    if PYGMT_AVAILABLE:
        grid_pygmt = pygmt.load_dataarray(runner.grid_file)

        def access_pygmt():
            data = grid_pygmt.values
            return data.mean()

        print("\n📊 Running PyGMT data access...")
        result = runner.run(access_pygmt, "pygmt_data_access", measure_memory=True)
        if result:
            results["pygmt"] = result
            print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
            print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
            print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    return results


def benchmark_data_manipulation(runner: GridBenchmarkRunner) -> dict:
    """Benchmark NumPy data manipulation operations."""
    results = {}

    print("\n" + "="*70)
    print("Benchmark 3: Data Manipulation (NumPy Operations)")
    print("="*70)

    # pygmt_nb
    with pygmt_nb.Session() as session:
        grid_nb = pygmt_nb.Grid(session, runner.grid_file)

        def manipulate_pygmt_nb():
            data = grid_nb.data()
            # Typical operations: normalize, compute statistics
            mean = data.mean()
            std = data.std()
            normalized = (data - mean) / std
            return normalized.max()

        print("\n📊 Running pygmt_nb data manipulation...")
        result = runner.run(manipulate_pygmt_nb, "pygmt_nb_manipulation", measure_memory=True)
        if result:
            results["pygmt_nb"] = result
            print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
            print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
            print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    # PyGMT
    if PYGMT_AVAILABLE:
        grid_pygmt = pygmt.load_dataarray(runner.grid_file)

        def manipulate_pygmt():
            data = grid_pygmt.values
            mean = data.mean()
            std = data.std()
            normalized = (data - mean) / std
            return normalized.max()

        print("\n📊 Running PyGMT data manipulation...")
        result = runner.run(manipulate_pygmt, "pygmt_manipulation", measure_memory=True)
        if result:
            results["pygmt"] = result
            print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
            print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
            print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    return results


def print_comparison(benchmark_name: str, results: dict):
    """Print comparison between pygmt_nb and PyGMT."""
    if "pygmt_nb" not in results or "pygmt" not in results:
        print(f"\n⚠️  Cannot compare {benchmark_name} - missing results")
        return

    nb = results["pygmt_nb"]
    pygmt = results["pygmt"]

    print(f"\n" + "="*70)
    print(f"Comparison: {benchmark_name}")
    print("="*70)

    # Time comparison
    speedup = pygmt["mean_time_ms"] / nb["mean_time_ms"]
    print(f"\n⏱️  Time:")
    print(f"   pygmt_nb: {nb['mean_time_ms']:.3f} ms")
    print(f"   PyGMT:    {pygmt['mean_time_ms']:.3f} ms")
    if speedup > 1:
        print(f"   ✅ pygmt_nb is {speedup:.2f}x FASTER")
    elif speedup < 1:
        print(f"   ⚠️  pygmt_nb is {1/speedup:.2f}x slower")
    else:
        print(f"   ≈  Similar performance")

    # Memory comparison
    if nb["memory_peak_mb"] > 0 and pygmt["memory_peak_mb"] > 0:
        mem_improvement = pygmt["memory_peak_mb"] / nb["memory_peak_mb"]
        print(f"\n💾 Memory:")
        print(f"   pygmt_nb: {nb['memory_peak_mb']:.2f} MB")
        print(f"   PyGMT:    {pygmt['memory_peak_mb']:.2f} MB")
        if mem_improvement > 1:
            print(f"   ✅ pygmt_nb uses {mem_improvement:.2f}x LESS memory")
        elif mem_improvement < 1:
            print(f"   ⚠️  pygmt_nb uses {1/mem_improvement:.2f}x more memory")
        else:
            print(f"   ≈  Similar memory usage")


def generate_markdown_report(all_results: dict, grid_file: str):
    """Generate markdown report of benchmark results."""
    report = []

    report.append("# Phase 2 Benchmark Results: Grid + NumPy Integration")
    report.append("")
    report.append(f"**Grid File**: `{Path(grid_file).name}`")

    # Get grid info
    with pygmt_nb.Session() as session:
        grid = pygmt_nb.Grid(session, grid_file)
        shape = grid.shape
        region = grid.region

    report.append(f"**Grid Size**: {shape[0]} × {shape[1]} = {shape[0] * shape[1]:,} elements")
    report.append(f"**Region**: ({region[0]}, {region[1]}, {region[2]}, {region[3]})")
    report.append("")

    # Summary table
    report.append("## Summary")
    report.append("")
    report.append("| Operation | pygmt_nb | PyGMT | Speedup | Memory Improvement |")
    report.append("|-----------|----------|-------|---------|-------------------|")

    for bench_name, results in all_results.items():
        if "pygmt_nb" in results and "pygmt" in results:
            nb = results["pygmt_nb"]
            pg = results["pygmt"]
            speedup = pg["mean_time_ms"] / nb["mean_time_ms"]
            mem_improvement = pg["memory_peak_mb"] / nb["memory_peak_mb"] if nb["memory_peak_mb"] > 0 else 1.0

            report.append(
                f"| {bench_name} | {nb['mean_time_ms']:.2f} ms | {pg['mean_time_ms']:.2f} ms | "
                f"**{speedup:.2f}x** | **{mem_improvement:.2f}x** |"
            )

    # Detailed results
    report.append("")
    report.append("## Detailed Results")
    report.append("")

    for bench_name, results in all_results.items():
        report.append(f"### {bench_name}")
        report.append("")

        if "pygmt_nb" in results:
            nb = results["pygmt_nb"]
            report.append("**pygmt_nb**:")
            report.append(f"- Time: {nb['mean_time_ms']:.3f} ms ± {nb['std_dev_ms']:.3f} ms")
            report.append(f"- Throughput: {nb['ops_per_sec']:.1f} ops/sec")
            report.append(f"- Memory: {nb['memory_peak_mb']:.2f} MB peak")
            report.append("")

        if "pygmt" in results:
            pg = results["pygmt"]
            report.append("**PyGMT**:")
            report.append(f"- Time: {pg['mean_time_ms']:.3f} ms ± {pg['std_dev_ms']:.3f} ms")
            report.append(f"- Throughput: {pg['ops_per_sec']:.1f} ops/sec")
            report.append(f"- Memory: {pg['memory_peak_mb']:.2f} MB peak")
            report.append("")

        if "pygmt_nb" in results and "pygmt" in results:
            nb = results["pygmt_nb"]
            pg = results["pygmt"]
            speedup = pg["mean_time_ms"] / nb["mean_time_ms"]
            mem_improvement = pg["memory_peak_mb"] / nb["memory_peak_mb"] if nb["memory_peak_mb"] > 0 else 1.0

            report.append("**Comparison**:")
            if speedup > 1:
                report.append(f"- ✅ pygmt_nb is **{speedup:.2f}x faster**")
            elif speedup < 1:
                report.append(f"- ⚠️  pygmt_nb is {1/speedup:.2f}x slower")

            if mem_improvement > 1:
                report.append(f"- ✅ pygmt_nb uses **{mem_improvement:.2f}x less memory**")
            elif mem_improvement < 1:
                report.append(f"- ⚠️  pygmt_nb uses {1/mem_improvement:.2f}x more memory")
            report.append("")

    return "\n".join(report)


def main():
    """Run all Phase 2 benchmarks."""
    print("="*70)
    print("Phase 2 Benchmarks: Grid + NumPy Integration")
    print("="*70)

    # Check PyGMT availability
    if not PYGMT_AVAILABLE:
        print("\n⚠️  PyGMT not installed. Installing PyGMT for comparison...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pygmt"])
            import pygmt
            globals()["PYGMT_AVAILABLE"] = True
            globals()["pygmt"] = pygmt
            print("✅ PyGMT installed successfully")
        except Exception as e:
            print(f"❌ Failed to install PyGMT: {e}")
            print("   Continuing with pygmt_nb only...")

    # Setup
    grid_file = str(Path(__file__).parent.parent / "tests" / "data" / "large_grid.nc")

    if not Path(grid_file).exists():
        print(f"❌ Grid file not found: {grid_file}")
        print("   Creating test grid...")
        import subprocess
        subprocess.run([
            "gmt", "grdmath", "-R0/100/0/100", "-I0.5", "X", "Y", "MUL", "=",
            grid_file
        ])

    print(f"\n📁 Grid file: {grid_file}")

    # Show grid info
    with pygmt_nb.Session() as session:
        grid = pygmt_nb.Grid(session, grid_file)
        print(f"   Shape: {grid.shape}")
        print(f"   Region: {grid.region}")
        print(f"   Elements: {grid.shape[0] * grid.shape[1]:,}")

    # Run benchmarks
    runner = GridBenchmarkRunner(grid_file, warmup=3, iterations=50)

    all_results = {}

    # Benchmark 1: Grid loading
    results = benchmark_grid_loading(runner)
    if results:
        all_results["Grid Loading"] = results
        if PYGMT_AVAILABLE:
            print_comparison("Grid Loading", results)

    # Benchmark 2: Data access
    results = benchmark_data_access(runner)
    if results:
        all_results["Data Access"] = results
        if PYGMT_AVAILABLE:
            print_comparison("Data Access", results)

    # Benchmark 3: Data manipulation
    results = benchmark_data_manipulation(runner)
    if results:
        all_results["Data Manipulation"] = results
        if PYGMT_AVAILABLE:
            print_comparison("Data Manipulation", results)

    # Generate report
    print("\n" + "="*70)
    print("Generating Markdown Report")
    print("="*70)

    report = generate_markdown_report(all_results, grid_file)
    report_path = Path(__file__).parent / "PHASE2_BENCHMARK_RESULTS.md"
    report_path.write_text(report)
    print(f"\n✅ Report saved to: {report_path}")

    print("\n" + "="*70)
    print("✅ All Phase 2 benchmarks completed successfully!")
    print("="*70)


if __name__ == "__main__":
    main()
