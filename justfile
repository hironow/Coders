# https://just.systems

default: help

help:
    @just --list

# Validate the workflow and both CI-tested native packages
check: lint-workflows tesseract-build gmt-build tesseract-check gmt-check tesseract-test gmt-test

verify: check

# Create isolated local environments for the CI-tested packages
init-test-envs python="3.11":
    uv venv --python {{python}} tesseract_nanobind_benchmark/.venv
    uv venv --python {{python}} pygmt_nanobind_benchmark/.venv

lint-fix:
    cd tesseract_nanobind_benchmark && uv run --locked --only-group lint ruff check --fix .
    cd pygmt_nanobind_benchmark && uv run --locked --only-group lint ruff check --fix .

lint-workflows:
    actionlint .github/workflows/*.yaml


UV := "uv"
PYTHON := "uv run python"
PIP := "uv pip"
PYTEST := "uv run --all-extras pytest"

# Tesseract nanobind benchmark

[group('tesseract')]
tesseract-build:
    cd tesseract_nanobind_benchmark && uv sync --locked --all-extras --group lint --reinstall-package tesseract-nanobind

[group('tesseract')]
tesseract-check:
    cd tesseract_nanobind_benchmark && uv run --locked --only-group lint ruff check .
    cd tesseract_nanobind_benchmark && uv run --locked --only-group lint ruff format --check src tests benchmarks examples
    cd tesseract_nanobind_benchmark && uv run --locked --all-extras --group lint ty check
    uv tool run --from semgrep==1.179.0 semgrep --config=auto tesseract_nanobind_benchmark/

[group('tesseract')]
tesseract-test:
    cd tesseract_nanobind_benchmark && uv run --locked --all-extras --group lint pytest tests/ -v

[group('tesseract')]
tesseract-benchmark:
    cd tesseract_nanobind_benchmark && uv run --locked --all-extras --group lint python benchmarks/benchmark.py

[group('tesseract')]
tesseract-clean:
    cd tesseract_nanobind_benchmark && rm -rf build/ dist/ *.egg-info .pytest_cache/

# Version management

# Show current version
[group('tesseract')]
tesseract-version:
    @grep '^version = ' tesseract_nanobind_benchmark/pyproject.toml | sed 's/version = "\(.*\)"/\1/'

# Bump patch version (0.1.0 -> 0.1.1)
[group('tesseract')]
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
[group('tesseract')]
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
[group('tesseract')]
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
[group('tesseract')]
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
[group('gmt')]
gmt-build:
    cd pygmt_nanobind_benchmark && uv sync --locked --all-extras --group lint --reinstall-package pygmt-nb

[group('gmt')]
gmt-check:
    cd pygmt_nanobind_benchmark && uv run --locked --only-group lint ruff check .
    cd pygmt_nanobind_benchmark && uv run --locked --only-group lint ruff format --check python tests benchmarks validation
    cd pygmt_nanobind_benchmark && uv run --locked --all-extras --group lint ty check
    uv tool run --from semgrep==1.179.0 semgrep --config=auto pygmt_nanobind_benchmark/

[group('gmt')]
gmt-test:
    cd pygmt_nanobind_benchmark && uv run --locked --all-extras --group lint pytest tests/ -v

# Run all benchmarks
[group('gmt')]
gmt-benchmark:
    cd pygmt_nanobind_benchmark && uv run --locked --all-extras --group lint python benchmarks/benchmark.py

# Run validation suite
[group('gmt')]
gmt-validate:
    cd pygmt_nanobind_benchmark && uv run --locked --all-extras --group lint python validation/validate.py

# Clean build artifacts
[group('gmt')]
gmt-clean:
    rm -rf pygmt_nanobind_benchmark/build/
    rm -rf pygmt_nanobind_benchmark/*.egg-info/
    rm -rf pygmt_nanobind_benchmark/python/**/__pycache__/
    rm -rf pygmt_nanobind_benchmark/tests/__pycache__/
    find . -name "*.so" -delete
    find . -name "*.pyc" -delete

fmt:
    cd tesseract_nanobind_benchmark && uv run --locked --only-group lint ruff format src tests benchmarks examples
    cd pygmt_nanobind_benchmark && uv run --locked --only-group lint ruff format python tests benchmarks validation

lint: tesseract-check gmt-check

# Generate signatures from the real compiled native extensions.
native-stubs:
    cd tesseract_nanobind_benchmark && uv run --with nanobind --all-extras python -m nanobind.stubgen -m tesseract_nanobind._tesseract_nanobind -o src/tesseract_nanobind/_tesseract_nanobind.pyi
    cd pygmt_nanobind_benchmark && uv run --with nanobind --all-extras python -m nanobind.stubgen -m pygmt_nb.clib._pygmt_nb_core -o python/pygmt_nb/clib/_pygmt_nb_core.pyi
    cd pygmt_nanobind_benchmark && uv run --locked --only-group lint ruff check --fix --unsafe-fixes python/pygmt_nb/clib/_pygmt_nb_core.pyi
    just fmt

regression-variable-getters:
    cd tesseract_nanobind_benchmark && uv run --locked --all-extras --group lint pytest tests/test_compat_extended.py -k variable_getter -v
