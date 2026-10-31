#!/system/bin/sh
# ==============================================================================
# Magisk / KernelSU / APatch Boot Service Optimizer
# Synthesized for Android Optimizer Production Harness
# ==============================================================================

# Wait until boot is completed
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 3
done
sleep 5

LOG_FILE="/data/local/tmp/kernel_gpu_thermal_optimizer.log"
echo "[$(date)] Android Optimizer Boot Daemon starting..." > "$LOG_FILE"

# 1. CPU Scaling Governor & Schedutil Rate Limits (ktweak / FDE.AI)
for policy in /sys/devices/system/cpu/cpufreq/policy*; do
    if [ -f "$policy/scaling_governor" ]; then
        avail=$(cat "$policy/scaling_available_governors" 2>/dev/null || true)
        if echo "$avail" | grep -q "schedutil"; then
            echo "schedutil" > "$policy/scaling_governor" 2>/dev/null || true
            [ -f "$policy/schedutil/up_rate_limit_us" ] && echo 500 > "$policy/schedutil/up_rate_limit_us" 2>/dev/null || true
            [ -f "$policy/schedutil/down_rate_limit_us" ] && echo 20000 > "$policy/schedutil/down_rate_limit_us" 2>/dev/null || true
        elif echo "$avail" | grep -q "interactive"; then
            echo "interactive" > "$policy/scaling_governor" 2>/dev/null || true
        fi
    fi
done

# 2. GPU Tuning (Qualcomm Adreno KGSL & ARM Mali)
if [ -d "/sys/class/kgsl/kgsl-3d0" ]; then
    avail_gov=$(cat /sys/class/kgsl/kgsl-3d0/devfreq/available_governors 2>/dev/null || true)
    if echo "$avail_gov" | grep -q "msm-adreno-tz"; then
        echo "msm-adreno-tz" > /sys/class/kgsl/kgsl-3d0/devfreq/governor 2>/dev/null || true
    fi
    [ -f /sys/class/kgsl/kgsl-3d0/bus_split ] && echo 1 > /sys/class/kgsl/kgsl-3d0/bus_split 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/force_bus_on ] && echo 1 > /sys/class/kgsl/kgsl-3d0/force_bus_on 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/force_rail_on ] && echo 1 > /sys/class/kgsl/kgsl-3d0/force_rail_on 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/force_clk_on ] && echo 1 > /sys/class/kgsl/kgsl-3d0/force_clk_on 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/idle_timer ] && echo 80 > /sys/class/kgsl/kgsl-3d0/idle_timer 2>/dev/null || true
    [ -f /sys/class/kgsl/kgsl-3d0/thermal_pwrlevel ] && echo 0 > /sys/class/kgsl/kgsl-3d0/thermal_pwrlevel 2>/dev/null || true
fi

for mali in /sys/devices/platform/*.mali /sys/devices/platform/*.gpu /sys/class/misc/mali*; do
    if [ -d "$mali" ]; then
        [ -f "$mali/dvfs_enable" ] && echo 1 > "$mali/dvfs_enable" 2>/dev/null || true
        if [ -f "$mali/devfreq/governor" ]; then
            mali_gov=$(cat "$mali/devfreq/available_governors" 2>/dev/null || true)
            if echo "$mali_gov" | grep -q "simple_ondemand"; then
                echo "simple_ondemand" > "$mali/devfreq/governor" 2>/dev/null || true
            fi
        fi
    fi
done

# 3. Controlled Thermal Throttling Mitigation
stop thermal-engine 2>/dev/null || true
stop thermald 2>/dev/null || true
stop mi_thermald 2>/dev/null || true

for zone in /sys/class/thermal/thermal_zone*; do
    [ -f "$zone/mode" ] && echo "disabled" > "$zone/mode" 2>/dev/null || true
done

for cdev in /sys/class/thermal/cooling_device*; do
    cdev_type=$(cat "$cdev/type" 2>/dev/null || true)
    if echo "$cdev_type" | grep -qiE "cpu|gpu|processor"; then
        [ -f "$cdev/cur_state" ] && echo 0 > "$cdev/cur_state" 2>/dev/null || true
    fi
done

# 4. Storage I/O Schedulers, ZRAM & Memory Tuning
for q in /sys/block/*/queue/scheduler; do
    if [ -f "$q" ]; then
        avail=$(cat "$q" 2>/dev/null || true)
        if echo "$avail" | grep -q "none"; then
            echo "none" > "$q" 2>/dev/null || true
        elif echo "$avail" | grep -q "mq-deadline"; then
            echo "mq-deadline" > "$q" 2>/dev/null || true
        fi
    fi
done

for r in /sys/block/*/queue/read_ahead_kb; do
    [ -f "$r" ] && echo 512 > "$r" 2>/dev/null || true
done

if [ -d "/sys/block/zram0" ]; then
    avail_algo=$(cat /sys/block/zram0/comp_algorithm 2>/dev/null || true)
    if echo "$avail_algo" | grep -q "lz4"; then
        swapoff /dev/block/zram0 2>/dev/null || true
        echo "lz4" > /sys/block/zram0/comp_algorithm 2>/dev/null || true
        swapon /dev/block/zram0 2>/dev/null || true
    fi
fi

# Linux Virtual Memory parameters
sysctl -w vm.swappiness=100 >/dev/null 2>&1 || true
sysctl -w vm.vfs_cache_pressure=100 >/dev/null 2>&1 || true
sysctl -w vm.dirty_ratio=20 >/dev/null 2>&1 || true
sysctl -w vm.dirty_background_ratio=10 >/dev/null 2>&1 || true
sysctl -w vm.dirty_expire_centisecs=1500 >/dev/null 2>&1 || true
sysctl -w vm.dirty_writeback_centisecs=3000 >/dev/null 2>&1 || true
sysctl -w vm.page-cluster=0 >/dev/null 2>&1 || true

echo "[$(date)] Magisk boot daemon applied kernel, GPU & memory optimizations successfully." >> "$LOG_FILE"
