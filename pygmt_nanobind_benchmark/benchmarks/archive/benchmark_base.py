"""
Benchmark base classes and utilities

Provides common infrastructure for all benchmarks.
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, Optional
import sys
import tracemalloc


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    name: str
    mean_time: float  # seconds
    median_time: float  # seconds
    std_dev: float  # seconds
    iterations: int
    memory_current: Optional[int] = None  # bytes
    memory_peak: Optional[int] = None  # bytes

    @property
    def ops_per_second(self) -> float:
        """Calculate operations per second."""
        if self.mean_time > 0:
            return 1.0 / self.mean_time
        return 0.0

    def format_time(self, seconds: float) -> str:
        """Format time in human-readable format."""
        if seconds >= 1.0:
            return f"{seconds:.3f} s"
        elif seconds >= 0.001:
            return f"{seconds * 1000:.3f} ms"
        elif seconds >= 0.000001:
            return f"{seconds * 1000000:.3f} µs"
        else:
            return f"{seconds * 1000000000:.3f} ns"

    def __str__(self) -> str:
        """String representation of results."""
        lines = [
            f"Benchmark: {self.name}",
            f"  Mean:       {self.format_time(self.mean_time)}",
            f"  Median:     {self.format_time(self.median_time)}",
            f"  Std Dev:    {self.format_time(self.std_dev)}",
            f"  Ops/sec:    {self.ops_per_second:.2f}",
            f"  Iterations: {self.iterations}",
        ]
        if self.memory_current is not None:
            lines.append(f"  Memory:     {self.memory_current / 1024 / 1024:.2f} MB")
        if self.memory_peak is not None:
            lines.append(f"  Peak Mem:   {self.memory_peak / 1024 / 1024:.2f} MB")
        return "\n".join(lines)


@dataclass
class ComparisonResult:
    """Comparison between two benchmark results."""

    name: str
    baseline: BenchmarkResult
    candidate: BenchmarkResult

    @property
    def speedup(self) -> float:
        """Calculate speedup (baseline / candidate)."""
        if self.candidate.mean_time > 0:
            return self.baseline.mean_time / self.candidate.mean_time
        return 0.0

    @property
    def memory_ratio(self) -> Optional[float]:
        """Calculate memory usage ratio (baseline / candidate)."""
        if (
            self.baseline.memory_current is not None
            and self.candidate.memory_current is not None
            and self.candidate.memory_current > 0
        ):
            return self.baseline.memory_current / self.candidate.memory_current
        return None

    def __str__(self) -> str:
        """String representation of comparison."""
        lines = [
            f"\nComparison: {self.name}",
            f"  Baseline:   {self.baseline.format_time(self.baseline.mean_time)}",
            f"  Candidate:  {self.candidate.format_time(self.candidate.mean_time)}",
            f"  Speedup:    {self.speedup:.2f}x",
        ]
        if self.memory_ratio is not None:
            lines.append(f"  Memory:     {self.memory_ratio:.2f}x")
        return "\n".join(lines)


class BenchmarkRunner:
    """Simple benchmark runner."""

    def __init__(self, warmup: int = 3, iterations: int = 100):
        """
        Initialize benchmark runner.

        Args:
            warmup: Number of warmup iterations
            iterations: Number of measured iterations
        """
        self.warmup = warmup
        self.iterations = iterations

    def run(
        self, func: Callable[[], Any], name: str, measure_memory: bool = False
    ) -> BenchmarkResult:
        """
        Run a benchmark.

        Args:
            func: Function to benchmark (no arguments)
            name: Benchmark name
            measure_memory: Whether to measure memory usage

        Returns:
            BenchmarkResult with timing and optional memory data
        """
        # Warmup
        for _ in range(self.warmup):
            func()

        # Start memory tracking if requested
        if measure_memory:
            tracemalloc.start()
            tracemalloc.reset_peak()

        # Measure iterations
        times = []
        for _ in range(self.iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)

        # Calculate statistics
        times.sort()
        mean_time = sum(times) / len(times)
        median_time = times[len(times) // 2]
        variance = sum((t - mean_time) ** 2 for t in times) / len(times)
        std_dev = variance**0.5

        # Get memory stats if tracking
        memory_current = None
        memory_peak = None
        if measure_memory:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            memory_current = current
            memory_peak = peak

        return BenchmarkResult(
            name=name,
            mean_time=mean_time,
            median_time=median_time,
            std_dev=std_dev,
            iterations=self.iterations,
            memory_current=memory_current,
            memory_peak=memory_peak,
        )

    def compare(
        self, baseline_func: Callable, candidate_func: Callable, name: str
    ) -> ComparisonResult:
        """
        Compare two implementations.

        Args:
            baseline_func: Baseline implementation
            candidate_func: Candidate implementation
            name: Comparison name

        Returns:
            ComparisonResult with speedup information
        """
        baseline = self.run(baseline_func, f"{name} (baseline)", measure_memory=True)
        candidate = self.run(
            candidate_func, f"{name} (candidate)", measure_memory=True
        )

        return ComparisonResult(name=name, baseline=baseline, candidate=candidate)


def format_benchmark_table(comparisons: list[ComparisonResult]) -> str:
    """
    Format comparison results as a markdown table.

    Args:
        comparisons: List of comparison results

    Returns:
        Markdown table string
    """
    lines = [
        "| Operation | Baseline | Candidate | Speedup |",
        "|-----------|----------|-----------|---------|",
    ]

    for comp in comparisons:
        baseline_time = comp.baseline.format_time(comp.baseline.mean_time)
        candidate_time = comp.candidate.format_time(comp.candidate.mean_time)
        speedup = f"{comp.speedup:.2f}x"

        lines.append(f"| {comp.name} | {baseline_time} | {candidate_time} | {speedup} |")

    return "\n".join(lines)
