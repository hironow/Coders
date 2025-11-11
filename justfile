# https://just.systems

default: help

help:
    @just --list


UV := "uv"
PYTHON := "uv run python"
PIP := "uv pip"
PYTEST := "uv run --all-extras pytest"

# Tesseract nanobind benchmark

tesseract-build:
    #!/usr/bin/env bash
    set -euo pipefail
    cd tesseract_nanobind_benchmark
    # Use --system flag if not in a virtual environment (for CI compatibility)
    if [ -n "${VIRTUAL_ENV:-}" ] || [ -d ".venv" ]; then
        {{PIP}} install -e .[test]
    else
        {{PIP}} install --system -e .[test]
    fi

tesseract-check:
    {{UV}} tool install ruff
    {{UV}} tool install semgrep
    @echo "Installed tools:"
    @{{UV}} tool list
    {{UV}} tool run ruff check tesseract_nanobind_benchmark/
    {{UV}} tool run semgrep --config=auto tesseract_nanobind_benchmark/

tesseract-test:
    #!/usr/bin/env bash
    set -euo pipefail
    cd tesseract_nanobind_benchmark
    # Use system python if not in a virtual environment (for CI compatibility)
    if [ -n "${VIRTUAL_ENV:-}" ] || [ -d ".venv" ]; then
        {{PYTEST}} tests/ -v
    else
        python -m pytest tests/ -v
    fi

tesseract-benchmark:
    #!/usr/bin/env bash
    set -euo pipefail
    cd tesseract_nanobind_benchmark
    # Use system python if not in a virtual environment (for CI compatibility)
    if [ -n "${VIRTUAL_ENV:-}" ] || [ -d ".venv" ]; then
        uv run --all-extras python benchmarks/benchmark.py
    else
        python benchmarks/benchmark.py
    fi

tesseract-clean:
    cd tesseract_nanobind_benchmark && rm -rf build/ dist/ *.egg-info .pytest_cache/

# Version management

# Show current version
tesseract-version:
    @grep '^version = ' tesseract_nanobind_benchmark/pyproject.toml | sed 's/version = "\(.*\)"/\1/'

# Bump patch version (0.1.0 -> 0.1.1)
tesseract-version-bump-patch:
    #!/usr/bin/env bash
    set -euo pipefail
    cd tesseract_nanobind_benchmark
    CURRENT=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    MAJOR=$(echo $CURRENT | cut -d. -f1)
    MINOR=$(echo $CURRENT | cut -d. -f2)
    PATCH=$(echo $CURRENT | cut -d. -f3)
    NEW_PATCH=$((PATCH + 1))
    NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
    sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    echo "Version bumped: $CURRENT -> $NEW_VERSION"
    cd ..
    git add tesseract_nanobind_benchmark/pyproject.toml
    git commit -m "Bump version to $NEW_VERSION"
    echo "✓ Committed version bump"

# Bump minor version (0.1.0 -> 0.2.0)
tesseract-version-bump-minor:
    #!/usr/bin/env bash
    set -euo pipefail
    cd tesseract_nanobind_benchmark
    CURRENT=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    MAJOR=$(echo $CURRENT | cut -d. -f1)
    MINOR=$(echo $CURRENT | cut -d. -f2)
    NEW_MINOR=$((MINOR + 1))
    NEW_VERSION="$MAJOR.$NEW_MINOR.0"
    sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    echo "Version bumped: $CURRENT -> $NEW_VERSION"
    cd ..
    git add tesseract_nanobind_benchmark/pyproject.toml
    git commit -m "Bump version to $NEW_VERSION"
    echo "✓ Committed version bump"

# Bump major version (0.1.0 -> 1.0.0)
tesseract-version-bump-major:
    #!/usr/bin/env bash
    set -euo pipefail
    cd tesseract_nanobind_benchmark
    CURRENT=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    MAJOR=$(echo $CURRENT | cut -d. -f1)
    NEW_MAJOR=$((MAJOR + 1))
    NEW_VERSION="$NEW_MAJOR.0.0"
    sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    echo "Version bumped: $CURRENT -> $NEW_VERSION"
    cd ..
    git add tesseract_nanobind_benchmark/pyproject.toml
    git commit -m "Bump version to $NEW_VERSION"
    echo "✓ Committed version bump"

# Create and push release tag
tesseract-release:
    #!/usr/bin/env bash
    set -euo pipefail
    cd tesseract_nanobind_benchmark
    VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    cd ..
    echo "Creating release tag: tesseract-nanobind-v$VERSION"
    git tag -a "tesseract-nanobind-v$VERSION" -m "Release version $VERSION"
    echo "✓ Tag created: tesseract-nanobind-v$VERSION"
    echo ""
    echo "To push the tag to remote, run:"
    echo "  git push origin tesseract-nanobind-v$VERSION"
    echo ""
    echo "Or to push all tags:"
    echo "  git push --tags"


# Build the nanobind extension
gmt-build:
    cd pygmt_nanobind_benchmark && uv run python -m pip install -e . --no-build-isolation

# Install in development mode
gmt-install:
    cd pygmt_nanobind_benchmark && uv run python -m pip install -e .

# Run all tests
gmt-test:
    cd pygmt_nanobind_benchmark && uv run pytest tests/ -v

# Run specific test
gmt-test-file file:
    cd pygmt_nanobind_benchmark && uv run pytest {{file}} -v

# Run all benchmarks
gmt-benchmark:
    cd pygmt_nanobind_benchmark && python3 benchmarks/compare_with_pygmt.py

# Run specific benchmark category
gmt-benchmark-category category:
    cd pygmt_nanobind_benchmark && python3 benchmarks/benchmark_{{category}}.py

# Show benchmark results
gmt-benchmark-results:
    @cat pygmt_nanobind_benchmark/benchmarks/BENCHMARK_RESULTS.md

# Run validation (pixel-perfect comparison)
gmt-validate:
    cd pygmt_nanobind_benchmark && uv run python validation/validate_examples.py

# Format Python code
gmt-format:
    uv run ruff format pygmt_nanobind_benchmark/

# Lint Python code
gmt-lint:
    uv run ruff check pygmt_nanobind_benchmark/

# Type check with mypy
gmt-typecheck:
    cd pygmt_nanobind_benchmark && uv run mypy python/ tests/

# Run all quality checks
gmt-verify: format lint typecheck test

# Clean build artifacts
gmt-clean:
    rm -rf pygmt_nanobind_benchmark/build/
    rm -rf pygmt_nanobind_benchmark/*.egg-info/
    rm -rf pygmt_nanobind_benchmark/python/**/__pycache__/
    rm -rf pygmt_nanobind_benchmark/tests/__pycache__/
    find . -name "*.so" -delete
    find . -name "*.pyc" -delete
