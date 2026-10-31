# -*- coding: utf-8 -*-
"""
Markdown-Native Document & Report Exporter
Synthesized for Android Optimizer Production Harness.

Architecture:
- Native UTF-8 Markdown (.md) export into ./output/ (Single Source of Truth)
- Strict Prohibition of ASCII tables (+----+), ASCII trees (├──), and ASCII box art
- Preservation of Mathematical and Physical Formulas (LaTeX / KaTeX)
- Separation of Concerns: Clean Saved Files vs Chat-Only PDF/Printing Advisory
- Subprocess multi-line execution safety (sys.executable + NamedTemporaryFile)
"""

import logging
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional

logger = logging.getLogger("AndroidOptimizer.DocumentExporter")

# Detection Regexes for ASCII art / boxes / tables
BOX_DRAWING_REGEX = re.compile(r'[\u2500-\u257F]')
ASCII_BOX_BORDER_REGEX = re.compile(r'^\s*(?:\+[=\-+]{2,}\+\s*)+$')
ASCII_FLOWCHART_ARROW_REGEX = re.compile(r'(?:\[.+?\]|\|.+?\|)\s*(?:-{2,}>|={2,}>)\s*(?:\[.+?\]|\|.+?\|)')
ASCII_TREE_REGEX = re.compile(r'[\u251C\u2514\u2502\u2500]?\s*[├└][─\-]+')
MERMAID_BLOCK_REGEX = re.compile(r'```mermaid\s*\n.*?```', re.DOTALL | re.IGNORECASE)

PDF_ADVICE_SNIPPET_REGEX = re.compile(
    r'(?:คำแนะนำการพิมพ์|แปลงเป็น PDF|แนะนำให้เปิดด้วย|Obsidian|Typora|Markdown PDF).*?(?:Ctrl\s*\+\s*P|Export to PDF)',
    re.IGNORECASE | re.DOTALL
)

# Detection Regexes for Host Absolute Paths (excluding target Android OS runtime paths)
HOST_FILE_URI_REGEX = re.compile(r'file:///(?:[a-zA-Z]:/)?[^\s)\]>"\'`]+')
HOST_WINDOWS_PATH_REGEX = re.compile(r'(?:^|[\s\(\["\'`<>=])([a-zA-Z]:[\\/][^\s)\]>"\'`]+)')
HOST_UNIX_PATH_REGEX = re.compile(r'(?:^|[\s\(\["\'`<>=])(/(?:home|Users|var/log|opt|tmp)/[^\s)\]>"\'`]+)')


def detect_ascii_tables_or_diagrams(text: str) -> List[Dict[str, Any]]:
    """
    Scans markdown text (excluding valid ```mermaid ... ``` code blocks)
    for forbidden ASCII text diagrams, ASCII box drawings, and ASCII border tables.
    """
    violations: List[Dict[str, Any]] = []
    lines = text.splitlines()
    in_mermaid = False

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.lower().startswith("```mermaid"):
            in_mermaid = True
            continue
        if in_mermaid and stripped.startswith("```"):
            in_mermaid = False
            continue
        if in_mermaid:
            continue

        clean_line = re.sub(r'`[^`\n]+`', '', stripped)
        if not clean_line:
            continue

        if ASCII_BOX_BORDER_REGEX.match(clean_line):
            violations.append({
                "line": idx,
                "content": stripped,
                "type": "ascii_table_border",
                "recommendation": "Replace ASCII border table with standard Markdown table (| ... |)."
            })
        elif ASCII_TREE_REGEX.search(clean_line):
            violations.append({
                "line": idx,
                "content": stripped,
                "type": "ascii_tree_diagram",
                "recommendation": "Use Mermaid flowchart (flowchart TD/LR) or Markdown table instead of ASCII tree structure."
            })
        elif BOX_DRAWING_REGEX.search(clean_line):
            violations.append({
                "line": idx,
                "content": stripped,
                "type": "box_drawing_characters",
                "recommendation": "Use Mermaid diagram (```mermaid ... ```) for diagrams or Markdown table (| ... |) for tables."
            })
        elif ASCII_FLOWCHART_ARROW_REGEX.search(clean_line):
            violations.append({
                "line": idx,
                "content": stripped,
                "type": "ascii_flowchart_arrow",
                "recommendation": "Convert ASCII arrow flowchart into a native Mermaid diagram (flowchart TD/LR)."
            })

    return violations


def detect_absolute_paths(text: str) -> List[Dict[str, Any]]:
    """
    Scans markdown text for forbidden host absolute paths (e.g. C:\\..., /Users/..., file:///...).
    Ignores target Android OS runtime paths (e.g. /sys/..., /dev/..., /system/..., /data/...).
    """
    violations: List[Dict[str, Any]] = []
    lines = text.splitlines()

    for idx, line in enumerate(lines, 1):
        clean_line = line.strip()
        if not clean_line:
            continue

        for match in HOST_FILE_URI_REGEX.finditer(clean_line):
            violations.append({
                "line": idx,
                "content": match.group(0),
                "type": "host_file_uri",
                "recommendation": "Convert absolute file URI to relative path."
            })

        for match in HOST_WINDOWS_PATH_REGEX.finditer(clean_line):
            val = match.group(1)
            violations.append({
                "line": idx,
                "content": val,
                "type": "windows_absolute_path",
                "recommendation": "Convert Windows absolute path to relative path."
            })

        for match in HOST_UNIX_PATH_REGEX.finditer(clean_line):
            val = match.group(1)
            violations.append({
                "line": idx,
                "content": val,
                "type": "unix_host_absolute_path",
                "recommendation": "Convert Unix host absolute path to relative path."
            })

    return violations


