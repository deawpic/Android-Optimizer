---
name: emulator-qa-testing
description: Android emulator automation, AVD lifecycle management, QA journey testing, monkey stress testing, and crash logcat analysis based on official Google Android Skills and emulator testbed specs.
compatibility: Android Virtual Devices (AVD), Android SDK 30+
category: testing
author: Android Optimizer Production Harness
---

# Android Emulator Automation & QA Testing Skill

This skill provides deterministic lifecycle control, automated test journey execution, and stress testing for Android Virtual Devices (AVD).

## 1. AVD Lifecycle Management

```bash
# List available Android Virtual Devices
emulator -list-avds

# Boot emulator in headless / no-window mode for CI/CD testbeds
emulator -avd <avd_name> -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect &

# Wait until emulator has finished booting
adb wait-for-device
while [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" != "1" ]; do
    sleep 2
done
echo "AVD Boot Completed Successfully."
```

## 2. Snapshot & State Restoration

```bash
# Save current running state to snapshot
adb emu avd snapshot save <snapshot_name>

# Restore emulator cleanly from snapshot
adb emu avd snapshot load <snapshot_name>
```

## 3. Automated Monkey Stress Testing

Fuzz-tests application UI with pseudorandom events to discover native crashes, ANRs (Application Not Responding), and memory leaks:

```bash
# Run 1000 random events on target application
adb shell monkey -p <package_name> \
    --throttle 100 \
    --pct-touch 60 \
    --pct-motion 20 \
    --pct-appswitch 10 \
    --ignore-crashes \
    --ignore-timeouts \
    1000
```

## 4. Crash Detection & Logcat Analysis

```bash
# Clear logcat buffers
adb logcat -c

# Filter only fatal crash tracebacks and ANRs
adb logcat -b crash -d > ./output/crash_report.log

# Check for ANR traces in data directory
adb shell "su -c 'ls -la /data/anr/'" 2>/dev/null || true
```

## 5. UI Hierarchy Dump for Verification

```bash
# Dump accessibility UI node hierarchy to XML
adb shell uiautomator dump /sdcard/window_dump.xml
adb pull /sdcard/window_dump.xml ./output/window_dump.xml
```
