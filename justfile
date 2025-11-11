# https://just.systems

default: help

help:
    @just --list

UV := "uv"
PYTHON := "uv run python"
PIP := "uv pip"
PYTEST := "uv run pytest"

# Tesseract nanobind benchmark

tesseract-build:
    cd tesseract_nanobind_benchmark && {{PIP}} install -e .

tesseract-check:
    {{UV}} tool install ruff
    {{UV}} tool install semgrep
    @echo "Installed tools:"
    @{{UV}} tool list
    {{UV}} tool run ruff check tesseract_nanobind_benchmark/
    {{UV}} tool run semgrep --config=auto tesseract_nanobind_benchmark/

tesseract-test:
    cd tesseract_nanobind_benchmark && {{PYTEST}} tests/ -v

tesseract-benchmark:
    cd tesseract_nanobind_benchmark && {{PYTHON}} benchmarks/benchmark.py

tesseract-clean:
    cd tesseract_nanobind_benchmark && rm -rf build/ dist/ *.egg-info .pytest_cache/