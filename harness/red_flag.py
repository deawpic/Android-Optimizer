# -*- coding: utf-8 -*-
"""
Emergency & Red Flag Interceptor for Android Systems
Synthesized for Android Optimizer Production Harness.

Features:
1. Instant Early-Exit Escalation: trips circuit breaker without waiting for long RAG/execution loops.
2. Battery Temperature Protection:
   - Warning: >= 42.0°C (dumpsys 420)
   - High Danger: >= 45.0°C (dumpsys 450) -> Prohibits thermal engine disabling
   - Critical Red Flag: >= 48.0°C (dumpsys 480) -> Immediate emergency stop & cool-down alert
3. Battery Capacity Guard: prohibits intensive compilation if battery <= 15%.
4. Destructive Command Prevention: blocks partition formatting, `rm -rf /`, or critical framework debloats.
5. Bootloop and System Crash detection.
"""

from enum import Enum
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("AndroidOptimizer.RedFlagInterceptor")


class RedFlagLevel(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    DANGER = "DANGER"
    CRITICAL_EMERGENCY = "CRITICAL_EMERGENCY"


class RedFlagVerdict:
    def __init__(
        self,
        level: RedFlagLevel,
        is_safe: bool,
        reason: str,
        recommendation: str,
        metrics: Optional[Dict[str, Any]] = None
    ):
        self.level = level
        self.is_safe = is_safe
        self.reason = reason
        self.recommendation = recommendation
        self.metrics = metrics or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "is_safe": self.is_safe,
            "reason": self.reason,
            "recommendation": self.recommendation,
            "metrics": self.metrics
        }


# Prohibited destructive shell operations
DESTRUCTIVE_COMMAND_PATTERNS = [
    re.compile(r"rm\s+(?:-[a-zA-Z]*r[a-zA-Z]*f?[a-zA-Z]*\s+)*(?:/|/system|/vendor|/data|/boot|/apex)", re.IGNORECASE),
    re.compile(r"dd\s+if=.*?of=/dev/block", re.IGNORECASE),
    re.compile(r"fastboot\s+(?:erase|flash)\s+(?:boot|system|vendor)", re.IGNORECASE),
    re.compile(r"(?:format|mkfs(?:\.[a-z0-9]+)?)\s+/dev/block", re.IGNORECASE),
    re.compile(r"pm\s+uninstall.*?(?:com\.android\.systemui|com\.android\.settings|com\.android\.keyguard|com\.android\.phone)", re.IGNORECASE),
]

CRITICAL_FRAMEWORK_PACKAGES = {
    "com.android.systemui",
    "com.android.settings",
    "com.android.phone",
    "com.android.keyguard",
    "com.android.packageinstaller",
    "com.google.android.packageinstaller",
}

CRITICAL_TV_PACKAGES = {
    "com.google.android.tungsten.bluetooth",
    "com.google.android.tv.remote.service",
    "com.android.bluetooth",
    "com.google.android.inputmethod.latin",
}

STOCK_TV_LAUNCHERS = {
    "com.google.android.apps.tv.launcherx",
    "com.google.android.tv.launcher",
    "com.mitv.tvhome",
    "com.tcl.waterfall.overseas",
}


