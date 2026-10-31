# -*- coding: utf-8 -*-
"""
Active Device & ADB Health Check Probe
Synthesized for Android Optimizer Production Harness.
"""

import json
from pathlib import Path
import sys

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from harness.adb_interface import ADBInterface
from harness.red_flag import EmergencyRedFlagInterceptor


def main():
    use_mock = "--mock" in sys.argv
    adb = ADBInterface(mock_mode=use_mock)

    print("=" * 60)
    print("🔍 ANDROID DEVICE & ADB HEALTH PROBE")
    print("=" * 60)

    if not adb.is_adb_installed():
        print("❌ Error: ADB command not found in system PATH.")
        sys.exit(1)

    devices = adb.get_connected_devices()
    if not devices:
        print("⚠️ Warning: No active Android devices connected via ADB.")
        if not use_mock:
            print("Tip: Run with '--mock' to test the harness in synthetic mode.")
            sys.exit(1)

    info = adb.get_device_info()
    battery = adb.get_battery_telemetry()
    verdict = EmergencyRedFlagInterceptor.evaluate_battery_telemetry(
        battery["temperature_raw"],
        battery["level"],
        battery["is_charging"]
    )

    print(f"Device Model     : {info['manufacturer']} {info['model']} (Brand: {info['brand']})")
    print(f"Android Version  : Android {info['release']} (SDK {info['sdk']})")
    print(f"Root Privileges  : {'✅ YES (uid=0)' if info['is_rooted'] else '❌ NO (Unrooted Userspace)'}")
    print(f"Battery Capacity : {battery['level']}% {'[CHARGING]' if battery['is_charging'] else ''}")
    print(f"Battery Temp     : {battery['temperature_celsius']}°C (Raw: {battery['temperature_raw']})")
    print("-" * 60)
    print(f"Safety Verdict   : [{verdict.level.value}] {verdict.reason}")
    print(f"Recommendation   : {verdict.recommendation}")
    print("=" * 60)

    if "--json" in sys.argv:
        output_payload = {
            "device": info,
            "battery": battery,
            "safety": verdict.to_dict()
        }
        print("\nJSON Output:\n" + json.dumps(output_payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
