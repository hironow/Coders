#!/usr/bin/env python3
"""
Main benchmark comparison script

Runs all benchmarks and generates a comprehensive comparison report.
"""

import sys
from pathlib import Path
from datetime import datetime

# Check for pygmt availability
try:
    import pygmt

    PYGMT_AVAILABLE = True
    PYGMT_VERSION = pygmt.__version__
except ImportError:
    PYGMT_AVAILABLE = False
    PYGMT_VERSION = "Not installed"

import pygmt_nb

# Import benchmark modules
from benchmark_session import run_manual_benchmarks as run_session_benchmarks


def print_header():
    """Print benchmark header with environment info."""
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  PyGMT nanobind Performance Benchmark Suite".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"pygmt: {PYGMT_VERSION}")
    print(f"pygmt_nb: {pygmt_nb.__version__}")
    print()


def print_footer(total_comparisons: int, avg_speedup: float):
    """Print benchmark footer with summary."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Benchmark Summary".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print(f"Total comparisons: {total_comparisons}")
    if total_comparisons > 0:
        print(f"Average speedup: {avg_speedup:.2f}x")
        print()
        if avg_speedup > 1.0:
            improvement = (avg_speedup - 1.0) * 100
            print(f"✓ pygmt_nb is {improvement:.1f}% faster on average")
        elif avg_speedup < 1.0:
            slowdown = (1.0 - avg_speedup) * 100
            print(f"✗ pygmt_nb is {slowdown:.1f}% slower on average")
        else:
            print("≈ Performance is equivalent")
    print()


def save_results_to_markdown(comparisons: list, output_file: Path):
    """Save benchmark results to a markdown file."""
    with output_file.open("w") as f:
        f.write("# PyGMT nanobind Benchmark Results\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Python**: {sys.version.split()[0]}\n\n")
        f.write(f"**pygmt**: {PYGMT_VERSION}\n\n")
        f.write(f"**pygmt_nb**: {pygmt_nb.__version__}\n\n")
        f.write("---\n\n")

        if not PYGMT_AVAILABLE:
            f.write(
                "⚠️ **Note**: pygmt is not installed. "
                "Only pygmt_nb baseline measurements are available.\n\n"
            )
        else:
            f.write("## Session Management Benchmarks\n\n")

            from benchmark_base import format_benchmark_table

            f.write(format_benchmark_table(comparisons))
            f.write("\n\n")

            # Calculate statistics
            if comparisons:
                speedups = [c.speedup for c in comparisons]
                avg_speedup = sum(speedups) / len(speedups)
                min_speedup = min(speedups)
                max_speedup = max(speedups)

                f.write("## Summary Statistics\n\n")
                f.write(f"- **Average Speedup**: {avg_speedup:.2f}x\n")
                f.write(f"- **Min Speedup**: {min_speedup:.2f}x\n")
                f.write(f"- **Max Speedup**: {max_speedup:.2f}x\n")
                f.write(f"- **Total Benchmarks**: {len(comparisons)}\n")

    print(f"\n✓ Results saved to: {output_file}")


def main():
    """Main benchmark execution."""
    print_header()

    if not PYGMT_AVAILABLE:
        print("⚠️  WARNING: pygmt is not installed")
        print("   Only pygmt_nb baseline measurements will be collected")
        print("   Install pygmt to enable comparison benchmarks")
        print()
        print("   Installation: pip install pygmt")
        print()

    all_comparisons = []

    # Run session benchmarks
    print("\n" + "═" * 70)
    print("Category: Session Management")
    print("═" * 70)
    session_comparisons = run_session_benchmarks()
    all_comparisons.extend(session_comparisons)

    # Calculate summary statistics
    total_comparisons = len(all_comparisons)
    avg_speedup = 0.0
    if total_comparisons > 0:
        avg_speedup = sum(c.speedup for c in all_comparisons) / total_comparisons

    # Print footer
    print_footer(total_comparisons, avg_speedup)

    # Save results
    output_dir = Path(__file__).parent
    output_file = output_dir / "BENCHMARK_RESULTS.md"
    save_results_to_markdown(all_comparisons, output_file)

    return 0 if PYGMT_AVAILABLE else 1


if __name__ == "__main__":
    sys.exit(main())
