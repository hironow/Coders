"""
PyGMT nanobind benchmark suite

This package provides comprehensive performance benchmarks comparing
pygmt (ctypes) with pygmt_nb (nanobind).
"""

from benchmark_base import (
    BenchmarkResult,
    BenchmarkRunner,
    ComparisonResult,
    format_benchmark_table,
)

__all__ = [
    "BenchmarkResult",
    "BenchmarkRunner",
    "ComparisonResult",
    "format_benchmark_table",
]
