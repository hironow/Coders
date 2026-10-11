# Coders

Please read [AGENTS.md](./AGENTS.md) first and follow the instructions there.

1. [pygmt_nanobind_benchmark](./pygmt_nanobind_benchmark/INSTRUCTIONS)
2. [tesseract_nanobind_benchmark](./tesseract_nanobind_benchmark/INSTRUCTIONS)
3. [mlt_nanobind_benchmark](./mlt_nanobind_benchmark/INSTRUCTIONS)

## Native package checks

Install uv, just, actionlint, GMT (including its headers and Ghostscript),
Tesseract, and Leptonica. Run `just check` at the repository root.
The gate builds both CI-tested native packages, checks Python formatting,
lint and types, runs Semgrep, and executes their tests.
`just verify` runs the same gate. `just fmt` formats their Python code.

Python dependencies come from the official PyPI registry and the package
lockfiles. Set `GMT_INCLUDE_DIR` and `GMT_LIBRARY_DIR` when GMT is installed
outside the system search paths.
