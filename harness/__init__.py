# -*- coding: utf-8 -*-
"""
Android Optimizer Production Harness Package
Synthesized according to Production Harness Master Standards.
"""

from .cache import DualLayerCache
from .verifier import GroundingOracle
from .mermaid_guardian import MermaidUnicodeGuardian
from .document import (
    DocumentExporter,
    audit_document_formatting,
    convert_absolute_paths_to_relative,
    detect_absolute_paths,
)
from .red_flag import EmergencyRedFlagInterceptor, RedFlagLevel, RedFlagVerdict
from .persona_router import PersonaRouter, PersonaTier
from .adb_interface import ADBInterface
from .evaluator import BenchmarkEvaluator
from .test_guardian import TestControlGuardian
from .soc_profile import SoCProfileManager
from .tv_manager import TVManager

__version__ = "2.2.0"
__all__ = [
    "DualLayerCache",
    "GroundingOracle",
    "MermaidUnicodeGuardian",
    "DocumentExporter",
    "audit_document_formatting",
    "detect_absolute_paths",
    "convert_absolute_paths_to_relative",
    "EmergencyRedFlagInterceptor",
    "RedFlagLevel",
    "RedFlagVerdict",
    "PersonaRouter",
    "PersonaTier",
    "ADBInterface",
    "BenchmarkEvaluator",
    "TestControlGuardian",
    "SoCProfileManager",
    "TVManager",
]
