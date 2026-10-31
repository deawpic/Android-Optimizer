# -*- coding: utf-8 -*-
"""
SoC Hardware Profiles & Low-Level Tuning Manager
Synthesized for Android Optimizer Production Harness.

Features:
1. Grounded SoC Profiles (Qualcomm Snapdragon 8 Gen 3/2, MediaTek Dimensity 9300, Google Tensor G3).
2. Hardware cluster core topologies and schedutil rate limits.
3. GPU governors, bus scaling, and Adreno/Mali parameters.
4. Memory & ZRAM compression profiles (lz4, zram disksize ratio, swappiness).
5. Deterministic platform code resolution and lookup.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("AndroidOptimizer.SoCProfileManager")


class SoCProfileManager:
    """
    Manager for loading, caching, and querying verified SoC profiles
    and device-specific kernel/GPU tuning parameters.
    """

    def __init__(self, profiles_path: Optional[Path] = None):
        self.profiles_path = profiles_path or (Path(__file__).parent / "soc_profiles.json")
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._platform_lookup: Dict[str, str] = {}
        self._load_profiles()

    def _load_profiles(self) -> None:
        """Loads SoC profiles from the json database."""
        if not self.profiles_path.exists():
            logger.warning("SoC profiles database not found at: %s", self.profiles_path)
            return

        try:
            content = self.profiles_path.read_text(encoding="utf-8")
            data = json.loads(content)
            db = data.get("soc_database", [])
            for entry in db:
                soc_id = entry.get("soc_id")
                if soc_id:
                    self._profiles[soc_id] = entry
                    for code in entry.get("platform_codes", []):
                        self._platform_lookup[code.lower()] = soc_id
        except Exception as e:
            logger.error("Failed to parse SoC profiles database: %s", e)

    def resolve_soc_by_platform(self, platform_string: str) -> Optional[str]:
        """Resolves SoC ID from platform string (e.g. 'sm8650', 'pineapple', 'mt6989')."""
        if not platform_string:
            return None

        p_lower = platform_string.lower().strip()
        # Direct lookup
        if p_lower in self._platform_lookup:
            return self._platform_lookup[p_lower]

        # Substring / partial match
        for code, soc_id in self._platform_lookup.items():
            if code in p_lower:
                return soc_id

        return None

    def get_profile(self, soc_id_or_platform: str) -> Optional[Dict[str, Any]]:
        """Retrieves full profile by SoC ID or platform code."""
        if soc_id_or_platform in self._profiles:
            return self._profiles[soc_id_or_platform]

        resolved = self.resolve_soc_by_platform(soc_id_or_platform)
        if resolved and resolved in self._profiles:
            return self._profiles[resolved]

        return None

    def get_cpu_tuning(self, soc_id_or_platform: str) -> Optional[Dict[str, Any]]:
        """Returns CPU cluster architecture and governor tuning."""
        prof = self.get_profile(soc_id_or_platform)
        return prof.get("cpu_architecture") if prof else None

    def get_gpu_tuning(self, soc_id_or_platform: str) -> Optional[Dict[str, Any]]:
        """Returns GPU family, governor, and sysfs parameters."""
        prof = self.get_profile(soc_id_or_platform)
        return prof.get("gpu_architecture") if prof else None

    def get_memory_tuning(self, soc_id_or_platform: str) -> Optional[Dict[str, Any]]:
        """Returns ZRAM algorithm, ratio, and swappiness settings."""
        prof = self.get_profile(soc_id_or_platform)
        return prof.get("memory_tuning") if prof else None

    def list_supported_socs(self) -> List[Dict[str, str]]:
        """Lists all supported SoC IDs and commercial names."""
        return [
            {
                "soc_id": soc_id,
                "commercial_name": data.get("commercial_name", soc_id),
                "vendor": data.get("vendor", "Unknown")
            }
            for soc_id, data in self._profiles.items()
        ]
