---
name: zram-swap-tuner
description: Kernel ZRAM swap compression, algorithm selection (lz4/zstd), memory swappiness, and page-cluster tuning based on VR-25/zram-swap-manager.
compatibility: Rooted Android (Magisk / KernelSU / APatch), Linux Kernel 4.4+
category: memory
author: Android Optimizer Production Harness
---

# Android ZRAM & Swap Management Skill

This skill configures compressed RAM swap (ZRAM) on rooted Android devices to extend usable memory and eliminate low-RAM app kills, based on the `VR-25/zram-swap-manager` architecture.

## 1. ZRAM Architecture & Algorithmic Comparison

| Algorithm | Compression Ratio | Decompression Speed | CPU Overhead | Recommended Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **lz4** | ~2.1x | ~3500 MB/s | Extremely Low | Mid-range to flagship gaming devices |
| **zstd** | ~2.7x | ~1200 MB/s | Moderate | Low-RAM devices (2GB-4GB) requiring maximum capacity |
| **lzo-rle** | ~2.0x | ~2500 MB/s | Low | Default fallback for older kernels |

## 2. Inspecting Current ZRAM State

```bash
adb shell "su -c '
echo \"--- ZRAM Block Device Status ---\"
cat /sys/block/zram0/comp_algorithm 2>/dev/null || true
cat /proc/swaps 2>/dev/null || true
cat /sys/block/zram0/disksize 2>/dev/null || true
'"
```

## 3. Dynamic ZRAM Reconfiguration

Configures ZRAM device size (typically 50% to 75% of physical RAM) with `lz4` compression and zero read-ahead:

```bash
adb shell "su -c '
if [ -d /sys/block/zram0 ]; then
    # 1. Turn off active swap
    swapoff /dev/block/zram0 2>/dev/null || true

    # 2. Reset device
    echo 1 > /sys/block/zram0/reset 2>/dev/null || true

    # 3. Select compression algorithm (lz4 if supported)
    avail_algo=\$(cat /sys/block/zram0/comp_algorithm 2>/dev/null || true)
    if echo \"\$avail_algo\" | grep -q \"lz4\"; then
        echo lz4 > /sys/block/zram0/comp_algorithm 2>/dev/null || true
    fi

    # 4. Set disk size (e.g., 3GB for 6GB/8GB device = 3221225472 bytes)
    echo 3221225472 > /sys/block/zram0/disksize 2>/dev/null || true

    # 5. Initialize and enable swap
    mkswap /dev/block/zram0 2>/dev/null || true
    swapon /dev/block/zram0 2>/dev/null || true
fi

# Kernel memory swappiness parameters
# swappiness=100 tells the kernel to aggressively use compressed ZRAM over dropping file page caches
sysctl -w vm.swappiness=100
# page-cluster=0 disables page read-ahead (crucial for random ZRAM RAM access)
sysctl -w vm.page-cluster=0
sysctl -w vm.vfs_cache_pressure=100
'"
```

## 4. Verification

```bash
adb shell "su -c '
free -m
cat /proc/swaps
cat /sys/block/zram0/mm_stat 2>/dev/null || true
'"
```
