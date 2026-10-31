#!/usr/bin/env bash
# ==============================================================================
# Android Optimizer Production Harness - Rootless Performance Script
# Ahead-Of-Time (AOT) Dexopt, Skia/Vulkan Acceleration & UI Tuning
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CACHE_DIR="$PROJECT_ROOT/cache"
mkdir -p "$CACHE_DIR"

echo "=== 1. Checking ADB Device Connection & Pre-Flight Diagnostics ==="
if ! command -v adb &> /dev/null; then
    echo "Error: adb command not found in PATH."
    exit 1
fi

device_count=$(adb devices | grep -v "List" | grep "device$" | wc -l)
if [ "$device_count" -eq 0 ]; then
    echo "Error: No active Android device found via ADB. Please check USB debugging."
    exit 1
fi

MANUFACTURER=$(adb shell getprop ro.product.manufacturer | tr -d '\r')
MODEL=$(adb shell getprop ro.product.model | tr -d '\r')
SDK_VER=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
RELEASE_VER=$(adb shell getprop ro.build.version.release | tr -d '\r')

echo "Connected Target: $MANUFACTURER $MODEL (Android $RELEASE_VER, SDK $SDK_VER)"

# Pre-flight Battery & Thermal Telemetry Inspection
BATTERY_INFO=$(adb shell dumpsys battery)
BATT_TEMP=$(echo "$BATTERY_INFO" | grep "temperature:" | awk '{print $2}' | tr -d '\r')
BATT_LEVEL=$(echo "$BATTERY_INFO" | grep "level:" | awk '{print $2}' | tr -d '\r')

echo "Battery Telemetry: Level=${BATT_LEVEL}%, Temperature=$(awk "BEGIN {print $BATT_TEMP/10}")°C"

# Emergency Red Flag Interceptor Gate
if [ -n "$BATT_TEMP" ] && [ "$BATT_TEMP" -ge 480 ]; then
    echo "🚨 CRITICAL RED FLAG INTERCEPT: Battery temperature is $(awk "BEGIN {print $BATT_TEMP/10}")°C (>= 48.0°C). Aborting execution to prevent thermal damage."
    exit 1
fi

if [ -n "$BATT_LEVEL" ] && [ "$BATT_LEVEL" -le 15 ]; then
    echo "⚠️ LOW BATTERY WARNING: Battery is at ${BATT_LEVEL}% (<= 15%). Compiling now risks sudden shutdown. Aborting."
    exit 1
fi

echo "=== 2. Tuning UI Responsiveness & Hardware Acceleration ==="
# Animation scales to 0.5x
adb shell settings put global window_animation_scale 0.5
adb shell settings put global transition_animation_scale 0.5
adb shell settings put global animator_duration_scale 0.5

# Touch & scrolling responsiveness
adb shell settings put system view.scroll_friction 0.008 2>/dev/null || true

# Skia Vulkan hardware rendering (Android 10+)
if [ "$SDK_VER" -ge 29 ]; then
    adb shell setprop debug.hwui.renderer skiavk 2>/dev/null || true
    echo "Hardware renderer configured: skiavk (Vulkan backend)."
fi

echo "=== 3. Adjusting Background & Phantom Process Limits ==="
if [ "$SDK_VER" -ge 31 ]; then
    adb shell settings put global max_phantom_processes 2147483647
    echo "Phantom process limit raised for Android 12+ (SDK $SDK_VER)."
else
    echo "Skipping max_phantom_processes (Device is below Android 12)."
fi

echo "=== 4. Executing ART Speed-Profile Ahead-Of-Time (AOT) Dexopt ==="
echo "Compiling hot methods for active applications..."
adb shell cmd package compile -m speed-profile -a

echo "=== 5. Trimming RAM Caches & Resetting Stats ==="
adb shell pm trim-caches 999G 2>/dev/null || true
adb shell dumpsys batterystats --reset 2>/dev/null || true

# Record state to log
echo "$(date '+%Y-%m-%d %H:%M:%S') | Optimizer applied successfully to $MANUFACTURER $MODEL" >> "$CACHE_DIR/optimizer_runs.log"

echo "=== Done! Production rootless device optimization completed successfully. ==="
