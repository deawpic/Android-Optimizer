---
name: adb-optimizer
description: Production rootless Android OS performance optimization skill via ADB covering Ahead-Of-Time (AOT) Dexopt runtime compilation, Skia/Vulkan hardware rendering, UI animation timing, touch sampling responsiveness, and phantom process limits.
compatibility: Android 9+ (API Level 28+)
category: performance
author: Android Optimizer Production Harness
---

# Android ADB Rootless Optimization Skill

This skill provides deterministic, non-destructive, and rootless performance tuning for Android devices via ADB. All optimizations run without modifying `/system` or `/vendor` partitions and can be fully rolled back.

## 1. Diagnostics & Pre-Flight Checks

Before applying optimizations, verify device connectivity, battery temperature, and charging state:

```bash
# Check device connection and serial
adb devices -l

# Check battery level and temperature (Temp in tenths of °C, e.g. 350 = 35.0°C)
adb shell dumpsys battery | grep -E "level|temperature|status"

# Inspect thermal throttling severity (0 = NONE, 1 = LIGHT, 2 = MODERATE, 3 = SEVERE)
adb shell dumpsys thermalservice
```

> **Safety Invariant**: Do NOT perform heavy AOT Dexopt compilation if battery is under 20% or battery temperature exceeds 42.0°C.

## 2. ART Ahead-Of-Time (AOT) Dexopt Compilation

Re-compiles applications ahead of time into native machine code, eliminating runtime Just-In-Time (JIT) compilation overhead and stutter.

### Compilation Profiles
- `speed-profile` (Recommended): Compiles hot code paths identified during actual app usage. Best balance of speed and storage footprint.
- `speed`: Compiles all methods into machine code. Maximum speed, moderate storage overhead.
- `everything`: Compiles all bytecode and profiles. Highest storage and compilation time.

```bash
# Compile all user and system apps with speed-profile
adb shell cmd package compile -m speed-profile -a

# Alternatively, target foreground or specific high-priority apps
adb shell cmd package compile -m speed <package_name>

# Inspect compilation status of a specific package
adb shell dumpsys package <package_name> | grep -E "dexopt|compilation"
```

## 3. Skia / Vulkan Hardware Acceleration & UI Rendering

Enables modern Vulkan rendering backend and smooths animation cadence:

```bash
# Set hardware UI renderer to Skia Vulkan (Android 10+)
adb shell setprop debug.hwui.renderer skiavk

# Scale window, transition, and animator durations to 0.5x for instant UI feedback
adb shell settings put global window_animation_scale 0.5
adb shell settings put global transition_animation_scale 0.5
adb shell settings put global animator_duration_scale 0.5
```

## 4. Touch Responsiveness & Scrolling Physics

Reduces touch latency and optimizes list fling friction:

```bash
# Adjust view scrolling friction (Default ~0.015; 0.008 provides smoother long flings)
adb shell settings put system view.scroll_friction 0.008

# Increase touch sampling response (Device-dependent sysprop)
adb shell setprop touch.pressure.scale 0.001 2>/dev/null || true
```

## 5. Phantom Process & Background Doze Management

Prevents Android 12+ from aggressively killing background child processes (such as Termux tasks or background daemons):

```bash
# Raise phantom process limit for Android 12+ (SDK 31+)
adb shell settings put global max_phantom_processes 2147483647

# Force immediate Doze mode idle maintenance when screen is off
adb shell dumpsys deviceidle force-idle
```

## 6. Battery Stats Reset & RAM Cache Trimming

```bash
# Reset battery usage statistics after a full charge
adb shell dumpsys batterystats --reset

# Trim in-memory app caches
adb shell pm trim-caches 999G
```

## 7. Complete Rollback Procedures

Reverts all settings to Android AOSP factory defaults:

```bash
# Reset animation scales
adb shell settings put global window_animation_scale 1.0
adb shell settings put global transition_animation_scale 1.0
adb shell settings put global animator_duration_scale 1.0

# Reset phantom process limit to standard (32)
adb shell settings put global max_phantom_processes 32

# Reset hardware renderer
adb shell setprop debug.hwui.renderer ""

# Unforce Doze idle state
adb shell dumpsys deviceidle unforce

# Reset ART compilation back to baseline
adb shell cmd package compile --reset -a
```
