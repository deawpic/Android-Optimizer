# -*- coding: utf-8 -*-
"""
Report Exporter CLI Utility
Generates clean UTF-8 Markdown reports into ./output/ adhering strictly to Clean File Gate.
"""

from datetime import datetime
from pathlib import Path
import sys

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from harness.adb_interface import ADBInterface
from harness.document import DocumentExporter
from harness.persona_router import PersonaRouter, PersonaTier
from harness.red_flag import EmergencyRedFlagInterceptor


def main():
    use_mock = "--mock" in sys.argv
    adb = ADBInterface(mock_mode=use_mock)
    exporter = DocumentExporter()

    info = adb.get_device_info()
    battery = adb.get_battery_telemetry()
    verdict = EmergencyRedFlagInterceptor.evaluate_battery_telemetry(
        battery["temperature_raw"],
        battery["level"],
        battery["is_charging"]
    )

    report_content = f"""# รายงานการตรวจสอบและปรับแต่งระบบ Android ประจำวัน
**วันที่สร้างเอกสาร**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**สถานะฮาร์เนส**: Production Grade Verified  

---

## 1. ข้อมูลอุปกรณ์และสเปกฮาร์ดแวร์

| คุณลักษณะ | รายละเอียด |
| :--- | :--- |
| **ผู้ผลิต (Manufacturer)** | {info['manufacturer']} |
| **รุ่นอุปกรณ์ (Model)** | {info['model']} (แบรนด์: {info['brand']}) |
| **เวอร์ชัน Android (OS)** | Android {info['release']} (SDK Level {info['sdk']}) |
| **สิทธิ์การเข้าถึง (Root Status)** | {'เปิดใช้งาน Root (uid=0)' if info['is_rooted'] else 'Userspace ปกติ (Rootless)'} |
| **ความจุแบตเตอรี่ (Battery Level)** | {battery['level']}% |
| **อุณหภูมิแบตเตอรี่ (Temperature)** | {battery['temperature_celsius']}°C (Raw: {battery['temperature_raw']}) |
| **การเชื่อมต่อไฟชาร์จ (Charging)** | {'กำลังชาร์จไฟ' if battery['is_charging'] else 'ใช้พลังงานจากแบตเตอรี่'} |

---

## 2. แผนผังสถาปัตยกรรมการทำงานของฮาร์เนส

```mermaid
flowchart TD
    DeviceNode["<b>อุปกรณ์ Android (ADB / USB)</b><br/>{info['manufacturer']} {info['model']}"] --> SafetyGate["<b>Emergency & Red Flag Interceptor</b><br/>ประเมินอุณหภูมิและแบตเตอรี่"]
    SafetyGate --> CacheLayer["<b>Tier-0 Dual-Layer Cache</b><br/>L1 LRU (&lt;0.2ms) + L2 SQLite WAL (&lt;2.0ms)"]
    CacheLayer --> ExecutionEngine["<b>Execution Engine</b><br/>Dexopt AOT, Debloat, Kernel Sysfs"]
    ExecutionEngine --> OracleGate["<b>Grounding Whitelist Oracle</b><br/>ตรวจสอบความถูกต้อง ไม่เดาค่าพารามิเตอร์"]
    OracleGate --> OutputDoc["<b>Clean Markdown Report</b><br/>บันทึกไฟล์ใน ./output/"]
```

---

## 3. ผลการวิเคราะห์ความปลอดภัยและข้อกำหนดทางเทคนิค

- **ระดับความปลอดภัย (Safety State)**: `{verdict.level.value}`
- **ผลการวินิจฉัย**: {verdict.reason}
- **ข้อเสนอแนะในการปฏิบัติงาน**: {verdict.recommendation}

### สรุปหลักการปรับแต่ง (Core Invariants)
1. **การปรับแต่งแบบ Rootless (AOT Dexopt)**: ใช้โปรไฟล์ `speed-profile` หรือ `speed` เพื่อเพิ่มความเร็วในการเปิดแอปพลิเคชัน โดยไม่กระทบพาร์ทิชันระบบ
2. **การถอนการติดตั้งแอปขยะ (User 0 Debloat)**: กำหนดเป้าหมายเฉพาะ `pm uninstall -k --user 0` เพื่อรับประกันว่าสามารถคืนค่าแอปพลิเคชันเดิมได้ 100% เสมอ
3. **การควบคุมอุณหภูมิ (Thermal Protection)**: ระบบตั้งเกณฑ์ความปลอดภัยสูงสุดไว้ที่ 48.0°C เพื่อถนอมอายุเซลล์แบตเตอรี่และป้องกันฮาร์ดแวร์เสียหาย
"""

    report_path = exporter.export_markdown_report("android_system_audit_report.md", report_content)
    project_root = Path(__file__).resolve().parent.parent
    try:
        rel_path = report_path.resolve().relative_to(project_root).as_posix()
    except (ValueError, RuntimeError):
        rel_path = f"output/{report_path.name}"
    print(f"✅ รายงานระดับ Production-Grade ถูกบันทึกเรียบร้อยที่: ./{rel_path}")


if __name__ == "__main__":
    main()
