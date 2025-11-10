# https://just.systems

default: help

help:
    @just --list

# Build the nanobind extension
build:
    cd pygmt_nanobind_benchmark && uv run python -m pip install -e . --no-build-isolation

# Install in development mode
install:
    cd pygmt_nanobind_benchmark && uv run python -m pip install -e .

# Run all tests
test:
    cd pygmt_nanobind_benchmark && uv run pytest tests/ -v

# Run specific test
test-file file:
    cd pygmt_nanobind_benchmark && uv run pytest {{file}} -v

# Run benchmarks
benchmark:
    cd pygmt_nanobind_benchmark && uv run python benchmarks/compare_with_pygmt.py

# Run validation (pixel-perfect comparison)
validate:
    cd pygmt_nanobind_benchmark && uv run python validation/validate_examples.py

# Format Python code
format:
    uv run ruff format pygmt_nanobind_benchmark/

# Lint Python code
lint:
    uv run ruff check pygmt_nanobind_benchmark/

# Type check with mypy
typecheck:
    cd pygmt_nanobind_benchmark && uv run mypy python/ tests/

# Run all quality checks
verify: format lint typecheck test

# Clean build artifacts
clean:
    rm -rf pygmt_nanobind_benchmark/build/
    rm -rf pygmt_nanobind_benchmark/*.egg-info/
    rm -rf pygmt_nanobind_benchmark/python/**/__pycache__/
    rm -rf pygmt_nanobind_benchmark/tests/__pycache__/
    find . -name "*.so" -delete
    find . -name "*.pyc" -delete