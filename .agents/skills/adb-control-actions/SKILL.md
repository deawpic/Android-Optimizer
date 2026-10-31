---
name: adb-control-actions
description: Comprehensive ADB Android Control skill definition and command actions covering device inputs, dumpsys introspection, am/pm intent management, screenshot capture, and wireless ADB.
compatibility: Android 7+ (API Level 24+)
category: control
author: Android Optimizer Production Harness
---

# Android ADB Device Control & Inspection Skill

This skill defines standardized ADB actions for programmatically inspecting, manipulating, and controlling connected Android devices and Termux environments.

## 1. Device Interception & Hardware Inputs

```bash
# Tap coordinate (X, Y)
adb shell input tap <x> <y>

# Swipe / Scroll (startX startY endX endY duration_ms)
adb shell input swipe 500 1500 500 500 300

# Text input (Note: Escape special characters or spaces with %s)
adb shell input text "Hello%sAndroid"

# Hardware Keyevents
adb shell input keyevent 3    # HOME
adb shell input keyevent 4    # BACK
adb shell input keyevent 26   # POWER (Screen Toggle)
adb shell input keyevent 224  # WAKEUP
adb shell input keyevent 82   # MENU / UNLOCK
```

## 2. Display Capture & Screen Inspection

```bash
# Screen capture to local disk
adb exec-out screencap -p > ./output/screen_capture.png

# Retrieve display resolution and density
adb shell wm size
adb shell wm density
```

## 3. Package & Activity Management

```bash
# Launch app by package name or explicit intent
adb shell monkey -p <package_name> -c android.intent.category.LAUNCHER 1
# or direct activity
adb shell am start -n <package_name>/<activity_name>

# Force stop application
adb shell am force-stop <package_name>

# Clear application cache and user data
adb shell pm clear <package_name>

# Grant runtime permissions
adb shell pm grant <package_name> android.permission.WRITE_EXTERNAL_STORAGE
```

## 4. Deep System Introspection (`dumpsys`)

```bash
# Battery statistics and health
adb shell dumpsys battery

# Thermal status & throttling sensor list
adb shell dumpsys thermalservice

# CPU utilization per process
adb shell dumpsys cpuinfo | head -n 25

# RAM memory distribution
adb shell dumpsys meminfo --summary <package_name>

# Window hierarchy and current foreground activity
adb shell dumpsys window | grep -E "mCurrentFocus|mFocusedApp"
```

## 5. Wireless ADB & Port Forwarding

```bash
# Enable TCP/IP on port 5555
adb tcpip 5555

# Connect over Wi-Fi
adb connect <device_ip>:5555

# Forward local port to device port
adb forward tcp:8080 tcp:8080
```
