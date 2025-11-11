# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Tesseract Nanobind project.

## Workflows

### 1. Tesseract Nanobind CI (`tesseract-nanobind-ci.yml`)

**Purpose**: Continuous Integration for build, test, and code quality checks.

**Triggers**:
- Push to `main` or `develop` branches (when tesseract_nanobind_benchmark files change)
- Pull requests to `main` or `develop` branches
- Manual dispatch

**Jobs**:

#### build-and-test
- **Matrix**: Tests on Ubuntu and macOS with Python 3.8-3.12
- **Steps**:
  1. Checkout repository with submodules
  2. Install system dependencies (Tesseract, Leptonica, CMake)
  3. Install Python dependencies
  4. Build the package
  5. Run test suite with coverage
  6. Upload coverage to Codecov (Ubuntu + Python 3.11 only)

#### compatibility-test
- **Purpose**: Verify tesserocr API compatibility
- **Platform**: Ubuntu with Python 3.11
- **Steps**:
  1. Install tesserocr alongside tesseract_nanobind
  2. Run compatibility tests to ensure drop-in replacement works

#### benchmark
- **Purpose**: Performance comparison against pytesseract and tesserocr
- **Triggers**: Only on pull requests or manual dispatch
- **Platform**: Ubuntu with Python 3.11
- **Steps**:
  1. Install all three implementations (pytesseract, tesserocr, tesseract_nanobind)
  2. Initialize test image submodules
  3. Run comprehensive benchmark comparing all three
  4. Upload benchmark results as artifact

#### code-quality
- **Purpose**: Code quality checks with ruff
- **Platform**: Ubuntu with Python 3.11
- **Steps**:
  1. Run ruff linter
  2. Check code formatting

### 2. Build Wheels (`tesseract-nanobind-build-wheels.yml`)

**Purpose**: Build distributable wheels for multiple platforms.

**Triggers**:
- Push tags matching `tesseract-nanobind-v*`
- Manual dispatch

**Jobs**:

#### build_wheels
- **Matrix**: Build on Ubuntu and macOS
- **Uses**: cibuildwheel for building wheels
- **Platforms**:
  - Linux: x86_64 (Python 3.8-3.12)
  - macOS: x86_64 and arm64 (Python 3.8-3.12)
- **Output**: Wheels for each platform uploaded as artifacts

#### build_sdist
- **Purpose**: Build source distribution
- **Platform**: Ubuntu
- **Output**: Source tarball uploaded as artifact

#### release
- **Purpose**: Create GitHub release with built wheels
- **Triggers**: Only on tag push
- **Steps**:
  1. Download all wheel and sdist artifacts
  2. Create GitHub release with all distribution files

## Usage

### Running CI Locally

To test the build and test process locally before pushing:

```bash
# Navigate to the project directory
cd tesseract_nanobind_benchmark

# Install dependencies
pip install -e .

# Run tests
pytest tests/ -v

# Run benchmarks
python benchmarks/compare_all.py
```

### Triggering Manual Workflows

1. Go to the Actions tab in GitHub
2. Select the workflow (e.g., "Tesseract Nanobind CI")
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

### Creating a Release

To create a release with built wheels:

```bash
# Tag the release
git tag tesseract-nanobind-v0.1.0
git push origin tesseract-nanobind-v0.1.0
```

This will automatically trigger the wheel building workflow and create a GitHub release.

## Badges

Add these badges to your README.md:

```markdown
[![Tesseract Nanobind CI](https://github.com/hironow/Coders/actions/workflows/tesseract-nanobind-ci.yml/badge.svg)](https://github.com/hironow/Coders/actions/workflows/tesseract-nanobind-ci.yml)
[![Build Wheels](https://github.com/hironow/Coders/actions/workflows/tesseract-nanobind-build-wheels.yml/badge.svg)](https://github.com/hironow/Coders/actions/workflows/tesseract-nanobind-build-wheels.yml)
```

## Dependencies

### System Dependencies
- **Tesseract OCR**: OCR engine
- **Leptonica**: Image processing library
- **CMake**: Build system
- **pkg-config**: Library configuration

### Python Dependencies
- **pytest**: Testing framework
- **pillow**: Image processing
- **numpy**: Array operations
- **pytesseract**: (benchmark only)
- **tesserocr**: (compatibility test and benchmark only)

## Troubleshooting

### Build Failures

If builds fail due to missing dependencies:

1. **Ubuntu**: Ensure `tesseract-ocr`, `libtesseract-dev`, and `libleptonica-dev` are installed
2. **macOS**: Ensure `tesseract` and `leptonica` are installed via Homebrew
3. **CMake**: Verify CMake >= 3.15 is available

### Test Failures

If tests fail:

1. Check that all dependencies are installed correctly
2. Verify Tesseract language data is available (eng.traineddata)
3. Review test output for specific failure reasons

### Coverage Upload

Coverage is only uploaded from:
- Ubuntu latest
- Python 3.11
- Main CI workflow

If coverage upload fails, it won't fail the entire CI run (set to non-blocking).
