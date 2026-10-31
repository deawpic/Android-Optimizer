# รายงานผลการปรับแต่งระบบ Xiaomi Redmi 9A (M2006C3MT) - อัปเดตล่าสุด
**วันที่และเวลา**: 2026-11-01 01:29:15  
**หมายเลขอุปกรณ์ (Serial)**: `FQWOLBKBEAAAOV79`  
**รหัสโมเดล**: Xiaomi M2006C3MT (`angelica_global` / แบรนด์: Redmi)  
**เวอร์ชันระบบ**: Android 10 (MIUI 12 / SDK 29)  
**การปรับแต่งล่าสุด**: คอมไพล์ AOT Speed Mode ให้แอปที่เพิ่งติดตั้งใหม่ (`com.movies037.mobile`)

---

## 1. ผลการปรับแต่งแอปที่ติดตั้งใหม่ (New App Optimization)

| รายการ | รายละเอียด |
| :--- | :--- |
| **ชื่อแพ็กเกจ (Package ID)** | `com.movies037.mobile` |
| **ชื่อแอปพลิเคชัน** | 037HD (แอปดูภาพยนตร์) |
| **เวอร์ชัน (Version)** | 1.0.0 |
| **สถานะการคอมไพล์เดิม** | `speed-profile` (บางส่วน) |
| **สถานะการคอมไพล์ใหม่** | **`arm: [status=speed]` (Full Native Machine Code 100%)** |
| **ผลลัพธ์ที่ได้** | โหลดแคตตาล็อกหนังเร็วขึ้น เริ่มเล่นวิดีโอทันที ไม่กระตุกจาก JIT Overhead |

---

## 2. รายชื่อแอปทั้งหมดที่ผ่านการคอมไพล์ Full AOT Speed Mode
1. **ระบบหลักและ Launcher**: `com.miui.home`, `com.android.systemui`, `com.android.settings`
2. **การสื่อสารและเว็บ**: `com.android.chrome`, `com.google.android.apps.messaging`, `com.google.android.gm`
3. **แอปส่วนตัวและความบันเทิง**: `com.movies037.mobile`, `com.tvth.mobile`, `gps.speedometer.digihud.odometer`, `app.revanced.android.gms`
