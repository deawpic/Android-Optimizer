#!/system/bin/sh
start thermal-engine 2>/dev/null || true
start thermald 2>/dev/null || true
start mi_thermald 2>/dev/null || true

for zone in /sys/class/thermal/thermal_zone*; do
    [ -f "$zone/mode" ] && echo "enabled" > "$zone/mode" 2>/dev/null || true
done

[ -f /sys/module/msm_thermal/core_control/enabled ] && echo 1 > /sys/module/msm_thermal/core_control/enabled 2>/dev/null || true
[ -f /sys/module/msm_thermal/parameters/enabled ] && echo "Y" > /sys/module/msm_thermal/parameters/enabled 2>/dev/null || true

sysctl -w vm.swappiness=60 >/dev/null 2>&1 || true
for r in /sys/block/*/queue/read_ahead_kb; do
    [ -f "$r" ] && echo 128 > "$r" 2>/dev/null || true
done
rm -f /data/local/tmp/kernel_gpu_thermal_optimizer.log
