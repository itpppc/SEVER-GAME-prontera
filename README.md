# SEVER GAME Prontera

เซิร์ฟเวอร์ Ragnarok Online ธีม Prontera บน [rAthena](https://github.com/rathena/rathena) (Renewal, ผู้เล่นใหม่เกิดที่ Prontera)

Repo นี้เก็บเฉพาะ **คอนฟิก สคริปต์ติดตั้ง และเอกสาร** ของเซิร์ฟเรา ตัว rAthena จะถูก clone มาไว้ที่ `./rathena` ตอนติดตั้ง (ไม่ commit) และ **ไม่มีไฟล์ client**

## เริ่มเร็ว (Linux: Ubuntu / Amazon Linux)

```bash
cp .env.example .env && nano .env   # แก้ทุกค่า CHANGE_ME
scripts/install.sh           # แพ็กเกจ + clone + compile
scripts/setup-db.sh                 # DB + import SQL + บัญชี inter-server
scripts/apply-config.sh             # วางคอนฟิกลง rathena/conf/import
cd rathena && ./athena-start start --enlog
```

## เอกสาร

- [docs/SETUP.md](docs/SETUP.md) — คู่มือติดตั้งละเอียด Ubuntu + Windows, client, GM, แก้ปัญหา
- [docs/COMMANDS.md](docs/COMMANDS.md) — คำสั่ง @/# ที่ตรวจกับ rAthena แล้ว พร้อมระดับสิทธิ์
- [docs/CLIENT.md](docs/CLIENT.md) — ติดตั้งและแพตช์ตัวเกม (client 2021-11-03) บน Windows ทีละขั้น
- [installer/Install-Prontera.bat](installer/Install-Prontera.bat) — ตัวติดตั้งตัวเกมคลิกเดียวบน Windows (โหลดจากต้นทาง แพตช์ และสร้างไอคอนให้เอง) แจกให้ผู้เล่นได้
