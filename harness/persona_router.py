# -*- coding: utf-8 -*-
"""
Adaptive 3-Tier Persona Routing for Android Optimization Harness
Synthesized for Android Optimizer Production Harness.

Tier 1: Kernel & AOSP Architecture Lead (IRAC / Technical Deep-Dive)
Tier 2: Android Developer & Power User (SOAP Note / Step-by-Step Implementation)
Tier 3: General Smartphone User & Gamer (Layman / Safety-First / Disclaimers)
"""

from enum import Enum
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("AndroidOptimizer.PersonaRouter")


class PersonaTier(str, Enum):
    TIER_1_EXPERT = "TIER_1_EXPERT"       # Kernel / AOSP Architect
    TIER_2_DEVELOPER = "TIER_2_DEVELOPER" # Android Dev / Power User
    TIER_3_USER = "TIER_3_USER"           # General Smartphone User


class PersonaRouter:
    """
    Routes output tone, depth, technical terminology, and layout according to target persona.
    Includes proactive evidence-on-demand inquiries at footer.
    """

    PROACTIVE_EVIDENCE_PROMPT = (
        "\n\n---\n"
        "💡 **Proactive Evidence-on-Demand**: "
        "ต้องการให้สืบค้นค่าพารามิเตอร์ Kernel Sysfs เพิ่มเติม, ตรวจสอบรายชื่อแพ็กเกจ OEM เฉพาะรุ่น "
        "หรือวิเคราะห์ Trace กราฟฟิก Skia/Vulkan เชิงลึกหรือไม่?"
    )

    @staticmethod
    def detect_persona_tier(prompt: str) -> PersonaTier:
        """Determines persona tier based on vocabulary in the prompt."""
        p_lower = prompt.lower()
        if any(w in p_lower for w in ["kernel", "sysfs", "governor", "schedutil", "zram", "kgsl", "irac", "devfreq", "cgroup"]):
            return PersonaTier.TIER_1_EXPERT
        if any(w in p_lower for w in ["adb", "debloat", "root", "magisk", "developer", "soap", "package", "dexopt"]):
            return PersonaTier.TIER_2_DEVELOPER
        return PersonaTier.TIER_3_USER

    @classmethod
    def format_response(
        cls,
        tier: PersonaTier,
        title: str,
        content_body: str,
        technical_data: Optional[Dict[str, Any]] = None,
        recommendation: str = ""
    ) -> str:
        """Formats the response according to the chosen Persona Tier."""
        if tier == PersonaTier.TIER_1_EXPERT:
            return cls._format_tier_1_expert(title, content_body, technical_data, recommendation)
        elif tier == PersonaTier.TIER_2_DEVELOPER:
            return cls._format_tier_2_developer(title, content_body, technical_data, recommendation)
        else:
            return cls._format_tier_3_user(title, content_body, technical_data, recommendation)

    @classmethod
    def _format_tier_1_expert(
        cls,
        title: str,
        content_body: str,
        technical_data: Optional[Dict[str, Any]],
        recommendation: str
    ) -> str:
        """IRAC Framework: Issue, Rule/Mechanism, Analysis, Conclusion."""
        lines = [
            f"## 🏛️ [Tier 1: Architecture Review] {title}",
            "",
            "### 1. Issue & Hardware Constraints",
            content_body,
            "",
            "### 2. AOSP & Linux Kernel Mechanisms",
            "การปรับแต่งมุ่งเน้นการลด Scheduling Latency, ปรับแต่ง I/O Barriers, และการจัดสรร ZRAM Compaction",
        ]
        if technical_data:
            lines.extend([
                "",
                "### 3. Quantitative Kernel Telemetry",
                "| Subsystem | Parameter / Path | Configured Value | Impact |",
                "| :--- | :--- | :--- | :--- |",
            ])
            for k, v in technical_data.items():
                lines.append(f"| Kernel / HW | `{k}` | `{v}` | Deterministic |")

        lines.extend([
            "",
            "### 4. Technical Conclusion & Invariant Gates",
            recommendation or "รักษา Execution Boundary และตรวจสอบ Sysfs node permissions ก่อน commit.",
            cls.PROACTIVE_EVIDENCE_PROMPT
        ])
        return "\n".join(lines)

    @classmethod
    def _format_tier_2_developer(
        cls,
        title: str,
        content_body: str,
        technical_data: Optional[Dict[str, Any]],
        recommendation: str
    ) -> str:
        """SOAP Note Framework: Subjective, Objective, Assessment, Plan."""
        lines = [
            f"## 🛠️ [Tier 2: Developer & Power User Guide] {title}",
            "",
            "### 📋 S (Subjective): System Diagnostics",
            content_body,
            "",
            "### 📊 O (Objective): Telemetry & Package Data",
        ]
        if technical_data:
            lines.extend([
                "| Item | Value |",
                "| :--- | :--- |",
            ])
            for k, v in technical_data.items():
                lines.append(f"| **{k}** | `{v}` |")
        else:
            lines.append("ระบบทำงานผ่าน ADB shell และ Userspace services.")

        lines.extend([
            "",
            "### ⚙️ A (Assessment): Optimization Opportunities",
            "การรัน AOT Dexopt และ Debloat ช่วยคืนพื้นที่หน่วยความจำและลด Background Wakelocks",
            "",
            "### 🚀 P (Plan): Implementation & Rollback Steps",
            recommendation or "รันคำสั่งตามลำดับ และเก็บไฟล์สำรอง baseline ทุกครั้งก่อนเริ่มกระบวนการ",
            cls.PROACTIVE_EVIDENCE_PROMPT
        ])
        return "\n".join(lines)

    @classmethod
    def _format_tier_3_user(
        cls,
        title: str,
        content_body: str,
        technical_data: Optional[Dict[str, Any]],
        recommendation: str
    ) -> str:
        """Layman-Friendly, High-Safety, Clear Warnings."""
        lines = [
            f"## 📱 [คู่มือสำหรับผู้ใช้งานทั่วไป] {title}",
            "",
            "### 💡 คำอธิบายเข้าใจง่าย",
            content_body,
            "",
            "### 🛡️ ข้อควรระวังและความปลอดภัย",
            "- การปรับแต่งทั้งหมดนี้ทำงานผ่านโหมด User 0 ไม่กระทบไฟล์ระบบหลัก",
            "- หากต้องการคืนค่าเดิม สามารถทำได้ทันทีด้วยปุ่มหรือสคริปต์ Rollback",
            "- **คำเตือน**: ห้ามปรับแต่งขณะเครื่องร้อนจัด หรือแบตเตอรี่เหลือน้อยกว่า 15%",
            "",
            "### 🎯 คำแนะนำการใช้งาน",
            recommendation or "กดรันสคริปต์อัตโนมัติ และรีสตาร์ทเครื่องหนึ่งครั้งเพื่อให้การตั้งค่าทำงานเต็มประสิทธิภาพ",
            "",
            "> [!NOTE]\n"
            "> *ข้อสงวนสิทธิ์: ผลลัพธ์ความเร็วขึ้นอยู่กับรุ่นโทรศัพท์และสภาพแบตเตอรี่ของท่าน*"
        ]
        return "\n".join(lines)
