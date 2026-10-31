# -*- coding: utf-8 -*-
"""
Token Optimization & Test Control Guardian
Synthesized for Android Optimizer Production Harness.

Enforces:
1. Zero-Test by default (Implementation-Only Mode).
2. Explicit Opt-In Trigger Verification ("write test", "unit test", "test this", "run tests", "generate test suite").
3. Minimal Context & Execution Log Suppression flags (pytest -q --tb=short --maxfail=1).
4. Strict Auto-Fix Loop Limit: Maximum 2 attempts before immediate stop.
5. Lightweight Verification Alternatives (Static linters / type checkers).
"""

from typing import Any, Dict, List, Optional

TRIGGER_KEYWORDS: List[str] = [
    "write test",
    "unit test",
    "test this",
    "run tests",
    "generate test suite",
    "run test",
    "เขียนเทส",
    "รันเทส",
    "ทดสอบระบบ"
]

SUPPRESSED_COMMANDS: Dict[str, str] = {
    "python": "pytest {path} -q --tb=short --maxfail=1",
    "bash": "bash {path}",
}

STATIC_CHECKERS: Dict[str, List[str]] = {
    "python": ["ruff check .", "mypy --quick ."],
    "bash": ["shellcheck {path}"]
}

MAX_AUTO_FIX_ATTEMPTS: int = 2


class TestControlGuardian:
    """Guardian enforcing the strict token optimization and test execution directive."""

    def __init__(self, max_auto_fix_attempts: int = MAX_AUTO_FIX_ATTEMPTS):
        self.max_auto_fix_attempts = max_auto_fix_attempts
        self.current_attempt = 0

    @staticmethod
    def is_testing_triggered(prompt: str) -> bool:
        """Determines if prompt explicitly opts into testing mode."""
        prompt_lower = prompt.lower()
        return any(keyword.lower() in prompt_lower for keyword in TRIGGER_KEYWORDS)

    @staticmethod
    def get_suppressed_command(language: str, path: str = "") -> str:
        """Returns the token-suppressed test command for the specified language."""
        lang_key = language.lower()
        template = SUPPRESSED_COMMANDS.get(lang_key, SUPPRESSED_COMMANDS["python"])
        return template.format(path=path or "<path>")

    @staticmethod
    def get_static_checkers(language: str) -> List[str]:
        """Returns lightweight static checkers and linters as alternatives to heavy unit tests."""
        return STATIC_CHECKERS.get(language.lower(), [])

    def record_attempt(self) -> Dict[str, Any]:
        """Records an auto-fix attempt and checks if the hard loop limit has been exceeded."""
        self.current_attempt += 1
        allowed = self.current_attempt <= self.max_auto_fix_attempts
        return {
            "attempt": self.current_attempt,
            "max_allowed": self.max_auto_fix_attempts,
            "allowed": allowed,
            "must_stop": not allowed,
            "message": (
                f"Attempt {self.current_attempt} of {self.max_auto_fix_attempts}"
                if allowed
                else f"Hard stop triggered: Maximum {self.max_auto_fix_attempts} auto-fix attempts reached. Reverting broken test changes."
            )
        }

    def reset_attempts(self) -> None:
        self.current_attempt = 0
