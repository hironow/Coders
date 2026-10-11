# Handover

Last updated: 2026-10-11 (Asia/Tokyo)

## Current state

The native workflows use the official uv action and a SHA-pinned just installer.
Both CI-tested packages use locked uv environments with pinned ruff and ty.
The root `just check` builds both native extensions and runs formatting, lint,
types, Semgrep, and tests. No Flatt action or registry is needed.
Tesseract compatibility getters return integer, boolean, and double values
through one-argument native overloads. Existing two-argument overloads remain.

## Verification

Local `just check` passed with Python 3.11: Tesseract 166 passed;
PyGMT 104 passed, one existing unimplemented grid-input test skipped.
Ruff, ty, actionlint, and Semgrep reported no findings.
The three getter regression tests failed before the fix and pass after it.
CI covers Python 3.10 through 3.14. Wheel builds will be checked by manual workflow dispatch without publishing
a release.

## Next actions

Review the PR CI and wheel build results before squash merging.

## Context

GMT headers and its runtime library must match. Local Homebrew builds use
`GMT_INCLUDE_DIR=/opt/homebrew/include/gmt` and
`GMT_LIBRARY_DIR=/opt/homebrew/lib`. Build tasks reinstall the editable native
package to ensure C++ changes are compiled. MLT is outside this change.
