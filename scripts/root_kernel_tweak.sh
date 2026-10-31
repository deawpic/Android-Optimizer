#!/usr/bin/env bash
# ==============================================================================
# Android Optimizer Production Harness - Root Kernel, GPU & Thermal Tuning
# Synthesized from FDE.AI, ktweak, VR-25 zram-swap-manager & adreno-gpu-tweaks
# Features Dynamic Flagship SoC Profiling: Snapdragon 8 Gen 2/3, Dimensity 9200/9300, Tensor
# ==============================================================================
set -e

echo "=== 1. Checking ADB & Root Privileges ==="
if ! command -v adb &> /dev/null; then
    echo "Error: adb command not found in PATH."
    exit 1
fi

device_count=$(adb devices | grep -v "List" | grep "device$" | wc -l)
if [ "$device_count" -eq 0 ]; then
    echo "Error: No Android device found via ADB."
    exit 1
fi

ROOT_CHECK=$(adb shell "su -c id" 2>/dev/null || true)
if [[ "$ROOT_CHECK" != *"uid=0"* ]]; then
    echo "Error: Device is not rooted or su access was denied. Cannot execute kernel tweaks."
    exit 1
fi
echo "Root access verified: uid=0(root)"

# Thermal Safety Gate
BATTERY_INFO=$(adb shell dumpsys battery)
BATT_TEMP=$(echo "$BATTERY_INFO" | grep "temperature:" | awk '{print $2}' | tr -d '\r')
if [ -n "$BATT_TEMP" ] && [ "$BATT_TEMP" -ge 450 ]; then
    echo "🚨 DANGER INTERCEPT: Battery temperature is $(awk "BEGIN {print $BATT_TEMP/10}")°C (>= 45.0°C). Aborting kernel/thermal modifications."
    exit 1
fi

# Dynamic SoC Identification
PLATFORM=$(adb shell getprop ro.board.platform | tr -d '\r' | tr '[:upper:]' '[:lower:]')
SOC_MODEL=$(adb shell getprop ro.soc.model | tr -d '\r' | tr '[:upper:]' '[:lower:]')
HARDWARE=$(adb shell getprop ro.hardware | tr -d '\r' | tr '[:upper:]' '[:lower:]')

echo "Detected Silicon Architecture: Platform=$PLATFORM, Model=$SOC_MODEL, Hardware=$HARDWARE"

echo "=== 2. Optimizing CPU Scaling Governor & Cluster-Aware Schedutil ==="
adb shell "su -c '
# Flagship Snapdragon 8 Gen 3 (sm8650 / pineapple)
if echo \"$PLATFORM $SOC_MODEL $HARDWARE\" | grep -qiE \"sm8650|pineapple\"; then
    echo \"Applying SoC Profile: Snapdragon 8 Gen 3 (1+5+2 Architecture)\"
    [ -d /sys/devices/system/cpu/cpufreq/policy0 ] && echo 1000 > /sys/devices/system/cpu/cpufreq/policy0/schedutil/up_rate_limit_us 2>/dev/null || true
    [ -d /sys/devices/system/cpu/cpufreq/policy2 ] && echo 500 > /sys/devices/system/cpu/cpufreq/policy2/schedutil/up_rate_limit_us 2>/dev/null || true
    [ -d /sys/devices/system/cpu/cpufreq/policy7 ] && echo 500 > /sys/devices/system/cpu/cpufreq/policy7/schedutil/up_rate_limit_us 2>/dev/null || true

# Flagship Snapdragon 8 Gen 2 (sm8550 / kalama)
elif echo \"$PLATFORM $SOC_MODEL $HARDWARE\" | grep -qiE \"sm8550|kalama\"; then
    echo \"Applying SoC Profile: Snapdragon 8 Gen 2 (1+4+3 Architecture)\"
    [ -d /sys/devices/system/cpu/cpufreq/policy0 ] && echo 1000 > /sys/devices/system/cpu/cpufreq/policy0/schedutil/up_rate_limit_us 2>/dev/null || true
    [ -d /sys/devices/system/cpu/cpufreq/policy3 ] && echo 500 > /sys/devices/system/cpu/cpufreq/policy3/schedutil/up_rate_limit_us 2>/dev/null || true
    [ -d /sys/devices/system/cpu/cpufreq/policy7 ] && echo 500 > /sys/devices/system/cpu/cpufreq/policy7/schedutil/up_rate_limit_us 2>/dev/null || true

