# -*- coding: utf-8 -*-
"""
Ground Truth Benchmark Evaluation Runner
Evaluates Android Optimizer Harness against 10 domain benchmark cases.
"""

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
from harness.evaluator import BenchmarkEvaluator
from harness.red_flag import EmergencyRedFlagInterceptor, RedFlagLevel
from harness.verifier import GroundingOracle
from harness.persona_router import PersonaRouter, PersonaTier
from harness.soc_profile import SoCProfileManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("EvalBenchmarks")


def simulate_agent_action(case: dict) -> dict:
    """Simulates agent trajectory and applies safety gates for benchmark testing."""
    category = case.get("category", "")
    inp = case.get("input", {})

    # Check thermal and battery telemetry
    if "temperature_raw" in inp or "battery_level" in inp:
        temp_raw = inp.get("temperature_raw")
        level = inp.get("battery_level")
        is_charging = inp.get("is_charging", False)
        verdict = EmergencyRedFlagInterceptor.evaluate_battery_telemetry(temp_raw, level, is_charging)
        if not verdict.is_safe:
            return {
                "intercepted": True,
                "red_flag_level": verdict.level.value,
                "reason": verdict.reason,
                "command": ""
            }

    # Check command safety
    if "command" in inp:
        verdict = EmergencyRedFlagInterceptor.audit_command_safety(inp["command"])
        if not verdict.is_safe:
            return {
                "intercepted": True,
                "red_flag_level": verdict.level.value,
                "reason": verdict.reason,
                "command": inp["command"]
            }

    # Check package debloat safety
    if category == "debloat" and "package_name" in inp:
        pkg = inp["package_name"]
        verdict = EmergencyRedFlagInterceptor.audit_package_debloat(pkg)
        if not verdict.is_safe:
            return {
                "intercepted": True,
                "red_flag_level": verdict.level.value,
                "reason": verdict.reason,
                "command": ""
            }
        return {
            "intercepted": False,
            "command": f"adb shell pm uninstall -k --user 0 {pkg}",
            "response_text": f"Successfully uninstalled {pkg} for User 0."
        }

    # Check discretion violations
    if category == "discretion":
        prompt = inp.get("prompt", "")
        sanitized, audit = GroundingOracle().sanitize_unverified_claims(prompt)
        return {
            "intercepted": False,
            "response_text": sanitized,
            "audit": audit
        }

    # Check SoC Profile Resolution
    if category == "soc_profile":
        platform = inp.get("platform", "").lower()
        soc_mgr = SoCProfileManager()
        resolved_soc = soc_mgr.resolve_soc_by_platform(platform)
        return {
            "intercepted": False,
            "resolved_soc": resolved_soc,
            "response_text": f"Resolved SoC: {resolved_soc}"
        }

    # Check TV Debloat and Launcher Guard
    if category == "tv_debloat":
        pkg = inp.get("target_package", "")
        installed_launchers = inp.get("installed_launchers", [])
        verdict = EmergencyRedFlagInterceptor.audit_tv_package_action(
            package_name=pkg,
            action=inp.get("action", "disable"),
            installed_packages=installed_launchers,
            alternative_launchers=installed_launchers
        )
        if not verdict.is_safe:
            return {
                "intercepted": True,
                "red_flag_level": verdict.level.value,
                "reason": verdict.reason
            }
        return {
            "intercepted": False,
            "command": f"pm disable-user --user 0 {pkg}",
            "response_text": f"Successfully disabled {pkg} using non-destructive User-0 protocol."
        }

    return {
        "intercepted": False,
        "command": "adb shell cmd package compile -m speed-profile -a",
        "response_text": "Task completed successfully with speed-profile."
    }


def main():
    evaluator = BenchmarkEvaluator()
    logger.info("Executing Benchmark Suite across %d Ground Truth cases...", len(evaluator.cases))

    results = evaluator.run_suite(simulate_agent_action)

    print("\n" + "=" * 60)
    print("🎯 HARNESS BENCHMARK EVALUATION RESULTS")
    print("=" * 60)
    print(f"Total Cases     : {results['total_cases']}")
    print(f"Passed Cases    : {results['passed_cases']}")
    print(f"Pass@1 Rate     : {results['pass_at_1'] * 100:.1f}%")
    print(f"Avg Latency     : {results['average_latency_ms']:.2f} ms")
    print("-" * 60)

    for r in results["case_results"]:
        status_icon = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"[{status_icon}] {r['case_id']} ({r['category']}) - {r['latency_ms']}ms")
        if not r["passed"]:
            for err in r["failure_reasons"]:
                print(f"     -> Reason: {err}")

    print("=" * 60)
    return 0 if results["pass_at_1"] == 1.0 else 1


if __name__ == "__main__":
    sys.exit(main())
