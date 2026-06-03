#!/usr/bin/env bash
# Run the full test suite against a v1-schema (pre-migration) database
# so the app's auto-migration code is exercised on every table.
#
# Usage:
#   bash scripts/run_tests_with_migration.sh
#
# This sets TEST_LEGACY_DB=1 so conftest.py creates a v1 database
# (REAL credit columns, no settings table) before each test fixture.
# The app then runs migration_2 on startup, testing the full path.

set -euo pipefail

cd "$(git rev-parse --show-toplevel 2>/dev/null || echo "$(dirname "$0")/..")"

echo "=== Running test suite with v1 → v2 migration ==="
echo ""

TEST_LEGACY_DB=1 python -m pytest GuiApp/tests/ -v "$@"
