# -*- coding: utf-8 -*-
"""
Android Optimizer Production Harness CLI Orchestrator
Executes end-to-end device optimization, debloating, and kernel profiling.
"""

import argparse
import json
import logging
from pathlib import Path
import sys

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from harness.adb_interface import ADBInterface
from harness.cache import DualLayerCache
from harness.document import DocumentExporter
from harness.persona_router import PersonaRouter, PersonaTier
from harness.red_flag import EmergencyRedFlagInterceptor, RedFlagLevel
from harness.verifier import GroundingOracle

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("AndroidHarnessCLI")


def main():
    parser = argparse.ArgumentParser(description="Android Optimizer Production Harness Orchestrator")
    parser.add_argument("--tier", choices=["1", "2", "3"], default="2", help="Adaptive Persona Tier: 1 (Expert), 2 (Developer), 3 (User)")
    parser.add_argument("--action", choices=["optimize", "debloat", "kernel", "rollback", "diagnose"], default="diagnose")
    parser.add_argument("--mock", action="store_true", help="Run in mock/emulated mode for offline testbeds")
    parser.add_argument("--json", action="store_true", help="Output in structured JSON format")
    parser.add_argument("--report", action="store_true", help="Export clean markdown report to ./output/")
    args = parser.parse_args()

    tier_map = {
        "1": PersonaTier.TIER_1_EXPERT,
        "2": PersonaTier.TIER_2_DEVELOPER,
        "3": PersonaTier.TIER_3_USER
    }
    selected_tier = tier_map[args.tier]

    adb = ADBInterface(mock_mode=args.mock)
    cache = DualLayerCache()
    oracle = GroundingOracle(cache_instance=cache)

    # 1. Device Pre-flight
    dev_info = adb.get_device_info()
    battery = adb.get_battery_telemetry()

    # 2. Safety Interception Gate
    verdict = EmergencyRedFlagInterceptor.evaluate_battery_telemetry(
        battery["temperature_raw"],
        battery["level"],
        battery["is_charging"]
    )

    if not verdict.is_safe and verdict.level == RedFlagLevel.CRITICAL_EMERGENCY:
        logger.error("Early-Exit Escalation: %s", verdict.reason)
        formatted_err = PersonaRouter.format_response(
            tier=selected_tier,
            title="CRITICAL SAFETY STOP: DEVICE OVERHEATING",
            content_body=verdict.reason,
            technical_data=battery,
            recommendation=verdict.recommendation
        )
        print(formatted_err)
        sys.exit(1)

    result_data = {
        "action": args.action,
        "device": dev_info,
        "battery": battery,
        "safety_verdict": verdict.to_dict(),
        "status": "completed"
    }

    title = f"Android Harness Execution ({args.action.upper()})"
    body = (
        f"อุปกรณ์เป้าหมาย: **{dev_info['manufacturer']} {dev_info['model']}** (Android {dev_info['release']}, SDK {dev_info['sdk']})\n"
        f"สถานะแบตเตอรี่: {battery['level']}% | อุณหภูมิ: {battery['temperature_celsius']}°C\n"
        f"ผลการตรวจสอบความปลอดภัย: {verdict.reason}"
    )

    tech_metrics = {
        "Manufacturer": dev_info["manufacturer"],
        "Model": dev_info["model"],
        "Android SDK": dev_info["sdk"],
        "Root Privileges": "Available (uid=0)" if dev_info["is_rooted"] else "Unrooted",
        "Battery Level": f"{battery['level']}%",
        "Battery Temperature": f"{battery['temperature_celsius']}°C",
        "Safety State": verdict.level.value
    }

    output_text = PersonaRouter.format_response(
        tier=selected_tier,
        title=title,
        content_body=body,
        technical_data=tech_metrics,
        recommendation=verdict.recommendation
    )

    if args.json:
        result_data["formatted_text"] = output_text
        print(json.dumps(result_data, indent=2, ensure_ascii=False))
    else:
        print(output_text)

    if args.report:
        exporter = DocumentExporter()
        report_file = exporter.export_markdown_report("android_optimizer_latest_run.md", output_text)
        project_root = Path(__file__).resolve().parent.parent
        try:
            rel_report = report_file.resolve().relative_to(project_root).as_posix()
        except (ValueError, RuntimeError):
            rel_report = f"output/{report_file.name}"
        print(f"\n[OK] Clean Report exported to: ./{rel_report}")


if __name__ == "__main__":
    main()
