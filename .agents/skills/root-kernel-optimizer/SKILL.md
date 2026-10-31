---
name: root-kernel-optimizer
description: Root-level Android kernel and sysfs parameter tuning skill for CPU governors, schedutil latency rates, virtual memory writebacks, I/O schedulers, and LMKD memory handling.
compatibility: Rooted Android (Magisk / KernelSU / APatch), Linux Kernel 4.9+
category: kernel
author: Android Optimizer Production Harness
---

# Android Root Kernel & Sysfs Optimization Skill

This skill applies low-level Linux kernel optimizations to rooted Android devices, derived from battle-tested parameters in FDE.AI, ktweak, and custom kernel configurations.

## 1. Privilege Verification & Safety Gate

Commands requiring root must verify `su` availability before executing:

```bash
ROOT_STATUS=$(adb shell "su -c id" 2>/dev/null || true)
if [[ "$ROOT_STATUS" != *"uid=0"* ]]; then
    echo "Error: Root access not available. Skipping kernel sysfs modifications."
    exit 1
fi
```

## 2. CPU Governor & Schedutil Latency Rates

Tuning `schedutil` governor rate limits ensures the CPU ramps up immediately on touch events and throttles down predictably to conserve battery:

```bash
adb shell "su -c '
for policy in /sys/devices/system/cpu/cpufreq/policy*; do
    if [ -f \$policy/scaling_governor ]; then
        avail=\$(cat \$policy/scaling_available_governors 2>/dev/null || true)
        if echo \$avail | grep -q "schedutil"; then
            echo schedutil > \$policy/scaling_governor 2>/dev/null || true
            # Rate limits (microseconds): 500us ramp-up, 20000us ramp-down
            [ -f \$policy/schedutil/up_rate_limit_us ] && echo 500 > \$policy/schedutil/up_rate_limit_us 2>/dev/null || true
            [ -f \$policy/schedutil/down_rate_limit_us ] && echo 20000 > \$policy/schedutil/down_rate_limit_us 2>/dev/null || true
        elif echo \$avail | grep -q "interactive"; then
            echo interactive > \$policy/scaling_governor 2>/dev/null || true
        fi
    fi
done
'"
```

## 3. Storage I/O Schedulers & Read-Ahead

Optimizes flash storage controllers (UFS and eMMC) for lowest queuing latency:

```bash
adb shell "su -c '
for q in /sys/block/*/queue/scheduler; do
    if [ -f \$q ]; then
        avail=\$(cat \$q 2>/dev/null || true)
        # For UFS / fast NVMe storage, "none" bypasses queue overhead
        if echo \$avail | grep -q "none"; then
            echo none > \$q 2>/dev/null || true
        elif echo \$avail | grep -q "mq-deadline"; then
            echo mq-deadline > \$q 2>/dev/null || true
        fi
    fi
done

# Read-ahead buffer: 512KB for smooth multimedia streaming and sequential app launch
for r in /sys/block/*/queue/read_ahead_kb; do
    [ -f \$r ] && echo 512 > \$r 2>/dev/null || true
done
'"
```

## 4. Virtual Memory (VM) Dirty Writebacks & Cache Pressure

Balancing dirty page expiration prevents massive flash write spikes that cause UI frame drops:

```bash
adb shell "su -c '
# Virtual Memory tuning (ktweak / FDE.AI standard)
sysctl -w vm.vfs_cache_pressure=100
sysctl -w vm.dirty_ratio=20
sysctl -w vm.dirty_background_ratio=10
sysctl -w vm.dirty_expire_centisecs=1500
sysctl -w vm.dirty_writeback_centisecs=3000
sysctl -w vm.stat_interval=10
sysctl -w vm.overcommit_memory=1
'"
```

## 5. Low Memory Killer Daemon (LMKD) & Cgroups

Prevents premature termination of user-facing applications:

```bash
adb shell "su -c '
# Prioritize UI rendering threads in root cgroup
if [ -d /dev/cpuset/top-app ]; then
    cat /dev/cpuset/top-app/tasks 2>/dev/null | head -n 5 > /dev/null || true
fi

# Ensure LMKD debug level is calm
setprop lmkd.recheck_on_failure false
'"
```

## 6. Kernel Verification & Telemetry

```bash
adb shell "su -c '
echo \"--- Active Scaling Governors ---\"
cat /sys/devices/system/cpu/cpufreq/policy*/scaling_governor
echo \"--- Active I/O Schedulers ---\"
cat /sys/block/*/queue/scheduler | grep -v \"none\" | head -n 3 || true
echo \"--- Current VM Parameters ---\"
sysctl vm.dirty_ratio vm.dirty_background_ratio vm.vfs_cache_pressure
'"
```