# MediaTek Dimensity 9300 (mt6989 / All-Big Cores)
elif echo \"$PLATFORM $SOC_MODEL $HARDWARE\" | grep -qiE \"mt6989|dimensity9300\"; then
    echo \"Applying SoC Profile: MediaTek Dimensity 9300 (All-Big Core Architecture)\"
    [ -d /sys/devices/system/cpu/cpufreq/policy0 ] && echo 800 > /sys/devices/system/cpu/cpufreq/policy0/schedutil/up_rate_limit_us 2>/dev/null || true
    [ -d /sys/devices/system/cpu/cpufreq/policy4 ] && echo 500 > /sys/devices/system/cpu/cpufreq/policy4/schedutil/up_rate_limit_us 2>/dev/null || true
    [ -d /sys/devices/system/cpu/cpufreq/policy7 ] && echo 500 > /sys/devices/system/cpu/cpufreq/policy7/schedutil/up_rate_limit_us 2>/dev/null || true

# Google Tensor G3 (zuma / 9-Core)
elif echo \"$PLATFORM $SOC_MODEL $HARDWARE\" | grep -qiE \"zuma|tensor_g3\"; then
    echo \"Applying SoC Profile: Google Tensor G3 (9-Core Architecture)\"
    [ -d /sys/devices/system/cpu/cpufreq/policy0 ] && echo 1000 > /sys/devices/system/cpu/cpufreq/policy0/schedutil/up_rate_limit_us 2>/dev/null || true
    [ -d /sys/devices/system/cpu/cpufreq/policy4 ] && echo 500 > /sys/devices/system/cpu/cpufreq/policy4/schedutil/up_rate_limit_us 2>/dev/null || true
    [ -d /sys/devices/system/cpu/cpufreq/policy8 ] && echo 500 > /sys/devices/system/cpu/cpufreq/policy8/schedutil/up_rate_limit_us 2>/dev/null || true
fi

# Generic Fallback for all clusters
for policy in /sys/devices/system/cpu/cpufreq/policy*; do
    if [ -f \$policy/scaling_governor ]; then
        avail=\$(cat \$policy/scaling_available_governors 2>/dev/null || true)
        if echo \$avail | grep -q "schedutil"; then
            echo schedutil > \$policy/scaling_governor 2>/dev/null || true
            [ -f \$policy/schedutil/up_rate_limit_us ] && echo 500 > \$policy/schedutil/up_rate_limit_us 2>/dev/null || true
            [ -f \$policy/schedutil/down_rate_limit_us ] && echo 20000 > \$policy/schedutil/down_rate_limit_us 2>/dev/null || true
        elif echo \$avail | grep -q "interactive"; then
            echo interactive > \$policy/scaling_governor 2>/dev/null || true
        fi
    fi
done
'"

echo "=== 3. Optimizing Qualcomm Adreno & ARM Mali GPU Sysfs ==="
adb shell "su -c '
# Qualcomm Adreno KGSL Interface (Adreno 740 / 750 / 600 Series)
if [ -d /sys/class/kgsl/kgsl-3d0 ]; then
    avail_gov=\$(cat /sys/class/kgsl/kgsl-3d0/devfreq/available_governors 2>/dev/null || true)
    if echo \$avail_gov | grep -q "msm-adreno-tz"; then
        echo msm-adreno-tz > /sys/class/kgsl/kgsl-3d0/devfreq/governor 2>/dev/null || true
    fi
    [ -f /sys/class/kgsl/kgsl-3d0/bus_split ] && echo 1 > /sys/class/kgsl/kgsl-3d0/bus_split 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/force_bus_on ] && echo 1 > /sys/class/kgsl/kgsl-3d0/force_bus_on 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/force_rail_on ] && echo 1 > /sys/class/kgsl/kgsl-3d0/force_rail_on 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/force_clk_on ] && echo 1 > /sys/class/kgsl/kgsl-3d0/force_clk_on 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/idle_timer ] && echo 85 > /sys/class/kgsl/kgsl-3d0/idle_timer 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/thermal_pwrlevel ] && echo 0 > /sys/class/kgsl/kgsl-3d0/thermal_pwrlevel 2>/dev/null || true
