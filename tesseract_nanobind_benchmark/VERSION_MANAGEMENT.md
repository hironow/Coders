# Version Management

This document describes the version management strategy for tesseract_nanobind.

## Version Strategy

We use **semantic versioning** (major.minor.patch) with **static version management** in `pyproject.toml`.

### Why Static Management?

- ✅ Simple and explicit - version is visible in `pyproject.toml`
- ✅ No additional dependencies or build-time magic
- ✅ Works perfectly with `scikit-build-core` (our build backend)
- ✅ Easy to automate with justfile commands

Reference: This approach is recommended for projects using `scikit-build-core`, which focuses on CMake/C++ builds and doesn't include dynamic versioning features.

## Version Management Commands

All version management is handled through justfile commands:

### Check Current Version

```bash
just tesseract-version
```

Output: `0.1.0`

### Bump Version

#### Patch Version (Bug fixes)
```bash
just tesseract-version-bump-patch
# 0.1.0 -> 0.1.1
```

#### Minor Version (New features, backward compatible)
```bash
just tesseract-version-bump-minor
# 0.1.0 -> 0.2.0
```

#### Major Version (Breaking changes)
```bash
just tesseract-version-bump-major
# 0.1.0 -> 1.0.0
```

Each bump command will:
1. Update `pyproject.toml` with the new version
2. Create a git commit with message: `Bump version to X.Y.Z`

### Create Release Tag

After bumping the version and ensuring all tests pass:

```bash
just tesseract-release
```

This will:
1. Read the current version from `pyproject.toml`
2. Create an annotated git tag: `tesseract-nanobind-vX.Y.Z`
3. Display instructions for pushing the tag

### Push Release

```bash
# Push specific tag
git push origin tesseract-nanobind-v0.1.0

# Or push all tags
git push --tags
```

## Release Workflow

### Standard Release Process

1. **Ensure clean state**
   ```bash
   git status  # Should be clean
   just tesseract-test  # All tests should pass
   just tesseract-check  # No lint errors
   ```

2. **Bump version**
   ```bash
   # Choose appropriate bump level
   just tesseract-version-bump-patch  # or minor/major
   ```

3. **Verify the change**
   ```bash
   just tesseract-version
   git log -1
   ```

4. **Create release tag**
   ```bash
   just tesseract-release
   ```

5. **Push to GitHub**
   ```bash
   # Push commits
   git push

   # Push tag (triggers wheel build workflow)
   git push origin tesseract-nanobind-v0.1.0
   ```

6. **GitHub Actions will automatically:**
   - Build wheels for multiple Python versions
   - Build source distribution (sdist)
   - Create GitHub Release with artifacts

## Integration with GitHub Actions

### CI Workflow (`tesseract-nanobind-ci.yaml`)
- Runs on every push to `main`/`develop`
- Tests all supported Python versions
- No version-specific logic

### Build Wheels Workflow (`tesseract-nanobind-build-wheels.yaml`)
- **Triggered by:** Tags matching `tesseract-nanobind-v*`
- Builds wheels for Linux and macOS
- Creates GitHub Release with downloadable artifacts

## Version File Locations

- **Source of Truth:** `tesseract_nanobind_benchmark/pyproject.toml`
- **Format:** `version = "X.Y.Z"` (line 7)

## Integration with uv and uv.lock

### Important Note

`uv.lock` does **not** manage the version in `pyproject.toml`. The lock file is for:
- Development dependencies (pytest, ruff, etc.)
- Runtime dependencies (numpy, pillow)

The build system dependencies (`scikit-build-core`, `nanobind`) are managed separately during the build process.

### Development Workflow with uv

```bash
# Setup environment
uv sync --all-extras

# Build and install in editable mode
just tesseract-build

# Run tests
just tesseract-test
```

## Troubleshooting

### "Tag already exists"
```bash
# List existing tags
git tag -l "tesseract-nanobind-v*"

# Delete local tag
git tag -d tesseract-nanobind-vX.Y.Z

# Delete remote tag (use with caution!)
git push origin :refs/tags/tesseract-nanobind-vX.Y.Z
```

### "Version not updated in build"
After bumping version, rebuild:
```bash
just tesseract-clean
just tesseract-build
```

### "Wrong version in wheel filename"
The wheel filename is generated from `pyproject.toml` at build time. If it's wrong:
1. Check `just tesseract-version`
2. Ensure `pyproject.toml` was committed
3. Rebuild: `just tesseract-clean && just tesseract-build`

## Future Improvements

Potential enhancements for later:

1. **Automated Changelog Generation**
   - Use git commits to generate CHANGELOG.md
   - Tools: `git-cliff`, `standard-version`

2. **Pre-release Versions**
   - Add support for alpha/beta/rc versions
   - Format: `0.2.0-alpha.1`

3. **CI-driven Releases**
   - Automatic version bump on merge to main
   - Requires careful workflow design

For now, manual version management provides maximum control and clarity.
