# https://just.systems

default: help

help:
    @just --list

# Tesseract nanobind benchmark
tesseract-build:
    cd tesseract_nanobind_benchmark && pip3 install --user -e .

tesseract-test:
    cd tesseract_nanobind_benchmark && python3 -m pytest tests/ -v

tesseract-benchmark:
    cd tesseract_nanobind_benchmark && python3 benchmarks/run_benchmarks.py

tesseract-benchmark-all:
    cd tesseract_nanobind_benchmark && python3 benchmarks/compare_all.py

tesseract-clean:
    cd tesseract_nanobind_benchmark && rm -rf build/ dist/ *.egg-info .pytest_cache/