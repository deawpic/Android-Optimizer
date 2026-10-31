---
name: adb-debloater
description: Non-destructive User-0 OEM package debloating, telemetry removal, and one-click restoration skill via ADB adhering to Universal Android Debloater (UAD) Next-Gen safety taxonomy.
compatibility: Android 8+ (API Level 26+)
category: debloat
author: Android Optimizer Production Harness
---

# Android ADB Multi-OEM Debloater Skill

This skill allows safe, non-destructive removal of OEM telemetry, pre-installed bloatware, and analytics services across all major smartphone vendors.

## 1. Safety Taxonomy & Operating Principles

Debloating adheres to the Universal Android Debloater (UAD) classification:

| Safety Tier | Description | Action Policy |
| :--- | :--- | :--- |
| **Tier 1: Recommended** | Analytics, telemetry, adware, OEM feedback apps, junk bloatware | Safe for autonomous uninstallation for User 0 |
| **Tier 2: Advanced** | OEM duplicate ecosystem apps (Notes, Cloud Sync, Game Center, Store) | Safe if user has alternative apps installed |
| **Tier 3: Expert** | Carrier apps, TTS engines, Print Spooler, Bluetooth MIDI | Requires explicit user confirmation |
| **Tier 4: Unsafe** | SystemUI, Telecom, Settings Provider, Keyguard, PackageInstaller | **STRICTLY PROHIBITED** from uninstallation |

### The User-0 Non-Destructive Guarantee
- Packages are uninstalled ONLY for User 0 using `pm uninstall -k --user 0 <pkg>`.
- The `-k` flag retains application data directories if needed.
- System partition binaries (`/system/app`, `/product/app`) remain untouched on the read-only partition, allowing immediate restoration via `pm install-existing <pkg>` without data loss or root.

## 2. Dynamic OEM Detection

Identify the target device brand and model before applying manufacturer-specific debloat lists:

```bash
MANUFACTURER=$(adb shell getprop ro.product.manufacturer | tr -d '\r' | tr '[:upper:]' '[:lower:]')
BRAND=$(adb shell getprop ro.product.brand | tr -d '\r' | tr '[:upper:]' '[:lower:]')
echo "Detected Vendor: $MANUFACTURER ($BRAND)"
```

## 3. Package Inspection & Backup Manifest

Always save a snapshot of installed packages before executing a debloat batch:

```bash
# Capture baseline manifest of all installed packages
adb shell pm list packages -u > ./cache/packages_baseline.txt

# Inspect if a specific package is installed and active
adb shell pm list packages | grep <package_name>
```

## 4. Execution Workflow

```bash
# Uninstall package for User 0
adb shell pm uninstall -k --user 0 <package_name>

# Verify uninstallation (Package should appear in disabled/uninstalled list)
adb shell pm list packages -u | grep <package_name>
```

## 5. Restoration & Reinstatement

Any removed package can be reinstated instantly:

```bash
# Restore single package
adb shell cmd package install-existing <package_name>

# Batch restore from debloat log
while IFS= read -r pkg; do
    [ -n "$pkg" ] && adb shell cmd package install-existing "$pkg" || true
done < ./cache/debloated_manifest.log
```

## 6. Supported OEM Families

- **Samsung (One UI)**: Bixby agents, Game Home, Samsung VisitIn, Rubin, Samsung Discovery.
- **Xiaomi / POCO / Redmi (MIUI / HyperOS)**: MSA (MIUI System Ads), Analytics, Joyose, Daemon, MiPicks, YellowPage.
- **Oppo / Realme / OnePlus (ColorOS / Realme UI / OxygenOS)**: HeyTap services, NearMe analytics, CDO client, GameSpace.
- **Vivo / iQOO (Funtouch OS / OriginOS)**: Vivo AppStore, Vivo Push, BBK theme, HiBoard, UnionPay.
- **Huawei / Honor (EMUI / MagicOS)**: HiFolder, HiMovie, AppMarket, GameBox.
- **Motorola / Lenovo (MyUX)**: Motorola CCC notification, Help, Lenovo browser.
- **Transsion (Tecno / Infinix / Itel - HiOS / XOS)**: PalmStore, MagicShow, AhaGames.
- **Google / AOSP Base**: Feedback, Print recommendation, Bookmark provider.
