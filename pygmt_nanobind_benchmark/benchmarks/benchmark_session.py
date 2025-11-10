"""
Session Management Benchmarks

Compares session creation and management overhead between
pygmt (ctypes) and pygmt_nb (nanobind).
"""

import pytest

try:
    import pygmt

    PYGMT_AVAILABLE = True
except ImportError:
    PYGMT_AVAILABLE = False

import pygmt_nb
from benchmark_base import BenchmarkRunner, ComparisonResult, format_benchmark_table


class TestSessionBenchmarks:
    """Session management benchmark tests using pytest-benchmark."""

    def test_session_creation_pygmt_nb(self, benchmark):
        """Benchmark pygmt_nb session creation."""

        def create_session():
            session = pygmt_nb.Session()
            return session

        result = benchmark(create_session)
        print(f"\npygmt_nb session creation: {result}")

    @pytest.mark.skipif(not PYGMT_AVAILABLE, reason="pygmt not installed")
    def test_session_creation_pygmt(self, benchmark):
        """Benchmark pygmt session creation."""

        def create_session():
            session = pygmt.clib.Session()
            return session

        result = benchmark(create_session)
        print(f"\npygmt session creation: {result}")

    def test_context_manager_pygmt_nb(self, benchmark):
        """Benchmark pygmt_nb context manager."""

        def use_context_manager():
            with pygmt_nb.Session() as session:
                _ = session.info()

        result = benchmark(use_context_manager)
        print(f"\npygmt_nb context manager: {result}")

    @pytest.mark.skipif(not PYGMT_AVAILABLE, reason="pygmt not installed")
    def test_context_manager_pygmt(self, benchmark):
        """Benchmark pygmt context manager."""

        def use_context_manager():
            with pygmt.clib.Session() as session:
                _ = session.info

        result = benchmark(use_context_manager)
        print(f"\npygmt context manager: {result}")

    def test_session_info_pygmt_nb(self, benchmark):
        """Benchmark pygmt_nb session.info() call."""
        session = pygmt_nb.Session()

        def get_info():
            return session.info()

        result = benchmark(get_info)
        print(f"\npygmt_nb session.info(): {result}")

    @pytest.mark.skipif(not PYGMT_AVAILABLE, reason="pygmt not installed")
    def test_session_info_pygmt(self, benchmark):
        """Benchmark pygmt session.info call."""
        session = pygmt.clib.Session()

        def get_info():
            return session.info

        result = benchmark(get_info)
        print(f"\npygmt session.info: {result}")


def run_manual_benchmarks():
    """
    Run manual benchmarks using our custom BenchmarkRunner.

    This allows running benchmarks even without pytest-benchmark.
    """
    print("=" * 70)
    print("Session Management Benchmarks")
    print("=" * 70)

    runner = BenchmarkRunner(warmup=10, iterations=1000)
    comparisons = []

    # Benchmark 1: Session creation
    print("\n1. Session Creation")
    print("-" * 70)

    def create_pygmt_nb():
        session = pygmt_nb.Session()
        return session

    result_nb = runner.run(create_pygmt_nb, "pygmt_nb", measure_memory=True)
    print(result_nb)

    if PYGMT_AVAILABLE:

        def create_pygmt():
            session = pygmt.clib.Session()
            return session

        result_pygmt = runner.run(create_pygmt, "pygmt", measure_memory=True)
        print(f"\n{result_pygmt}")

        comparison = ComparisonResult(
            name="Session creation", baseline=result_pygmt, candidate=result_nb
        )
        comparisons.append(comparison)
        print(comparison)

    # Benchmark 2: Context manager
    print("\n\n2. Context Manager Usage")
    print("-" * 70)

    def context_pygmt_nb():
        with pygmt_nb.Session() as session:
            _ = session.info()

    result_nb = runner.run(context_pygmt_nb, "pygmt_nb", measure_memory=True)
    print(result_nb)

    if PYGMT_AVAILABLE:

        def context_pygmt():
            with pygmt.clib.Session() as session:
                _ = session.info

        result_pygmt = runner.run(context_pygmt, "pygmt", measure_memory=True)
        print(f"\n{result_pygmt}")

        comparison = ComparisonResult(
            name="Context manager", baseline=result_pygmt, candidate=result_nb
        )
        comparisons.append(comparison)
        print(comparison)

    # Benchmark 3: Info access
    print("\n\n3. Session Info Access")
    print("-" * 70)

    session_nb = pygmt_nb.Session()

    def info_pygmt_nb():
        return session_nb.info()

    result_nb = runner.run(info_pygmt_nb, "pygmt_nb", measure_memory=False)
    print(result_nb)

    if PYGMT_AVAILABLE:
        session_pygmt = pygmt.clib.Session()

        def info_pygmt():
            return session_pygmt.info

        result_pygmt = runner.run(info_pygmt, "pygmt", measure_memory=False)
        print(f"\n{result_pygmt}")

        comparison = ComparisonResult(
            name="Info access", baseline=result_pygmt, candidate=result_nb
        )
        comparisons.append(comparison)
        print(comparison)

    # Summary table
    if comparisons:
        print("\n\n" + "=" * 70)
        print("Summary: pygmt vs pygmt_nb")
        print("=" * 70)
        print(format_benchmark_table(comparisons))

    return comparisons


if __name__ == "__main__":
    run_manual_benchmarks()