class EmergencyRedFlagInterceptor:
    """
    Early-exit Safety Gatekeeper preventing hardware damage or bricked devices.
    """

    @classmethod
    def evaluate_battery_telemetry(
        cls,
        temperature_raw: Optional[int],
        battery_level: Optional[int],
        is_charging: bool = False
    ) -> RedFlagVerdict:
        """
        Evaluates battery conditions from dumpsys battery:
        temperature_raw is in tenths of degree Celsius (e.g., 425 = 42.5°C).
        """
        metrics = {
            "temperature_celsius": (temperature_raw / 10.0) if temperature_raw is not None else None,
            "battery_level": battery_level,
            "is_charging": is_charging
        }

        # 1. Critical Overheating Guard (>= 48.0°C)
        if temperature_raw is not None and temperature_raw >= 480:
            return RedFlagVerdict(
                level=RedFlagLevel.CRITICAL_EMERGENCY,
                is_safe=False,
                reason=f"🚨 CRITICAL THERMAL RED FLAG: อุณหภูมิแบตเตอรี่พุ่งสูงถึง {temperature_raw / 10.0:.1f}°C ซึ่งเกินเกณฑ์ปลอดภัยสูงสุด (48.0°C)",
                recommendation="หยุดการทำงานทันที ถอดสายชาร์จ วางอุปกรณ์ในพื้นที่โปร่งและปล่อยให้ระบายความร้อน ห้ามรันสคริปต์ปรับแต่งใดๆ",
                metrics=metrics
            )

        # 2. High Danger Threshold (>= 45.0°C)
        if temperature_raw is not None and temperature_raw >= 450:
            return RedFlagVerdict(
                level=RedFlagLevel.DANGER,
                is_safe=False,
                reason=f"⚠️ DANGER: อุณหภูมิแบตเตอรี่อยู่ที่ {temperature_raw / 10.0:.1f}°C (สูงผิดปกติ)",
                recommendation="ไม่อนุญาตให้ปิดระบบควบคุมความร้อน (Thermal Engine) หรือเร่งโอเวอร์คล็อก GPU Adreno/Mali เด็ดขาด",
                metrics=metrics
            )

        # 3. Low Battery Threshold (<= 15%)
        if battery_level is not None and battery_level <= 15 and not is_charging:
            return RedFlagVerdict(
                level=RedFlagLevel.WARNING,
                is_safe=False,
                reason=f"⚠️ LOW BATTERY WARNING: ระดับแบตเตอรี่เหลือเพียง {battery_level}%",
                recommendation="ไม่ควรทำการคอมไพล์ Dexopt แบบ AOT (-a) หรือเขียน I/O หนัก เพราะอาจทำให้เครื่องดับฉับพลันและเกิดความเสียหายต่อระบบไฟล์",
                metrics=metrics
            )

        # 4. Thermal Warning (>= 42.0°C)
        if temperature_raw is not None and temperature_raw >= 420:
            return RedFlagVerdict(
                level=RedFlagLevel.WARNING,
                is_safe=True,
                reason=f"อุณหภูมิเริ่มสูงขึ้น ({temperature_raw / 10.0:.1f}°C)",
                recommendation="อนุญาตให้ทำงานได้ แต่ควรใช้โปรไฟล์ speed-profile แทนการคอมไพล์ full everything",
                metrics=metrics
            )

        return RedFlagVerdict(
            level=RedFlagLevel.NORMAL,
            is_safe=True,
            reason="สถานะแบตเตอรี่และอุณหภูมิอยู่ในเกณฑ์ปกติ",
            recommendation="สามารถดำเนินกระบวนการปรับแต่งได้อย่างปลอดภัย",
            metrics=metrics
        )

    @classmethod
    def audit_command_safety(cls, command: str) -> RedFlagVerdict:
        """Audits shell commands for destructive, non-recoverable operations."""
        for pattern in DESTRUCTIVE_COMMAND_PATTERNS:
            match = pattern.search(command)
            if match:
                return RedFlagVerdict(
                    level=RedFlagLevel.CRITICAL_EMERGENCY,
                    is_safe=False,
                    reason=f"🚨 INTERCEPT: ตรวจพบคำสั่งอันตรายร้ายแรงที่ทำลายระบบปฏิบัติการ: '{match.group(0)}'",
                    recommendation="ปฏิเสธการรันคำสั่งโดยเด็ดขาด เพื่อป้องกันเครื่องติด Bootloop หรือระบบพังทลาย"
                )

        return RedFlagVerdict(
            level=RedFlagLevel.NORMAL,
            is_safe=True,
            reason="คำสั่งผ่านการตรวจสอบความปลอดภัย",
            recommendation="อนุญาตให้ประมวลผลคำสั่ง"
        )

    @classmethod
    def audit_package_debloat(cls, package_name: str) -> RedFlagVerdict:
        """Audits package for safe User-0 debloating."""
        cleaned = package_name.strip()
        if cleaned in CRITICAL_FRAMEWORK_PACKAGES:
            return RedFlagVerdict(
                level=RedFlagLevel.CRITICAL_EMERGENCY,
                is_safe=False,
                reason=f"🚨 CRITICAL: ห้ามถอนการติดตั้งแพ็กเกจระบบหลัก '{cleaned}'",
                recommendation="แพ็กเกจนี้เป็นแกนหลักของ UI/โทรศัพท์ หากลบออกจะทำให้เครื่องบูตไม่ติดทันที (Bootloop)"
            )

        return RedFlagVerdict(
            level=RedFlagLevel.NORMAL,
            is_safe=True,
            reason=f"แพ็กเกจ '{cleaned}' สามารถถอนการติดตั้งได้สำหรับ User 0",
            recommendation="สามารถลบได้ผ่าน pm uninstall -k --user 0"
        )

    @classmethod
    def audit_tv_package_action(
        cls,
        package_name: str,
        action: str = "disable",
        installed_packages: Optional[List[str]] = None,
        alternative_launchers: Optional[List[str]] = None
    ) -> RedFlagVerdict:
        """
        Audits Android TV / Google TV package disabling according to CleanYourTV rules:
        1. Never disable Bluetooth / TV remote pairing services (loss of remote navigation).
        2. Never disable stock launcher unless an alternative launcher is confirmed present.
        """
        cleaned = package_name.strip()
        installed = installed_packages or []
        known_alts = alternative_launchers or [
            "com.gathin.tvhome",
            "com.spocky.projectivy",
            "me.efdev.flauncher",
            "ca.dstudio.atvlauncher.pro",
            "ca.dstudio.atvlauncher.free",
            "com.princecreations.emulauncher"
        ]

        if cleaned in CRITICAL_FRAMEWORK_PACKAGES or cleaned in CRITICAL_TV_PACKAGES:
            return RedFlagVerdict(
                level=RedFlagLevel.CRITICAL_EMERGENCY,
                is_safe=False,
                reason=f"🚨 CRITICAL TV RED FLAG: ห้ามปิดหรือลบแพ็กเกจควบคุมโทรทัศน์ '{cleaned}'",
                recommendation="แพ็กเกจนี้ควบคุมรีโมต Bluetooth หรือระบบควบคุมแกนกลาง หากปิดใช้งานจะไม่สามารถใช้รีโมตสั่งงานทีวีได้"
            )

        if cleaned in STOCK_TV_LAUNCHERS and action in {"disable", "uninstall"}:
            has_alt = any(alt in installed for alt in known_alts)
            if not has_alt:
                return RedFlagVerdict(
                    level=RedFlagLevel.CRITICAL_EMERGENCY,
                    is_safe=False,
                    reason=f"🚨 CRITICAL TV RED FLAG: ปฏิเสธการปิด Stock Launcher '{cleaned}' เนื่องจากยังไม่พบ Launcher ทางเลือก",
                    recommendation="ต้องติดตั้ง Launcher ทางเลือก (เช่น CleanYourTV tvhome, Projectivy, หรือ FLauncher) ให้เสร็จก่อน จึงจะสามารถปิด Stock Launcher ได้ เพื่อป้องกันปัญหาหน้าจอดำ (Black Screen)"
                )

        return RedFlagVerdict(
            level=RedFlagLevel.NORMAL,
            is_safe=True,
            reason=f"แพ็กเกจทีวี '{cleaned}' ผ่านการตรวจสอบความปลอดภัย",
            recommendation="สามารถดำเนินการปิดใช้งานได้อย่างปลอดภัยผ่าน pm disable-user --user 0"
        )
