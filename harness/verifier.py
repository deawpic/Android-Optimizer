# -*- coding: utf-8 -*-
"""
Grounding Oracle & Anti-Hallucination Verifier for Android Systems
Synthesized for Android Optimizer Production Harness.

Features:
1. Grounding Whitelist Oracle for Android parameters, Sysfs paths, and sysctl keys.
2. Citation & Identifier Extraction (SDK versions, Dexopt modes, Sysfs nodes, Package IDs).
3. Anti-Sycophancy & Discretion Gate: intercepts unrealistic 100% performance guarantees.
4. Auto-Sanitizer: strips unverified citations or flags ungrounded claims.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("AndroidOptimizer.GroundingOracle")

# 1. Prohibited absolute guarantees (Anti-Sycophancy / System Discretion Gate)
PROHIBITED_ABSOLUTE_GUARANTEES = [
    re.compile(r"เร็วขึ้น(?:อย่าง)?แน่นอน\s*(?:100%|ร้อยเปอร์เซ็นต์)?", re.IGNORECASE),
    re.compile(r"การันตีผล(?:การเพิ่มความเร็ว|fps|เฟรมเรต)?\s*(?:100%)?", re.IGNORECASE),
    re.compile(r"ไม่มีทาง(?:แล็ก|กระตุก|บั๊ก|เครื่องดับ)", re.IGNORECASE),
    re.compile(r"รับรองผล(?:ลื่นไหล|ไม่กินแบต)?", re.IGNORECASE),
    re.compile(r"100%\s*(?:guarantee|safe|bug-free|no\s*throttle)", re.IGNORECASE),
]

# 2. Android Domain Citation & Parameter Regexes
ANDROID_PATTERNS = {
    # Android SDK Level (e.g. SDK 31, API 34)
    "sdk_version": re.compile(r"\b(?:SDK|API|API Level)\s*([1-3][0-9])\b", re.IGNORECASE),
    # Dexopt Compilation Modes
    "dexopt_mode": re.compile(r"\b(?:compile\s+-m\s+)?(speed-profile|speed|everything|quicken|space-profile|space|verify)\b"),
    # Linux sysctl keys
    "sysctl_key": re.compile(r"\b(vm\.(?:swappiness|vfs_cache_pressure|dirty_ratio|dirty_background_ratio|dirty_expire_centisecs|dirty_writeback_centisecs|page-cluster|overcommit_memory))\b"),
    # Android System Properties
    "system_property": re.compile(r"\b(ro\.(?:product\.(?:manufacturer|brand|model|cpu\.abi)|build\.version\.(?:sdk|release)|soc\.(?:manufacturer|model)|board\.platform|hardware)|debug\.hwui\.renderer|sys\.boot_completed)\b"),
    # Sysfs Base Nodes
    "sysfs_node": re.compile(r"(/sys/(?:devices/system/cpu/cpufreq|class/kgsl/kgsl-3d0|block/[a-z0-9]+/queue|class/thermal|block/zram0)[a-zA-Z0-9_\-/]*)"),
}

# Verified Sysfs Node Root Prefixes
VERIFIED_SYSFS_PREFIXES = (
    "/sys/devices/system/cpu/",
    "/sys/class/kgsl/kgsl-3d0",
    "/sys/block/zram",
    "/sys/class/thermal",
    "/sys/block/",
    "/proc/sys/vm/",
)

# Standard Verified Baseline Whitelist
STANDARD_VERIFIED_WHITELIST = {
    # SDK Levels
    "28", "29", "30", "31", "32", "33", "34", "35",
    # Dexopt Modes
    "speed-profile", "speed", "everything", "quicken", "verify", "space", "space-profile",
    # Sysctl Keys
    "vm.swappiness", "vm.vfs_cache_pressure", "vm.dirty_ratio", "vm.dirty_background_ratio",
    "vm.dirty_expire_centisecs", "vm.dirty_writeback_centisecs", "vm.page-cluster", "vm.overcommit_memory",
    # Properties & SoC Platforms
    "ro.product.manufacturer", "ro.product.brand", "ro.product.model", "ro.build.version.sdk",
    "ro.build.version.release", "debug.hwui.renderer", "sys.boot_completed",
    "ro.soc.manufacturer", "ro.soc.model", "ro.board.platform", "ro.hardware",
    # Verified SoC Identifiers
    "sm8650", "sm8550", "mt6989", "mt6985", "zuma", "pineapple", "kalama",
    # GPU Governors & Parameters
    "msm-adreno-tz", "simple_ondemand", "bus_split", "force_bus_on", "thermal_pwrlevel", "idle_timer",
    "up_rate_limit_us", "down_rate_limit_us",
    # Android TV Features & Verified Packages (CleanYourTV)
    "android.software.leanback", "com.google.android.apps.tv.launcherx", "com.google.android.tungsten.setupwraith",
    "com.google.android.tv.launcher", "com.mitv.tvhome", "com.tcl.waterfall.overseas",
    "com.gathin.tvhome", "com.spocky.projectivy", "me.efdev.flauncher", "com.princecreations.emulauncher",
}


class GroundingOracle:
    """
    Independent Verification Oracle ensuring AI Agents never hallucinate Android
    system parameters, invalid sysctl variables, or make ungrounded guarantees.
    """

    def __init__(self, verified_whitelist: Optional[Set[str]] = None, cache_instance: Optional[Any] = None):
        self.verified_whitelist: Set[str] = set(verified_whitelist or STANDARD_VERIFIED_WHITELIST)
        self.cache = cache_instance

    def register_verified(self, identifier: str) -> None:
        """Adds a verified identifier to the whitelist and persistent cache."""
        cleaned = identifier.strip()
        self.verified_whitelist.add(cleaned)
        if self.cache and hasattr(self.cache, "add_verified_identifier"):
            self.cache.add_verified_identifier(cleaned, source="grounding_oracle")

    def get_all_verified(self) -> Set[str]:
        """Combines in-memory and database cache verified identifiers."""
        combined = set(self.verified_whitelist)
        if self.cache and hasattr(self.cache, "get_all_verified_identifiers"):
            combined.update(self.cache.get_all_verified_identifiers())
        return combined

    @classmethod
    def extract_identifiers(cls, text: str) -> Dict[str, List[str]]:
        """Extracts Android identifiers and configuration parameters from text."""
        extracted: Dict[str, List[str]] = {}
        for category, pattern in ANDROID_PATTERNS.items():
            matches = pattern.findall(text)
            cleaned = []
            for m in matches:
                val = m[0] if isinstance(m, tuple) else m
                if val and val not in cleaned:
                    cleaned.append(val.strip())
            if cleaned:
                extracted[category] = cleaned
        return extracted

    def detect_unverified_identifiers(self, text: str) -> Dict[str, List[str]]:
        """Detects identifiers present in text that are not verified in oracle."""
        extracted = self.extract_identifiers(text)
        all_verified = self.get_all_verified()
        unverified: Dict[str, List[str]] = {}

        for category, items in extracted.items():
            if category == "sysfs_node":
                missing = [
                    item for item in items
                    if item not in all_verified and not any(item.startswith(prefix) for prefix in VERIFIED_SYSFS_PREFIXES)
                ]
            else:
                missing = [item for item in items if item not in all_verified]
            if missing:
                unverified[category] = missing
        return unverified

    @classmethod
    def check_discretion_violations(cls, text: str) -> List[str]:
        """Checks for prohibited absolute claims or guarantees."""
        violations = []
        for pattern in PROHIBITED_ABSOLUTE_GUARANTEES:
            match = pattern.search(text)
            if match:
                violations.append(match.group(0))
        return violations

    def sanitize_unverified_claims(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Sanitizes text by flagging ungrounded claims and removing sycophantic guarantees,
        ensuring evidence-based, objective communication.
        """
        discretion_violations = self.check_discretion_violations(text)
        sanitized = text

        for violation in discretion_violations:
            replacement = "มีโอกาสช่วยเพิ่มประสิทธิภาพขึ้นตามสภาพฮาร์ดแวร์และการระบายความร้อน"
            sanitized = sanitized.replace(violation, replacement)

        audit_result = {
            "discretion_violations": discretion_violations,
            "was_modified": bool(discretion_violations),
            "unverified_identifiers": self.detect_unverified_identifiers(text)
        }
        return sanitized, audit_result
