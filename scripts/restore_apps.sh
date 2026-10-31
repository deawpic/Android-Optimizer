#!/usr/bin/env bash
# ==============================================================================
# Android Optimizer Production Harness - App Reinstatement Engine
# Restores debloated User-0 packages via cmd package install-existing
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CACHE_DIR="$PROJECT_ROOT/cache"
MANIFEST_FILE="$CACHE_DIR/debloated_manifest.log"

if ! command -v adb &> /dev/null; then
    echo "Error: adb command not found in PATH."
    exit 1
fi

if [ -n "$1" ]; then
    echo "Restoring individual package: $1"
    adb shell cmd package install-existing "$1"
    echo "Package $1 reinstated successfully."
    exit 0
fi

if [ ! -f "$MANIFEST_FILE" ]; then
    echo "No debloat manifest found at $MANIFEST_FILE."
    echo "To restore a specific app manually, run: ./scripts/restore_apps.sh <package_name>"
    exit 0
fi

echo "=== Restoring packages from debloat manifest ($MANIFEST_FILE) ==="
RESTORED_COUNT=0

while IFS= read -r pkg || [ -n "$pkg" ]; do
    pkg=$(echo "$pkg" | tr -d '\r' | xargs)
    [ -z "$pkg" ] && continue
    echo "Reinstalling: $pkg"
    adb shell cmd package install-existing "$pkg" >/dev/null 2>&1 || true
    RESTORED_COUNT=$((RESTORED_COUNT + 1))
done < "$MANIFEST_FILE"

rm -f "$MANIFEST_FILE"
echo "=== Done! Successfully reinstated $RESTORED_COUNT packages for User 0. ==="
