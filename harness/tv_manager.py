# -*- coding: utf-8 -*-
"""
Android TV & Google TV Optimizer Manager
Synthesized for Android Optimizer Production Harness.
Reference: https://github.com/Gathin23/cleanyourtv (CleanYourTV)

Features:
1. Wireless ADB Pairing & Connection over Wi-Fi.
2. Leanback & Google TV Environment Auto-Detection.
3. Safe Non-Destructive Debloating via `pm disable-user --user 0`.
4. Alternative Launcher Safety Guard (Blocks stock launcher removal if no replacement exists).
5. Bluetooth Remote & Navigation Service Protection.
6. Full Reversibility Engine via `pm enable`.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .adb_interface import ADBInterface
from .red_flag import EmergencyRedFlagInterceptor, RedFlagLevel

logger = logging.getLogger("AndroidOptimizer.TVManager")


class TVManager:
    """
    Manager for Android TV / Google TV optimization, bloatware removal,
    and safe alternative launcher deployment based on CleanYourTV.
    """

    def __init__(
        self,
        adb: Optional[ADBInterface] = None,
        presets_path: Optional[Path] = None
    ):
        self.adb = adb or ADBInterface()
        self.presets_path = presets_path or (Path(__file__).resolve().parent.parent / "data" / "tv_debloat_presets.json")
        self._data: Dict[str, Any] = {}
        self._load_presets()

    def _load_presets(self) -> None:
        """Loads TV debloat presets and launcher metadata."""
        if not self.presets_path.exists():
            logger.warning("TV debloat presets not found at: %s", self.presets_path)
            return

        try:
            content = self.presets_path.read_text(encoding="utf-8")
            self._data = json.loads(content)
        except Exception as e:
            logger.error("Failed to load TV presets: %s", e)

    def connect_wireless(self, host: str, port: int = 5555) -> Tuple[bool, str]:
        """Connects to Android TV over local Wi-Fi network."""
        return self.adb.connect_wireless(host, port)

    def disconnect_wireless(self) -> Tuple[bool, str]:
        """Disconnects wireless ADB connection."""
        return self.adb.disconnect_wireless()

    def detect_tv_environment(self) -> Dict[str, Any]:
        """Detects whether device is a TV and identifies manufacturer and active launchers."""
        is_tv = self.adb.is_android_tv()
        dev_info = self.adb.get_device_info()
        installed_packages = set(self.adb.get_installed_packages())

        # Match vendor preset
        mfg = dev_info.get("manufacturer", "").lower()
        model = dev_info.get("model", "").lower()
        brand = dev_info.get("brand", "").lower()

        matched_preset_key = "google_tv"
        if "xiaomi" in mfg or "xiaomi" in brand or "mitv" in model:
            matched_preset_key = "xiaomi_mitv"
        elif "tcl" in mfg or "tcl" in brand:
            matched_preset_key = "tcl_tv"
        elif "sony" in mfg or "sony" in brand:
            matched_preset_key = "sony_bravia"
        elif "hisense" in mfg or "hisense" in brand:
            matched_preset_key = "hisense_tv"

        presets = self._data.get("tv_presets", {})
        active_preset = presets.get(matched_preset_key, {})

        # Check installed launchers
        supported_launchers = self._data.get("supported_launchers", [])
        installed_alt_launchers = [
            l for l in supported_launchers
            if l.get("package") in installed_packages
        ]

        stock_launcher = active_preset.get("stock_launcher")
        has_stock_launcher = stock_launcher in installed_packages if stock_launcher else False

        return {
            "is_android_tv": is_tv,
            "device": dev_info,
            "matched_preset": matched_preset_key,
            "preset_description": active_preset.get("description", "Generic TV Profile"),
            "stock_launcher": stock_launcher,
            "stock_launcher_installed": has_stock_launcher,
            "installed_alternative_launchers": installed_alt_launchers,
            "has_alternative_launcher": len(installed_alt_launchers) > 0,
            "total_packages_count": len(installed_packages)
        }

    def debloat_tv(
        self,
        dry_run: bool = False,
        enable_launcher_swap: bool = False,
        target_alt_launcher: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes non-destructive TV debloating via `pm disable-user --user 0`.
        Safeguards stock launcher and TV remote controls.
        """
        env = self.detect_tv_environment()
        installed = set(self.adb.get_installed_packages())
        preset_key = env["matched_preset"]
        preset = self._data.get("tv_presets", {}).get(preset_key, {})
        candidate_packages = list(preset.get("packages", []))

        disabled = []
        skipped = []
        errors = []

        # 1. Evaluate Stock Launcher swap
        stock_launcher = preset.get("stock_launcher")
        if stock_launcher and stock_launcher in installed:
            if enable_launcher_swap:
                alt_pkgs = [l["package"] for l in self._data.get("supported_launchers", [])]
                if target_alt_launcher:
                    alt_pkgs.append(target_alt_launcher)

                verdict = EmergencyRedFlagInterceptor.audit_tv_package_action(
                    stock_launcher,
                    action="disable",
                    installed_packages=list(installed),
                    alternative_launchers=alt_pkgs
                )
                if verdict.is_safe:
                    candidate_packages.append(stock_launcher)
                    # Also include setup wizard if needed for Google TV
                    setup_wizard = preset.get("setup_wizard")
                    if setup_wizard and setup_wizard in installed:
                        candidate_packages.append(setup_wizard)
                else:
                    skipped.append({
                        "package": stock_launcher,
                        "reason": verdict.reason
                    })
            else:
                skipped.append({
                    "package": stock_launcher,
                    "reason": "Launcher swap not enabled (stock launcher retained for safety)."
                })

        # 2. Process candidate packages
        for pkg in candidate_packages:
            if pkg not in installed:
                continue

            # Safety audit check
            verdict = EmergencyRedFlagInterceptor.audit_tv_package_action(
                pkg,
                action="disable",
                installed_packages=list(installed),
                alternative_launchers=alt_pkgs if enable_launcher_swap else None
            )
            if not verdict.is_safe:
                skipped.append({
                    "package": pkg,
                    "reason": verdict.reason
                })
                continue

            if not dry_run:
                ok = self.adb.disable_package(pkg)
                if ok:
                    disabled.append(pkg)
                else:
                    errors.append(pkg)
            else:
                disabled.append(pkg)

        return {
            "status": "completed",
            "dry_run": dry_run,
            "device": env["device"],
            "preset_applied": preset_key,
            "disabled_count": len(disabled),
            "disabled_packages": disabled,
            "skipped_packages": skipped,
            "errors": errors,
            "methodology": "pm disable-user --user 0"
        }

    def restore_tv(self, include_stock_launcher: bool = True) -> Dict[str, Any]:
        """
        Restores all disabled packages on the Android TV using `pm enable`.
        Guarantees complete reversibility.
        """
        env = self.detect_tv_environment()
        preset_key = env["matched_preset"]
        preset = self._data.get("tv_presets", {}).get(preset_key, {})

        packages_to_enable = list(preset.get("packages", []))
        if include_stock_launcher:
            stock = preset.get("stock_launcher")
            if stock:
                packages_to_enable.append(stock)
            setup = preset.get("setup_wizard")
            if setup:
                packages_to_enable.append(setup)

        enabled = []
        errors = []

        for pkg in packages_to_enable:
            ok = self.adb.enable_package(pkg)
            if ok:
                enabled.append(pkg)
            else:
                errors.append(pkg)

        return {
            "status": "restored",
            "device": env["device"],
            "preset": preset_key,
            "enabled_count": len(enabled),
            "enabled_packages": enabled,
            "errors": errors,
            "methodology": "pm enable <package>"
        }

    def list_supported_launchers(self) -> List[Dict[str, str]]:
        """Returns verified alternative TV launchers."""
        return list(self._data.get("supported_launchers", []))