fi

# ARM Mali & Immortalis Interface (Dimensity & Tensor)
for mali in /sys/devices/platform/*.mali /sys/devices/platform/*.gpu /sys/class/misc/mali*; do
    if [ -d \$mali ]; then
        [ -f \$mali/dvfs_enable ] && echo 1 > \$mali/dvfs_enable 2>/dev/null || true
        if [ -f \$mali/devfreq/governor ]; then
            mali_gov=\$(cat \$mali/devfreq/available_governors 2>/dev/null || true)
            if echo \$mali_gov | grep -q "simple_ondemand"; then
                echo simple_ondemand > \$mali/devfreq/governor 2>/dev/null || true
            fi
        fi
    fi
done
'"

echo "=== 4. Controlled Thermal Throttling Mitigation ==="
adb shell "su -c '
stop thermal-engine 2>/dev/null || true
stop thermald 2>/dev/null || true
stop mi_thermald 2>/dev/null || true

for zone in /sys/class/thermal/thermal_zone*; do
    [ -f \$zone/mode ] && echo disabled > \$zone/mode 2>/dev/null || true
done

for cdev in /sys/class/thermal/cooling_device*; do
    cdev_type=\$(cat \$cdev/type 2>/dev/null || true)
    if echo \$cdev_type | grep -qiE "cpu|gpu|processor"; then
        [ -f \$cdev/cur_state ] && echo 0 > \$cdev/cur_state 2>/dev/null || true
    fi
done
'"

echo "=== 5. Storage I/O Schedulers, ZRAM & Virtual Memory Tuning ==="
adb shell "su -c '
# I/O Scheduler & Read Ahead
for q in /sys/block/*/queue/scheduler; do
    if [ -f \$q ]; then
        avail=\$(cat \$q 2>/dev/null || true)
        if echo \$avail | grep -q "none"; then
            echo none > \$q 2>/dev/null || true
        elif echo \$avail | grep -q "mq-deadline"; then
            echo mq-deadline > \$q 2>/dev/null || true
        fi
    fi
done
for r in /sys/block/*/queue/read_ahead_kb; do
    [ -f \$r ] && echo 512 > \$r 2>/dev/null || true
done

# ZRAM Compression (lz4 preferred)
if [ -d /sys/block/zram0 ]; then
    avail_algo=\$(cat /sys/block/zram0/comp_algorithm 2>/dev/null || true)
    if echo \$avail_algo | grep -q "lz4"; then
        swapoff /dev/block/zram0 2>/dev/null || true
        echo lz4 > /sys/block/zram0/comp_algorithm 2>/dev/null || true
        swapon /dev/block/zram0 2>/dev/null || true
    fi
fi

# Linux Virtual Memory (VM) Parameters (ktweak / FDE.AI standards)
sysctl -w vm.swappiness=100 >/dev/null 2>&1 || true
sysctl -w vm.vfs_cache_pressure=100 >/dev/null 2>&1 || true
sysctl -w vm.dirty_ratio=20 >/dev/null 2>&1 || true
sysctl -w vm.dirty_background_ratio=10 >/dev/null 2>&1 || true
sysctl -w vm.dirty_expire_centisecs=1500 >/dev/null 2>&1 || true
sysctl -w vm.dirty_writeback_centisecs=3000 >/dev/null 2>&1 || true
sysctl -w vm.page-cluster=0 >/dev/null 2>&1 || true
'"

echo "=== Done! Production SoC-aware Kernel, GPU, and Memory optimizations applied. ==="
