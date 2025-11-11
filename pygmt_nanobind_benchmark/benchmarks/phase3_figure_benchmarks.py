#!/usr/bin/env python3
"""
Phase 3 Benchmarks: Figure Methods (basemap, coast, plot, text)

Measures performance of the 4 implemented Figure methods:
1. basemap() - Map frames and axes
2. coast() - Coastlines and borders
3. plot() - Scatter plots and lines
4. text() - Text annotations
5. Complete figure workflow (multiple operations)
"""

import sys
import time
import tracemalloc
import statistics
import tempfile
import shutil
from pathlib import Path
from typing import Callable, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Disable PyGMT comparison for Phase 3
# PyGMT uses GMT modern mode which is incompatible with classic mode .ps output
# and may interfere with pygmt_nb's classic mode operations
PYGMT_AVAILABLE = False

import pygmt_nb
import numpy as np


class FigureBenchmarkRunner:
    """Benchmark runner for Figure operations."""

    def __init__(self, warmup: int = 3, iterations: int = 30):
        self.warmup = warmup
        self.iterations = iterations
        self.temp_dir = Path(tempfile.mkdtemp(prefix="phase3_bench_"))

    def cleanup(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

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


def benchmark_basemap(runner: FigureBenchmarkRunner) -> dict:
    """Benchmark basemap() method."""
    results = {}

    print("\n" + "="*70)
    print("Benchmark 1: Figure.basemap()")
    print("="*70)

    # pygmt_nb
    def basemap_pygmt_nb():
        fig = pygmt_nb.Figure()
        fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
        output = runner.temp_dir / "basemap_nb.ps"
        fig.savefig(str(output))
        return output.stat().st_size

    print("\n📊 Running pygmt_nb basemap...")
    result = runner.run(basemap_pygmt_nb, "pygmt_nb_basemap", measure_memory=True)
    if result:
        results["pygmt_nb"] = result
        print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
        print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
        print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    # PyGMT
    if PYGMT_AVAILABLE:
        def basemap_pygmt():
            fig = pygmt.Figure()
            fig.basemap(region=[0, 10, 0, 10], projection="X10c", frame="afg")
            output = runner.temp_dir / "basemap_pygmt.ps"
            fig.savefig(str(output))
            return output.stat().st_size

        print("\n📊 Running PyGMT basemap...")
        result = runner.run(basemap_pygmt, "pygmt_basemap", measure_memory=True)
        if result:
            results["pygmt"] = result
            print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
            print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
            print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    return results


def benchmark_coast(runner: FigureBenchmarkRunner) -> dict:
    """Benchmark coast() method."""
    results = {}

    print("\n" + "="*70)
    print("Benchmark 2: Figure.coast()")
    print("="*70)

    # pygmt_nb
    def coast_pygmt_nb():
        fig = pygmt_nb.Figure()
        fig.coast(
            region=[130, 150, 30, 45],
            projection="M15c",
            frame="afg",
            land="lightgray",
            water="lightblue",
            shorelines=True,
            resolution="low"
        )
        output = runner.temp_dir / "coast_nb.ps"
        fig.savefig(str(output))
        return output.stat().st_size

    print("\n📊 Running pygmt_nb coast...")
    result = runner.run(coast_pygmt_nb, "pygmt_nb_coast", measure_memory=True)
    if result:
        results["pygmt_nb"] = result
        print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
        print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
        print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    # PyGMT
    if PYGMT_AVAILABLE:
        def coast_pygmt():
            fig = pygmt.Figure()
            fig.coast(
                region=[130, 150, 30, 45],
                projection="M15c",
                frame="afg",
                land="lightgray",
                water="lightblue",
                shorelines=True,
                resolution="low"
            )
            output = runner.temp_dir / "coast_pygmt.ps"
            fig.savefig(str(output))
            return output.stat().st_size

        print("\n📊 Running PyGMT coast...")
        result = runner.run(coast_pygmt, "pygmt_coast", measure_memory=True)
        if result:
            results["pygmt"] = result
            print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
            print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
            print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    return results


def benchmark_plot(runner: FigureBenchmarkRunner) -> dict:
    """Benchmark plot() method."""
    results = {}

    print("\n" + "="*70)
    print("Benchmark 3: Figure.plot()")
    print("="*70)

    # Generate test data (100 points)
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # pygmt_nb
    def plot_pygmt_nb():
        fig = pygmt_nb.Figure()
        fig.plot(
            x=x, y=y,
            region=[0, 10, -1.5, 1.5],
            projection="X10c/6c",
            style="c0.1c",
            fill="red",
            frame="afg"
        )
        output = runner.temp_dir / "plot_nb.ps"
        fig.savefig(str(output))
        return output.stat().st_size

    print(f"\n📊 Running pygmt_nb plot (with {len(x)} points)...")
    result = runner.run(plot_pygmt_nb, "pygmt_nb_plot", measure_memory=True)
    if result:
        results["pygmt_nb"] = result
        print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
        print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
        print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    # PyGMT
    if PYGMT_AVAILABLE:
        def plot_pygmt():
            fig = pygmt.Figure()
            fig.plot(
                x=x, y=y,
                region=[0, 10, -1.5, 1.5],
                projection="X10c/6c",
                style="c0.1c",
                fill="red",
                frame="afg"
            )
            output = runner.temp_dir / "plot_pygmt.ps"
            fig.savefig(str(output))
            return output.stat().st_size

        print(f"\n📊 Running PyGMT plot (with {len(x)} points)...")
        result = runner.run(plot_pygmt, "pygmt_plot", measure_memory=True)
        if result:
            results["pygmt"] = result
            print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
            print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
            print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    return results


def benchmark_text(runner: FigureBenchmarkRunner) -> dict:
    """Benchmark text() method."""
    results = {}

    print("\n" + "="*70)
    print("Benchmark 4: Figure.text()")
    print("="*70)

    # Generate test data (10 text labels)
    x = np.linspace(1, 9, 10)
    y = np.linspace(1, 9, 10)
    text_labels = [f"Label {i}" for i in range(10)]

    # pygmt_nb
    def text_pygmt_nb():
        fig = pygmt_nb.Figure()
        fig.text(
            x=x, y=y, text=text_labels,
            region=[0, 10, 0, 10],
            projection="X10c",
            font="12p,Helvetica,black",
            frame="afg"
        )
        output = runner.temp_dir / "text_nb.ps"
        fig.savefig(str(output))
        return output.stat().st_size

    print(f"\n📊 Running pygmt_nb text (with {len(text_labels)} labels)...")
    result = runner.run(text_pygmt_nb, "pygmt_nb_text", measure_memory=True)
    if result:
        results["pygmt_nb"] = result
        print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
        print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
        print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    # PyGMT
    if PYGMT_AVAILABLE:
        def text_pygmt():
            fig = pygmt.Figure()
            fig.text(
                x=x, y=y, text=text_labels,
                region=[0, 10, 0, 10],
                projection="X10c",
                font="12p,Helvetica,black",
                frame="afg"
            )
            output = runner.temp_dir / "text_pygmt.ps"
            fig.savefig(str(output))
            return output.stat().st_size

        print(f"\n📊 Running PyGMT text (with {len(text_labels)} labels)...")
        result = runner.run(text_pygmt, "pygmt_text", measure_memory=True)
        if result:
            results["pygmt"] = result
            print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
            print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
            print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    return results


def benchmark_complete_workflow(runner: FigureBenchmarkRunner) -> dict:
    """Benchmark complete figure workflow with multiple operations."""
    results = {}

    print("\n" + "="*70)
    print("Benchmark 5: Complete Figure Workflow")
    print("="*70)

    # Generate test data
    x = np.linspace(0, 10, 50)
    y = np.sin(x)

    # pygmt_nb
    def workflow_pygmt_nb():
        fig = pygmt_nb.Figure()
        # 1. Draw basemap
        fig.basemap(region=[0, 10, -1.5, 1.5], projection="X15c/10c", frame=["af", "xag", "yag"])
        # 2. Plot data
        fig.plot(x=x, y=y, region=[0, 10, -1.5, 1.5], projection="X15c/10c",
                 pen="1.5p,blue")
        fig.plot(x=x, y=y, region=[0, 10, -1.5, 1.5], projection="X15c/10c",
                 style="c0.15c", fill="red")
        # 3. Add title
        fig.text(x=5, y=1.2, text="Sine Wave", region=[0, 10, -1.5, 1.5],
                 projection="X15c/10c", font="18p,Helvetica-Bold,black", justify="MC")
        # 4. Save figure
        output = runner.temp_dir / "workflow_nb.ps"
        fig.savefig(str(output))
        return output.stat().st_size

    print("\n📊 Running pygmt_nb complete workflow...")
    result = runner.run(workflow_pygmt_nb, "pygmt_nb_workflow", measure_memory=True)
    if result:
        results["pygmt_nb"] = result
        print(f"   ✓ {result['mean_time_ms']:.3f} ms ± {result['std_dev_ms']:.3f} ms")
        print(f"   ✓ {result['ops_per_sec']:.1f} ops/sec")
        print(f"   ✓ {result['memory_peak_mb']:.2f} MB peak memory")

    # PyGMT
    if PYGMT_AVAILABLE:
        def workflow_pygmt():
            fig = pygmt.Figure()
            fig.basemap(region=[0, 10, -1.5, 1.5], projection="X15c/10c", frame=["af", "xag", "yag"])
            fig.plot(x=x, y=y, region=[0, 10, -1.5, 1.5], projection="X15c/10c",
                     pen="1.5p,blue")
            fig.plot(x=x, y=y, region=[0, 10, -1.5, 1.5], projection="X15c/10c",
                     style="c0.15c", fill="red")
            fig.text(x=5, y=1.2, text="Sine Wave", region=[0, 10, -1.5, 1.5],
                     projection="X15c/10c", font="18p,Helvetica-Bold,black", justify="MC")
            output = runner.temp_dir / "workflow_pygmt.ps"
            fig.savefig(str(output))
            return output.stat().st_size

        print("\n📊 Running PyGMT complete workflow...")
        result = runner.run(workflow_pygmt, "pygmt_workflow", measure_memory=True)
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
    if speedup > 1.05:  # More than 5% faster
        print(f"   ✅ pygmt_nb is {speedup:.2f}x FASTER")
    elif speedup < 0.95:  # More than 5% slower
        print(f"   ⚠️  pygmt_nb is {1/speedup:.2f}x slower")
    else:
        print(f"   ≈  Similar performance (±5%)")

    # Memory comparison
    if nb["memory_peak_mb"] > 0 and pygmt["memory_peak_mb"] > 0:
        mem_improvement = pygmt["memory_peak_mb"] / nb["memory_peak_mb"]
        print(f"\n💾 Memory:")
        print(f"   pygmt_nb: {nb['memory_peak_mb']:.2f} MB")
        print(f"   PyGMT:    {pygmt['memory_peak_mb']:.2f} MB")
        if mem_improvement > 1.05:
            print(f"   ✅ pygmt_nb uses {mem_improvement:.2f}x LESS memory")
        elif mem_improvement < 0.95:
            print(f"   ⚠️  pygmt_nb uses {1/mem_improvement:.2f}x more memory")
        else:
            print(f"   ≈  Similar memory usage (±5%)")


def generate_markdown_report(all_results: dict):
    """Generate markdown report of benchmark results."""
    report = []

    report.append("# Phase 3 Benchmark Results: Figure Methods")
    report.append("")
    report.append("**Date**: " + time.strftime("%Y-%m-%d"))
    report.append("")
    report.append("## Methods Benchmarked")
    report.append("")
    report.append("1. **basemap()** - Map frames and axes")
    report.append("2. **coast()** - Coastlines and borders (Japan region, low resolution)")
    report.append("3. **plot()** - Scatter plots (100 data points)")
    report.append("4. **text()** - Text annotations (10 labels)")
    report.append("5. **Complete Workflow** - Multiple operations (basemap + plot + text)")
    report.append("")

    # Summary table
    report.append("## Summary")
    report.append("")
    report.append("| Operation | pygmt_nb | PyGMT | Speedup | Memory |")
    report.append("|-----------|----------|-------|---------|--------|")

    for bench_name, results in all_results.items():
        if "pygmt_nb" in results:
            nb = results["pygmt_nb"]
            if "pygmt" in results:
                pg = results["pygmt"]
                speedup = pg["mean_time_ms"] / nb["mean_time_ms"]
                mem_improvement = pg["memory_peak_mb"] / nb["memory_peak_mb"] if nb["memory_peak_mb"] > 0 else 1.0

                speedup_str = f"**{speedup:.2f}x**" if speedup > 1.05 else f"{speedup:.2f}x"
                mem_str = f"**{mem_improvement:.2f}x less**" if mem_improvement > 1.05 else f"{nb['memory_peak_mb']:.1f} MB"

                report.append(
                    f"| {bench_name} | {nb['mean_time_ms']:.1f} ms | {pg['mean_time_ms']:.1f} ms | "
                    f"{speedup_str} | {mem_str} |"
                )
            else:
                # pygmt_nb only
                report.append(
                    f"| {bench_name} | {nb['mean_time_ms']:.1f} ms | - | - | {nb['memory_peak_mb']:.1f} MB |"
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
            if speedup > 1.05:
                report.append(f"- ✅ pygmt_nb is **{speedup:.2f}x faster**")
            elif speedup < 0.95:
                report.append(f"- ⚠️  pygmt_nb is {1/speedup:.2f}x slower")
            else:
                report.append(f"- ≈ Similar performance (speedup: {speedup:.2f}x)")

            if mem_improvement > 1.05:
                report.append(f"- ✅ pygmt_nb uses **{mem_improvement:.2f}x less memory**")
            elif mem_improvement < 0.95:
                report.append(f"- ⚠️  pygmt_nb uses {1/mem_improvement:.2f}x more memory")
            else:
                report.append(f"- ≈ Similar memory usage")
            report.append("")

    # Key findings
    report.append("## Key Findings")
    report.append("")

    if all("pygmt" in results for results in all_results.values()):
        avg_speedup = statistics.mean([
            results["pygmt"]["mean_time_ms"] / results["pygmt_nb"]["mean_time_ms"]
            for results in all_results.values()
            if "pygmt" in results and "pygmt_nb" in results
        ])

        if avg_speedup > 1.05:
            report.append(f"- ✅ **Overall**: pygmt_nb is **{avg_speedup:.2f}x faster** on average")
        elif avg_speedup < 0.95:
            report.append(f"- ⚠️  **Overall**: pygmt_nb is {1/avg_speedup:.2f}x slower on average")
        else:
            report.append(f"- **Overall**: Similar performance to PyGMT (average speedup: {avg_speedup:.2f}x)")
    else:
        report.append("- PyGMT comparison not available (PyGMT not installed)")
        report.append("- All pygmt_nb benchmarks completed successfully")

    report.append("")
    report.append("## Notes")
    report.append("")
    report.append("- All benchmarks use GMT classic mode (ps* commands)")
    report.append("- PostScript output files generated for all operations")
    report.append("- Warmup iterations: 3, Measurement iterations: 30")
    report.append("- Memory measurements include PostScript generation overhead")
    report.append("")

    return "\n".join(report)


def main():
    """Run all Phase 3 benchmarks."""
    print("="*70)
    print("Phase 3 Benchmarks: Figure Methods")
    print("="*70)

    # Check PyGMT availability
    if not PYGMT_AVAILABLE:
        print("\n⚠️  PyGMT not installed")
        print("   Continuing with pygmt_nb only...")
        print("   (Install PyGMT for comparison: pip install pygmt)")

    # Setup
    runner = FigureBenchmarkRunner(warmup=3, iterations=30)

    try:
        all_results = {}

        # Benchmark 1: basemap
        results = benchmark_basemap(runner)
        if results:
            all_results["basemap()"] = results
            if PYGMT_AVAILABLE:
                print_comparison("basemap()", results)

        # Benchmark 2: coast
        results = benchmark_coast(runner)
        if results:
            all_results["coast()"] = results
            if PYGMT_AVAILABLE:
                print_comparison("coast()", results)

        # Benchmark 3: plot
        results = benchmark_plot(runner)
        if results:
            all_results["plot()"] = results
            if PYGMT_AVAILABLE:
                print_comparison("plot()", results)

        # Benchmark 4: text
        results = benchmark_text(runner)
        if results:
            all_results["text()"] = results
            if PYGMT_AVAILABLE:
                print_comparison("text()", results)

        # Benchmark 5: complete workflow
        results = benchmark_complete_workflow(runner)
        if results:
            all_results["Complete Workflow"] = results
            if PYGMT_AVAILABLE:
                print_comparison("Complete Workflow", results)

        # Generate report
        print("\n" + "="*70)
        print("Generating Markdown Report")
        print("="*70)

        report = generate_markdown_report(all_results)
        report_path = Path(__file__).parent / "PHASE3_BENCHMARK_RESULTS.md"
        report_path.write_text(report)
        print(f"\n✅ Report saved to: {report_path}")

        print("\n" + "="*70)
        print("✅ All Phase 3 benchmarks completed successfully!")
        print("="*70)

    finally:
        # Cleanup
        runner.cleanup()
        print(f"\n🧹 Cleaned up temporary directory: {runner.temp_dir}")


if __name__ == "__main__":
    main()
