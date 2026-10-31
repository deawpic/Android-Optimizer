#!/usr/bin/env bash
# ==============================================================================
# Android Optimizer Production Harness - Universal State Rollback
# Restores all animations, AOT compilation, GPU/kernel parameters & apps
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== 1. Checking ADB Device Connection ==="
if ! command -v adb &> /dev/null; then
    echo "Error: adb command not found in PATH."
    exit 1
fi

device_count=$(adb devices | grep -v "List" | grep "device$" | wc -l)
if [ "$device_count" -eq 0 ]; then
    echo "Error: No Android device found via ADB."
    exit 1
fi

echo "=== 2. Reverting UI Animation Scales & Physics to 1.0x ==="
adb shell settings put global window_animation_scale 1.0
adb shell settings put global transition_animation_scale 1.0
adb shell settings put global animator_duration_scale 1.0
adb shell settings put system view.scroll_friction 0.015 2>/dev/null || true

echo "=== 3. Resetting Phantom Process Limit to Default (32) ==="
SDK_VER=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
if [ "$SDK_VER" -ge 31 ]; then
    adb shell settings put global max_phantom_processes 32
fi

echo "=== 4. Resetting Hardware Renderer & Doze State ==="
adb shell setprop debug.hwui.renderer "" 2>/dev/null || true
adb shell dumpsys deviceidle unforce 2>/dev/null || true

echo "=== 5. Resetting ART Compilation Profiles to Baseline ==="
echo "Resetting ART odex/vdex caches across all packages..."
adb shell cmd package compile --reset -a

echo "=== 6. Restoring All Debloated User-0 Packages ==="
if [ -f "$SCRIPT_DIR/restore_apps.sh" ]; then
    bash "$SCRIPT_DIR/restore_apps.sh"
fi

echo "=== 7. Restoring Kernel & Thermal Daemons (If Rooted) ==="
ROOT_CHECK=$(adb shell "su -c id" 2>/dev/null || true)
if [[ "$ROOT_CHECK" == *"uid=0"* ]]; then
    adb shell "su -c '
    start thermal-engine 2>/dev/null || true
    start thermald 2>/dev/null || true
    start mi_thermald 2>/dev/null || true

    for zone in /sys/class/thermal/thermal_zone*; do
        [ -f \$zone/mode ] && echo enabled > \$zone/mode 2>/dev/null || true
    done

    [ -f /sys/class/kgsl/kgsl-3d0/force_bus_on ] && echo 0 > /sys/class/kgsl/kgsl-3d0/force_bus_on 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/force_clk_on ] && echo 0 > /sys/class/kgsl/kgsl-3d0/force_clk_on 2>/dev/null || true

    sysctl -w vm.swappiness=60 >/dev/null 2>&1 || true
    sysctl -w vm.vfs_cache_pressure=100 >/dev/null 2>&1 || true
    sysctl -w vm.dirty_ratio=20 >/dev/null 2>&1 || true
    sysctl -w vm.dirty_background_ratio=10 >/dev/null 2>&1 || true
    '"
    echo "Thermal and kernel parameters returned to baseline."
fi

echo "=== Done! Device state successfully restored to factory defaults. ==="
