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