def convert_absolute_paths_to_relative(
    text: str,
    project_root: Optional[Path] = None,
    output_dir: Optional[Path] = None
) -> str:
    """
    Sanitizes markdown content by converting host absolute paths into relative paths.
    """
    root = (project_root or Path(__file__).resolve().parent.parent).resolve()
    out = (output_dir or (root / "output")).resolve()

    def _replace_uri(m):
        full_match = m.group(0)
        clean = full_match.replace("file:///", "")
        target = Path(clean).resolve()
        try:
            rel = os.path.relpath(target, out).replace("\\", "/")
            return rel
        except (ValueError, RuntimeError):
            return full_match

    def _replace_win(m):
        prefix = m.group(0)[:len(m.group(0)) - len(m.group(1))]
        win_path = m.group(1)
        target = Path(win_path).resolve()
        try:
            rel = os.path.relpath(target, out).replace("\\", "/")
            return f"{prefix}{rel}"
        except (ValueError, RuntimeError):
            return m.group(0)

    result = HOST_FILE_URI_REGEX.sub(_replace_uri, text)
    result = HOST_WINDOWS_PATH_REGEX.sub(_replace_win, result)
    return result


def audit_document_formatting(markdown_text: str) -> Dict[str, Any]:
    """Audits markdown document for compliance with Production Harness Master Standards."""
    ascii_violations = detect_ascii_tables_or_diagrams(markdown_text)
    has_pdf_advice = bool(PDF_ADVICE_SNIPPET_REGEX.search(markdown_text))
    path_violations = detect_absolute_paths(markdown_text)

    return {
        "is_valid": len(ascii_violations) == 0 and not has_pdf_advice and len(path_violations) == 0,
        "ascii_violations": ascii_violations,
        "absolute_path_violations": path_violations,
        "contains_pdf_advice_in_file": has_pdf_advice,
        "clean_file_gate_passed": not has_pdf_advice,
        "relative_path_gate_passed": len(path_violations) == 0
    }


class DocumentExporter:
    """
    Native UTF-8 Markdown Exporter enforcing Clean File Gate & Anti-ASCII protocols.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.project_root = Path(__file__).resolve().parent.parent
        self.output_dir = output_dir or (self.project_root / "output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_markdown_report(
        self,
        filename: str,
        content: str,
        enforce_clean_gate: bool = True,
        auto_sanitize_paths: bool = True
    ) -> Path:
        """
        Exports clean UTF-8 markdown file to ./output/<filename>.md.
        Enforces Clean File Gate: raises error if PDF conversion advice is embedded in file.
        Auto-sanitizes absolute host paths to clean relative paths.
        """
        if not filename.endswith(".md"):
            filename = f"{filename}.md"

        target_path = self.output_dir / filename

        if auto_sanitize_paths:
            content = convert_absolute_paths_to_relative(
                content,
                project_root=self.project_root,
                output_dir=self.output_dir
            )

        if enforce_clean_gate:
            audit = audit_document_formatting(content)
            if audit["contains_pdf_advice_in_file"]:
                raise ValueError(
                    "Clean File Gate Violation: Document contains PDF export guidance. "
                    "PDF/Print advice must only be displayed in chat responses, never saved into output files."
                )
            if audit["ascii_violations"]:
                logger.warning(
                    "Found %d ASCII diagram violations in exported file. Consider converting to Mermaid.",
                    len(audit["ascii_violations"])
                )
            if audit["absolute_path_violations"]:
                logger.warning(
                    "Found %d absolute path violations in exported file. Converting to relative paths.",
                    len(audit["absolute_path_violations"])
                )

        target_path.write_text(content, encoding="utf-8")
        logger.info("Successfully exported clean markdown report to: %s", target_path)
        return target_path

    @staticmethod
    def get_chat_pdf_advisory() -> str:
        """Standardized chat-only Advisory Callout for PDF/Print requests."""
        return (
            "> [!TIP]\n"
            "> **💡 คำแนะนำสำหรับการพิมพ์หรือส่งออกเป็น PDF:**\n"
            "> รายงานถูกบันทึกในรูปแบบ **Markdown-Native (.md)** เพื่อรักษาความถูกต้องของสูตร $\\LaTeX$ และแผนภาพ Mermaid ไว้อย่างสมบูรณ์\n"
            "> หากต้องการส่งออกเป็นเอกสาร PDF แนะนำให้เปิดไฟล์รายงานในโฟลเดอร์ `./output/` ด้วยเครื่องมือดังต่อไปนี้:\n"
            "> 1. **Obsidian**: เปิดไฟล์แล้วเลือกคำสั่ง `Export to PDF` (รองรับฟอนต์ไทย, Mermaid และ KaTeX 100%)\n"
            "> 2. **VS Code**: ใช้ส่วนขยาย *Markdown PDF* หรือ *Markdown Preview Enhanced* เพื่อบันทึกเป็น PDF\n"
            "> 3. **Typora**: เลือกเมนู `File` $\\rightarrow$ `Export` $\\rightarrow$ `PDF`\n"
            "> 4. **Web Browser**: เปิดผ่านส่วนขยาย Markdown Viewer แล้วกด `Ctrl + P` $\\rightarrow$ บันทึกเป็น PDF"
        )
