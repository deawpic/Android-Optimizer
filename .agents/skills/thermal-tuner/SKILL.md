---
name: thermal-tuner
description: Qualcomm Adreno / ARM Mali GPU tuning, thermal engine mitigation, and cooling device control skill with strict thermal safety guardrails.
compatibility: Rooted Android with Qualcomm Snapdragon or MediaTek SoC
category: hardware
author: Android Optimizer Production Harness
---

# Android GPU & Thermal Tuning Skill

This skill provides Qualcomm Adreno sysfs tuning and thermal throttling mitigation for rooted Android systems. It incorporates hardware parameter baselines from `crian/adreno-gpu-tweaks` and thermal safety guardrails from `diagnose-android-overheating`.

## 1. Safety Guardrail & Temperature Gate

> **CRITICAL RED FLAG WARNING**: Never disable thermal engines if battery temperature exceeds **45.0°C**. Doing so can result in hardware degradation, emergency shutdown, or thermal damage.

```bash
# Verify battery temperature before applying GPU or thermal tweaks
BATTERY_TEMP=$(adb shell dumpsys battery | grep "temperature" | awk '{print $2}')
# Temperature is reported in tenths of a degree Celsius (450 = 45.0°C)
if [ "$BATTERY_TEMP" -ge 450 ]; then
    echo "EMERGENCY INTERCEPT: Device is currently at $(awk "BEGIN {print $BATTERY_TEMP/10}")°C. Aborting thermal modifications."
    exit 1
fi
```

## 2. Qualcomm Adreno GPU Sysfs Tuning (KGSL Interface)

Tunes the Adreno GPU governor, bus frequency scaling, and clock power rail:

```bash
adb shell "su -c '
if [ -d /sys/class/kgsl/kgsl-3d0 ]; then
    # Devfreq governor: msm-adreno-tz (Qualcomm dynamic trustzone governor)
    avail_gov=\$(cat /sys/class/kgsl/kgsl-3d0/devfreq/available_governors 2>/dev/null || true)
    if echo \$avail_gov | grep -q "msm-adreno-tz"; then
        echo msm-adreno-tz > /sys/class/kgsl/kgsl-3d0/devfreq/governor 2>/dev/null || true
    fi

    # Bus scaling optimization
    [ -f /sys/class/kgsl/kgsl-3d0/bus_split ] && echo 1 > /sys/class/kgsl/kgsl-3d0/bus_split 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/force_bus_on ] && echo 1 > /sys/class/kgsl/kgsl-3d0/force_bus_on 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/force_rail_on ] && echo 1 > /sys/class/kgsl/kgsl-3d0/force_rail_on 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/force_clk_on ] && echo 1 > /sys/class/kgsl/kgsl-3d0/force_clk_on 2>/dev/null || true

    # Idle timer (ms before GPU downclocks): 80ms provides smooth gaming without micro-stutter
    [ -f /sys/class/kgsl/kgsl-3d0/idle_timer ] && echo 80 > /sys/class/kgsl/kgsl-3d0/idle_timer 2>/dev/null || true

    # Set thermal power level to highest performance state (0 = Max freq allowed)
    [ -f /sys/class/kgsl/kgsl-3d0/thermal_pwrlevel ] && echo 0 > /sys/class/kgsl/kgsl-3d0/thermal_pwrlevel 2>/dev/null || true
fi
'"
```

## 3. ARM Mali GPU Tuning (MediaTek / Exynos)

```bash
adb shell "su -c '
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
```

## 4. Controlled Thermal Daemon Mitigation

```bash
adb shell "su -c '
# Stop aggressive OEM thermal limiters (Temporarily for benchmarks or heavy gaming)
stop thermal-engine 2>/dev/null || true
stop thermald 2>/dev/null || true
stop mi_thermald 2>/dev/null || true

# Reset cooling device states to 0 (unthrottled)
for cdev in /sys/class/thermal/cooling_device*; do
    cdev_type=\$(cat \$cdev/type 2>/dev/null || true)
    if echo \$cdev_type | grep -qiE "cpu|gpu|processor"; then
        [ -f \$cdev/cur_state ] && echo 0 > \$cdev/cur_state 2>/dev/null || true
    fi
done
'"
```

## 5. Rollback & Thermal Restitution

Immediately re-engages factory thermal throttling daemons:

```bash
adb shell "su -c '
start thermal-engine 2>/dev/null || true
start thermald 2>/dev/null || true
start mi_thermald 2>/dev/null || true

for zone in /sys/class/thermal/thermal_zone*; do
    [ -f \$zone/mode ] && echo enabled > \$zone/mode 2>/dev/null || true
done

[ -f /sys/class/kgsl/kgsl-3d0/force_bus_on ] && echo 0 > /sys/class/kgsl/kgsl-3d0/force_bus_on 2>/dev/null || true
[ -f /sys/class/kgsl/kgsl-3d0/force_clk_on ] && echo 0 > /sys/class/kgsl/kgsl-3d0/force_clk_on 2>/dev/null || true
'"
```
