---
name: diagnose-android-thermal
description: Evidence-based Android thermal diagnostics, idle heat inspection, battery overheating alarms, and throttling attribution skill using read-only ADB commands.
compatibility: Android 8+ (API Level 26+)
category: diagnostics
author: Android Optimizer Production Harness
---

# Android Thermal Diagnostics & Safety Stop Skill

This skill diagnoses abnormal heat and battery drain with read-only ADB evidence before proposing any intervention. It incorporates the safety stop protocols from `diagnose-android-overheating`.

## 1. Safety Stop Conditions

> **STOP IMMEDIATELY IF**:
> - Device battery temperature is $\ge 48.0^\circ\text{C}$ (reported as $\ge 480$ by dumpsys battery)
> - Physical device shows battery swelling, unusual odors, or hot spots near the charging port
> - Disconnect charger immediately and place on a non-conductive, fire-safe surface.

## 2. Read-Only Baseline Capture

Never reset batterystats or force-stop apps before capturing initial telemetry:

```bash
# Capture battery telemetry (temperature, voltage, level, status)
adb shell dumpsys battery

# Capture thermal service throttling status
adb shell dumpsys thermalservice

# Capture top 15 CPU consuming processes
adb shell dumpsys cpuinfo | head -n 20

# Check device uptime and load averages
adb shell uptime
```

## 3. Thermal Throttling Severity Matrix

| Severity Level | Integer Value | Operating Status | Harness Action |
| :--- | :--- | :--- | :--- |
| **NONE** | 0 | Normal operating temperatures | All optimizations permitted |
| **LIGHT** | 1 | Minimal frequency throttling | Monitor temperature trend |
| **MODERATE** | 2 | Visible CPU/GPU downclocking | Throttle background compilations |
| **SEVERE** | 3 | High throttling, frame drops | Defer Dexopt, prohibit GPU overclock |
| **CRITICAL** | 4 | Imminent shutdown risk | **Emergency Red Flag Escalation** |
| **EMERGENCY**| 5 | Shutdown in progress | Hardware safety stop |

## 4. Multi-Signal Thermal Attribution

Correlate at least two independent telemetry signals before concluding the root cause:
- Rising battery temp + persistent process CPU $\rightarrow$ Runaway background app / rogue thread.
- Rising battery temp + high charging current $\rightarrow$ Fast charging heat (normal; compare unplugged).
- Throttling during cellular data in low signal $\rightarrow$ Modem transmission power escalation.
- Thermal severity spike after Dexopt compilation $\rightarrow$ AOT compilation load (will cool after finish).
