#!/usr/bin/env bash
# ==============================================================================
# Android Optimizer Production Harness - Safe Multi-OEM Debloater
# Target: User 0 (pm uninstall -k --user 0) with Backup Manifest Logging
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LIST_FILE="$PROJECT_ROOT/data/debloat_list.txt"
CACHE_DIR="$PROJECT_ROOT/cache"
MANIFEST_FILE="$CACHE_DIR/debloated_manifest.log"
mkdir -p "$CACHE_DIR"

if [ ! -f "$LIST_FILE" ]; then
    echo "Error: debloat_list.txt not found at $LIST_FILE!"
    exit 1
fi

echo "=== 1. Checking ADB Device Connection & Specs ==="
if ! command -v adb &> /dev/null; then
    echo "Error: adb command not found in PATH."
    exit 1
fi

device_count=$(adb devices | grep -v "List" | grep "device$" | wc -l)
if [ "$device_count" -eq 0 ]; then
    echo "Error: No active Android device found via ADB."
    exit 1
fi

MANUFACTURER=$(adb shell getprop ro.product.manufacturer | tr -d '\r' | tr '[:upper:]' '[:lower:]')
BRAND=$(adb shell getprop ro.product.brand | tr -d '\r' | tr '[:upper:]' '[:lower:]')
MODEL=$(adb shell getprop ro.product.model | tr -d '\r')
echo "Target Device: $MANUFACTURER ($BRAND) Model: $MODEL"

echo "=== 2. Backing up Existing Package Baseline ==="
adb shell pm list packages -u > "$CACHE_DIR/packages_baseline.txt"
echo "Package baseline stored in $CACHE_DIR/packages_baseline.txt"

echo "=== 3. Executing Safe Debloat for User 0 ==="
DEBLOAT_COUNT=0

while IFS= read -r line || [ -n "$line" ]; do
    pkg=$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
    [[ -z "$pkg" || "$pkg" =~ ^# ]] && continue

    # Critical Framework Protection Gate
    if [[ "$pkg" == "com.android.systemui" || "$pkg" == "com.android.settings" || "$pkg" == "com.android.phone" || "$pkg" == "com.android.keyguard" ]]; then
        echo "Safety Gate: Skipping critical framework package $pkg"
        continue
    fi

    # Smart Vendor Filter
    if [[ "$pkg" == com.samsung.* || "$pkg" == com.sec.* ]]; then
        [[ "$MANUFACTURER" != *"samsung"* ]] && continue
    elif [[ "$pkg" == com.miui.* || "$pkg" == com.xiaomi.* ]]; then
        [[ "$MANUFACTURER" != *"xiaomi"* && "$BRAND" != *"poco"* && "$BRAND" != *"redmi"* ]] && continue
    elif [[ "$pkg" == com.heytap.* || "$pkg" == com.coloros.* || "$pkg" == com.oppo.* || "$pkg" == com.oplus.* || "$pkg" == com.nearme.* ]]; then
        [[ "$MANUFACTURER" != *"oppo"* && "$MANUFACTURER" != *"realme"* && "$MANUFACTURER" != *"oneplus"* ]] && continue
    elif [[ "$pkg" == com.vivo.* || "$pkg" == com.bbk.* || "$pkg" == com.iqoo.* ]]; then
        [[ "$MANUFACTURER" != *"vivo"* && "$BRAND" != *"iqoo"* ]] && continue
    elif [[ "$pkg" == com.huawei.* || "$pkg" == com.hihonor.* ]]; then
        [[ "$MANUFACTURER" != *"huawei"* && "$MANUFACTURER" != *"honor"* ]] && continue
    elif [[ "$pkg" == com.motorola.* || "$pkg" == com.lenovo.* ]]; then
        [[ "$MANUFACTURER" != *"motorola"* && "$MANUFACTURER" != *"lenovo"* ]] && continue
    elif [[ "$pkg" == com.transsion.* ]]; then
        [[ "$MANUFACTURER" != *"transsion"* && "$MANUFACTURER" != *"tecno"* && "$MANUFACTURER" != *"infinix"* && "$MANUFACTURER" != *"itel"* ]] && continue
    fi

    # Check if installed
    if adb shell pm list packages | grep -q "^package:$pkg$"; then
        echo "Debloating [User 0]: $pkg"
        adb shell pm uninstall -k --user 0 "$pkg" >/dev/null 2>&1 || true
        echo "$pkg" >> "$MANIFEST_FILE"
        DEBLOAT_COUNT=$((DEBLOAT_COUNT + 1))
    fi
done < "$LIST_FILE"

echo "=== Done! Safely debloated $DEBLOAT_COUNT packages for User 0. ==="
echo "Manifest of removed packages saved to: $MANIFEST_FILE"
echo "To restore all packages at any time, run: make restore"
