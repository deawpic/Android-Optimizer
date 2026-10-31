# -*- coding: utf-8 -*-
"""
Android TV & Google TV CleanYourTV CLI Orchestrator
Synthesized for Android Optimizer Production Harness.
Reference: https://github.com/Gathin23/cleanyourtv
"""

import argparse
import json
import logging
from pathlib import Path
import sys

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from harness.adb_interface import ADBInterface
from harness.document import DocumentExporter
from harness.tv_manager import TVManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("CleanYourTV")


def main():
    parser = argparse.ArgumentParser(description="CleanYourTV: Android TV & Google TV Optimizer")
    parser.add_argument("--ip", help="Wireless IP address of Android TV (e.g. 192.168.1.50 or 192.168.1.50:5555)")
    parser.add_argument("--detect", action="store_true", help="Detect TV environment, vendor preset, and launchers")
    parser.add_argument("--clean", action="store_true", help="Debloat TV bloatware and ad services via disable-user --user 0")
    parser.add_argument("--swap-launcher", action="store_true", help="Disable stock ad launcher (requires alt launcher)")
    parser.add_argument("--alt-launcher", help="Package of installed alternative launcher (e.g. com.spocky.projectivy, me.efdev.flauncher)")
    parser.add_argument("--restore", action="store_true", help="Re-enable all disabled TV packages and restore stock launcher")
    parser.add_argument("--mock", action="store_true", help="Run in mock/emulated mode for offline testbed")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--report", action="store_true", help="Export clean markdown report to ./output/")
    args = parser.parse_args()

    adb = ADBInterface(mock_mode=args.mock)
    tv = TVManager(adb=adb)

    # 1. Connect Wireless if IP is provided
    if args.ip:
        logger.info("Connecting to Android TV wirelessly at %s...", args.ip)
        success, msg = tv.connect_wireless(args.ip)
        if not success:
            logger.error("Failed to connect to TV at %s: %s", args.ip, msg)
            if not args.mock:
                sys.exit(1)
        else:
            logger.info("Successfully connected to TV: %s", msg)

    # In mock mode, configure TV mock state
    if args.mock:
        adb._mock_state["is_tv"] = True
        adb._mock_state["manufacturer"] = "Google"
        adb._mock_state["brand"] = "google"
        adb._mock_state["model"] = "Chromecast"
        adb._mock_state["characteristics"] = "tv"
        adb._mock_state["installed_packages"].extend([
            "com.google.android.apps.tv.launcherx",
            "com.google.android.tungsten.setupwraith",
            "com.google.android.tvrecommendations",
            "com.gathin.tvhome"
        ])

    env = tv.detect_tv_environment()

    # Default action if none specified: detect
    if not (args.clean or args.restore):
        args.detect = True

    result_data = {
        "tv_environment": env,
        "action": "detect"
    }

    if args.clean:
        result_data["action"] = "clean"
        clean_res = tv.debloat_tv(
            dry_run=False,
            enable_launcher_swap=args.swap_launcher,
            target_alt_launcher=args.alt_launcher
        )
        result_data["clean_result"] = clean_res

    elif args.restore:
        result_data["action"] = "restore"
        restore_res = tv.restore_tv(include_stock_launcher=True)
        result_data["restore_result"] = restore_res

    # Output formatting
    if args.json:
        print(json.dumps(result_data, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("📺 CLEANYOURTV: ANDROID TV & GOOGLE TV OPTIMIZER")
        print("=" * 60)
        print(f"Device Model     : {env['device'].get('manufacturer', 'Unknown')} {env['device'].get('model', 'TV')}")
        print(f"Android TV OS    : {'✅ YES (Leanback/Google TV)' if env['is_android_tv'] else '⚠️ Generic Android'}")
        print(f"Matched Preset   : {env['matched_preset'].upper()} ({env['preset_description']})")
        print(f"Stock Launcher   : {env['stock_launcher'] or 'None'}")
        print(f"Alt Launcher     : {'✅ Installed' if env['has_alternative_launcher'] else '❌ Not Detected'}")
        if env["installed_alternative_launchers"]:
            alts = ", ".join([f"{l['name']} ({l['package']})" for l in env["installed_alternative_launchers"]])
            print(f"Detected Alts    : {alts}")
        print("-" * 60)

        if args.clean:
            c = result_data["clean_result"]
            print(f"Disabled Packages: {c['disabled_count']} packages safely disabled via pm disable-user --user 0")
            for p in c["disabled_packages"]:
                print(f"  [-] Disabled: {p}")
            if c["skipped_packages"]:
                print(f"Skipped / Guarded: {len(c['skipped_packages'])} packages")
                for s in c["skipped_packages"]:
                    print(f"  [!] Skipped: {s['package']} - {s['reason']}")
            print("=" * 60)
            print("✅ TV Optimization complete! Bloatware & ad recommendations deactivated.")

        elif args.restore:
            r = result_data["restore_result"]
            print(f"Restored Packages: {r['enabled_count']} packages re-enabled via pm enable")
            for p in r["enabled_packages"]:
                print(f"  [+] Restored: {p}")
            print("=" * 60)
            print("✅ TV Restoration complete! Stock launcher and services reinstated.")

    if args.report:
        exporter = DocumentExporter()
        report_content = f"""# CleanYourTV: รายงานการปรับแต่ง Android TV & Google TV
**อ้างอิงมาตรฐาน**: [Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv)  
**อุปกรณ์**: {env['device'].get('manufacturer')} {env['device'].get('model')}  
**สถานะ Leanback / TV**: {'เปิดใช้งาน (Android TV)' if env['is_android_tv'] else 'Generic Android'}  

---

## 1. ข้อมูลระบบและการตรวจจับโปรไฟล์
| รายการ | ค่าที่ตรวจพบ |
| :--- | :--- |
| **โปรไฟล์ที่ตรงกัน** | `{env['matched_preset']}` |
| **Stock Launcher** | `{env['stock_launcher']}` |
| **Launcher ทางเลือก** | {'ตรวจพบพร้อมใช้งาน' if env['has_alternative_launcher'] else 'ยังไม่พบ Launcher ทางเลือก'} |
| **วิธีการปรับแต่ง** | `pm disable-user --user 0` (ไม่ลบไฟล์ ปลอดภัย 100%) |

---

## 2. ผลการดำเนินการ
- **การดำเนินการ**: `{result_data['action'].upper()}`
"""
        report_path = exporter.export_markdown_report("android_tv_optimization_report.md", report_content)
        rel_path = report_path.name
        try:
            rel_path = report_path.resolve().relative_to(Path(__file__).resolve().parent.parent).as_posix()
        except Exception:
            rel_path = f"output/{report_path.name}"
        print(f"\n[OK] TV Report exported to: ./{rel_path}")


if __name__ == "__main__":
    main()
