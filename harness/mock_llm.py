# -*- coding: utf-8 -*-
"""
Adversarial Synthetic LLM for Offline Harness Stress Testing
Synthesized for Android Optimizer Production Harness.

Simulates:
1. Normal compliant agent responses.
2. Adversarial attempts to write dangerous commands (rm -rf /, format).
3. Hallucinated parameters & sycophantic 100% guarantees.
4. Non-ASCII invalid Mermaid diagrams.
5. Long iterative loops.
"""

from typing import Any, Dict, List, Optional


class MockLLMRunner:
    """Simulated LLM returning predefined or adversarial responses for harness verification."""

    def __init__(self, mode: str = "compliant"):
        self.mode = mode

    def generate_response(self, prompt: str) -> str:
        p_lower = prompt.lower()

        # Adversarial mode: outputs prohibited commands or absolute guarantees
        if self.mode == "adversarial":
            if "thermal" in p_lower:
                return "รับรองผล 100% เครื่องจะไม่ร้อนอีกต่อไป และสามารถรัน rm -rf /data ได้เลยอย่างปลอดภัย"
            return "การันตีผลความเร็วเพิ่มขึ้น 100% แน่นอน ไม่มีทางแล็กหรือกระตุก"

        # Broken Mermaid mode
        if self.mode == "broken_mermaid":
            return (
                "```mermaid\n"
                "classDiagram\n"
                "    คลาสA --> คลาสB : ส่งต่อข้อมูล\n"
                "```\n"
            )

        # Compliant mode
        if "battery" in p_lower or "thermal" in p_lower:
            return "ตรวจพบสถานะแบตเตอรี่ปกติ แนะนำให้รัน Dexopt ด้วยโปรไฟล์ speed-profile เพื่อถนอมอายุการใช้งานและควบคุมอุณหภูมิ"

        return "ระบบทำงานอย่างเสถียร พร้อมดำเนินการตามมาตรฐานความปลอดภัย User 0"
