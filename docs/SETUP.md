# คู่มือติดตั้งเซิร์ฟเวอร์ SEVER GAME Prontera (rAthena)

เซิร์ฟเวอร์ Ragnarok Online บน [rAthena](https://github.com/rathena/rathena) โหมด Renewal, ผู้เล่นใหม่เกิดที่ Prontera
ทุกชื่อไฟล์/คีย์คอนฟิกในคู่มือนี้ตรวจกับซอร์ส rAthena ล่าสุดแล้ว และสคริปต์ฝั่ง Ubuntu ทดสอบติดตั้งจริงแล้ว

> ⚠️ ตัวเกม (Client / data.grf) เป็นลิขสิทธิ์ของ Gravity และ**ห้าม commit เข้า repo นี้** การเปิดเซิร์ฟสาธารณะมีความเสี่ยงด้านกฎหมาย ใช้เพื่อเรียนรู้/ทดสอบเป็นหลัก

## ภาพรวม

```
Client (Ragexe ที่แพตช์แล้ว)
   │ 6900                 │ 6121                 │ 5121
   ▼                      ▼                      ▼
login-server  ◄──►  char-server  ◄──►  map-server   (+ web-server 8888)
        └──────────── MariaDB: ragnarok + ragnarok_log ────────────┘
```

| พอร์ต | เซิร์ฟเวอร์ | ต้องเปิด firewall เมื่อให้คนอื่นเข้า |
|---|---|---|
| 6900 | login | ✅ |
| 6121 | char | ✅ |
| 5121 | map | ✅ |
| 3306 | MariaDB | ❌ ห้ามเปิดออกอินเทอร์เน็ต |

สเปกขั้นต่ำ: CPU 1 core, RAM 1 GB (แนะนำ 2 GB), ดิสก์ 500 MB

## โครงสร้าง repo

| Path | หน้าที่ |
|---|---|
| `.env.example` | ค่าตั้งต้นทั้งหมด (คัดลอกเป็น `.env` แล้วแก้) |
| `config/import/*` | คอนฟิกเฉพาะเซิร์ฟนี้ จะถูกคัดลอกไป `rathena/conf/import/` (rAthena โหลดไฟล์ในนี้ทับค่าเริ่มต้น จึงไม่ต้องแก้ไฟล์ต้นฉบับ) |
| `scripts/install-ubuntu.sh` | ติดตั้งแพ็กเกจ, clone rAthena, คอมไพล์ |
| `scripts/setup-db.sh` | สร้าง DB + user, import SQL, เปลี่ยนรหัส inter-server |
| `scripts/apply-config.sh` | เติมค่าจาก `.env` ลง `config/import/*` แล้ววางใน rAthena |
| `scripts/make-gm.sh` | ตั้ง group ให้ไอดี (เช่น GM 99) |
| `docs/COMMANDS.md` | รายการคำสั่ง @/# ที่ตรวจแล้ว |

---

## ทางที่ 1: Ubuntu 22.04 / 24.04 (แนะนำ)

```bash
# 1) โหลด repo นี้
git clone https://github.com/itpppc/SEVER-GAME-prontera.git
cd SEVER-GAME-prontera

# 2) ตั้งค่า: แก้ทุกค่าที่ขึ้นต้นด้วย CHANGE_ME (สคริปต์จะไม่ยอมรันถ้ายังไม่แก้)
cp .env.example .env
nano .env

# 3) ติดตั้งแพ็กเกจ + clone rAthena ไว้ที่ ./rathena + คอมไพล์ (ใช้เวลาหลายนาที)
scripts/install-ubuntu.sh

# 4) สร้างฐานข้อมูลและ import SQL (รันซ้ำได้ ไม่ลบข้อมูลเดิม)
scripts/setup-db.sh

# 5) วางคอนฟิก
scripts/apply-config.sh

# 6) เปิดเซิร์ฟ
cd rathena
./athena-start start --enlog   # log อยู่ที่ rathena/log/ · หยุด: ./athena-start stop · สถานะ: ./athena-start status
```

ค่าใน `.env` ที่ควรรู้

| คีย์ | ความหมาย |
|---|---|
| `DB_PASS` | รหัสผ่าน DB user `ragnarok` (ตั้งใหม่ ห้ามใช้ค่าตัวอย่าง) |
| `INTER_USER` / `INTER_PASS` | บัญชีที่ login/char/map ใช้คุยกัน แทน `s1`/`p1` ของ rAthena (ถ้าไม่เปลี่ยน ใครก็ล็อกอินเป็น server ได้) |
| `PUBLIC_IP` | IP ที่ client จะต่อเข้า char/map: `127.0.0.1` เล่นเครื่องเดียว, IP วง LAN ให้เพื่อนในบ้าน, Public IP ของ VPS ถ้าเปิดออกเน็ต |
| `PACKETVER` | วันที่ของ client exe (ค่าเริ่มต้น `20211103` ตามที่ rAthena แนะนำ) ต้องตรงกับ client ที่จะแพตช์ |
| `NEW_ACCOUNT` | `yes` = สมัครไอดีหน้าล็อกอินด้วย `_M`/`_F` ได้ |
| `RATHENA_REF` | branch/tag ของ rAthena ที่จะ build (ค่าเริ่มต้น `master`) |

ถ้า root ของ MariaDB ใช้รหัสผ่าน (ไม่ใช่ socket auth แบบค่าเริ่มต้นของ Ubuntu) ให้รันแบบ
`MYSQL_ADMIN="mysql -uroot -p" scripts/setup-db.sh`

เปลี่ยน `PACKETVER` ภายหลัง: แก้ `.env` แล้วรัน `scripts/install-ubuntu.sh --skip-apt` ใหม่

---

## ทางที่ 2: Windows (ทดสอบในเครื่อง)

### 2.1 โปรแกรมที่ต้องมี
1. **Visual Studio 2022 Community** ติ๊ก workload **Desktop development with C++**
2. **Git for Windows**
3. **MariaDB** (หรือ XAMPP ที่มี MariaDB + phpMyAdmin)
4. **Notepad++** สำหรับแก้คอนฟิก

### 2.2 โหลด rAthena
เปิด Git Bash แล้วรัน (URL เต็มต้องเป็นแบบนี้ คู่มือเดิมถูกตัดเหลือ `https://github.com`)
```bash
mkdir -p /c/ro-server && cd /c/ro-server
git clone https://github.com/rathena/rathena.git rathena
git clone https://github.com/itpppc/SEVER-GAME-prontera.git
```

### 2.3 ฐานข้อมูล
เปิด phpMyAdmin → แท็บ **SQL** แล้วรัน (เปลี่ยนรหัสผ่านก่อน; ไม่แนะนำให้ rAthena ใช้ `root` ไม่มีรหัส)
```sql
CREATE DATABASE ragnarok CHARACTER SET utf8mb4;
CREATE DATABASE ragnarok_log CHARACTER SET utf8mb4;
CREATE USER 'ragnarok'@'localhost' IDENTIFIED BY 'CHANGE_ME_db_password';
CREATE USER 'ragnarok'@'127.0.0.1' IDENTIFIED BY 'CHANGE_ME_db_password';
GRANT ALL PRIVILEGES ON ragnarok.* TO 'ragnarok'@'localhost', 'ragnarok'@'127.0.0.1';
GRANT ALL PRIVILEGES ON ragnarok_log.* TO 'ragnarok'@'localhost', 'ragnarok'@'127.0.0.1';
FLUSH PRIVILEGES;
```
แล้ว **Import** จาก `C:\ro-server\rathena\sql-files\` ตามลำดับ

| ฐานข้อมูล | ไฟล์ |
|---|---|
| `ragnarok` | `main.sql` → `web.sql` → `roulette_default_data.sql` |
| `ragnarok_log` | `logs.sql` |

เปลี่ยนบัญชี inter-server (แทน `s1`/`p1`):
```sql
UPDATE ragnarok.login SET userid = 'CHANGE_ME_inter_user', user_pass = 'CHANGE_ME_inter_pass'
WHERE account_id = 1 AND sex = 'S';
```

### 2.4 คอมไพล์
1. ดับเบิลคลิก `C:\ro-server\rathena\rAthena.sln`
2. แถบบนเลือก **Release** และ **x64**
3. ถ้าจะใช้ client วันที่อื่นที่ไม่ใช่ 2021-11-03: เปิด `src\custom\defines_pre.hpp` เพิ่ม `#define PACKETVER 20211103` (เปลี่ยนเป็นวันที่ของ client)
4. **Build → Build Solution** รอจนขึ้น `succeeded`
5. ได้ไฟล์ `login-server.exe`, `char-server.exe`, `map-server.exe`, `web-server.exe` และ `runserver.bat` ในโฟลเดอร์ `rathena`

### 2.5 คอนฟิก
คัดลอกทุกไฟล์จาก `SEVER-GAME-prontera\config\import\` ไปทับ `rathena\conf\import\`
แล้วเปิดแต่ละไฟล์แทนที่ `{{...}}` ด้วยค่าจริง

| ตัวแปร | ค่าตัวอย่าง |
|---|---|
| `{{DB_HOST}}` / `{{DB_PORT}}` | `127.0.0.1` / `3306` |
| `{{DB_NAME}}` / `{{LOG_DB_NAME}}` | `ragnarok` / `ragnarok_log` |
| `{{DB_USER}}` / `{{DB_PASS}}` | `ragnarok` / รหัสที่ตั้งใน 2.3 |
| `{{INTER_USER}}` / `{{INTER_PASS}}` | ค่าเดียวกับ UPDATE ใน 2.3 |
| `{{SERVER_NAME}}` | `Prontera` (ไม่เกิน 20 ตัวอักษร) |
| `{{PUBLIC_IP}}` | `127.0.0.1` |
| `{{NEW_ACCOUNT}}` | `yes` |

> ทำหลัง build (2.4) เพราะ build ครั้งแรกจะสร้าง `conf/import/` จาก `conf/import-tmpl/` ให้

### 2.6 เปิดเซิร์ฟ
ดับเบิลคลิก `rathena\runserver.bat` (เปิดหน้าต่าง login, char, web, map ให้ครบ) หรือเปิดเองทีละตัว: login → char → map
แต่ละตัวพร้อมเมื่อขึ้นคำว่า `ready` และ map-server ขึ้น `Map-server connected to char-server`

---

## 3. เตรียม Client

1. ใช้ kRO Clean Client (มี `data.grf`) + **Ragexe วันที่ตรงกับ `PACKETVER`** (ค่าเริ่มต้น 2021-11-03)
2. แพตช์ exe ด้วย **WARP** (ตัวใหม่) หรือ **NEMO** ให้มีอย่างน้อย
   - โหลด `clientinfo.xml` / sclientinfo ที่เรากำหนด (ไม่ใช้ IP ของ kRO)
   - Read Data Folder First
   - ปิดการเข้ารหัสรหัสผ่านฝั่ง client (ถ้าจะสมัครไอดีแบบ `_M`/`_F`)
   - **อย่าติ๊ก Disable Packet Encryption** — rAthena เปิด `PACKET_OBFUSCATION` และมีคีย์ของ client 2021-11-03 อยู่แล้ว ถ้าปิดฝั่งเดียวจะเข้าไม่ได้
3. `data/clientinfo.xml`
```xml
<?xml version="1.0" encoding="euc-kr" ?>
<clientinfo>
  <servicetype>korea</servicetype>
  <servertype>primary</servertype>
  <connection>
    <display>Prontera</display>
    <address>127.0.0.1</address>  <!-- = PUBLIC_IP ของเซิร์ฟ -->
    <port>6900</port>
    <version>1</version>          <!-- rAthena ไม่ได้ตรวจค่านี้ -->
    <langtype>1</langtype>
  </connection>
</clientinfo>
```
> คู่มือเดิมบอกว่า `<version>` ต้องตรงกับ `src/config/packets.h` — ไม่จริง ไฟล์จริงคือ `src/config/packets.hpp` และสิ่งที่ต้องตรงคือ **วันที่ของ exe กับ `PACKETVER`** ไม่ใช่เลข version

## 4. ล็อกอินครั้งแรก + ตั้ง GM

1. หน้าล็อกอินพิมพ์ `admin_M` (ชาย) หรือ `admin_F` (หญิง) + รหัสผ่านใหม่ (≥ 4–6 ตัวตาม client) ระบบจะสร้างไอดี `admin` ให้ (ต้อง `NEW_ACCOUNT=yes`)
2. ล็อกอินอีกครั้งด้วย `admin` (ไม่มี `_M`)
3. ครั้งแรกจะถูกให้ตั้ง **PIN** (rAthena เปิด `pincode_enabled` ไว้) ถ้าไม่ต้องการ เพิ่ม `pincode_enabled: no` ใน `config/import/char_conf.txt`
4. ตั้งเป็น Admin
   - Ubuntu: `scripts/make-gm.sh admin 99`
   - Windows: `UPDATE ragnarok.login SET group_id = 99 WHERE userid = 'admin';`
5. ออกแล้วเข้าใหม่ ทดสอบ `@go 0`, `@item 501 10`
6. เปิดให้คนอื่นเข้าแล้ว แนะนำตั้ง `NEW_ACCOUNT=no` และทำหน้าสมัครแยก

คำสั่งทั้งหมดดูที่ [COMMANDS.md](COMMANDS.md)

## 5. ปรับแต่งที่ใช้บ่อย

| อยากปรับ | ไฟล์ (วางใน `conf/import/`) | ตัวอย่าง |
|---|---|---|
| เรต EXP | `battle_conf.txt` | `base_exp_rate: 1000` (100 = x1) / `job_exp_rate: 1000` |
| เรตดรอป | `battle_conf.txt` | `item_rate_common: 500`, `item_rate_card: 100` |
| จุดเกิดตัวละครใหม่ | `char_conf.txt` | `start_point: prontera,156,191` (ตั้งไว้แล้ว) |
| Pre-Renewal (คลาสสิก) | คอมไพล์ใหม่ | Ubuntu: เพิ่ม `--enable-prere=yes` ใน `./configure`; Windows: `#define PRERE` ใน `src/custom/defines_pre.hpp` |

แก้ battle_conf แล้วใช้ `@reloadbattleconf` ในเกมได้เลย

## 6. แก้ปัญหา

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| char ขึ้น `Can not connect to login-server` หรือ map ต่อ char ไม่ได้ | `INTER_USER`/`INTER_PASS` ใน conf ไม่ตรงกับแถว `account_id = 1` ในตาราง `login` |
| `Access denied for user 'ragnarok'` | รหัส DB ใน `inter_conf.txt` ไม่ตรง หรือยังไม่ได้สร้าง user ที่ `127.0.0.1` |
| `Table 'ragnarok.xxx' doesn't exist` | ยัง import SQL ไม่ครบ (`main.sql`, `web.sql`, `logs.sql`) |
| เข้าเกมได้แต่ค้างหลังเลือกเซิร์ฟ | `PUBLIC_IP` ผิด หรือไม่ได้เปิดพอร์ต 6121/5121 |
| ล็อกอินแล้ว disconnect ทันที | วันที่ client exe ≠ `PACKETVER` หรือแพตช์ปิด packet encryption |
| พิมพ์ `_M` แล้ว "Rejected from server" | `new_account` เป็น `no` หรือ client ยังเข้ารหัสรหัสผ่านอยู่ |

ดูข้อความ error ในหน้าต่าง console ของแต่ละเซิร์ฟ (Ubuntu: เปิดด้วย `--enlog` แล้วดู `rathena/log/*.log`)

## 7. สิ่งที่แก้จากคู่มือเดิม

| เดิม | ที่ถูกต้อง |
|---|---|
| `git clone https://github.com .` | `git clone https://github.com/rathena/rathena.git` |
| import แค่ `main.sql` + `logs.sql` | ต้องมี `web.sql` และ `roulette_default_data.sql` ด้วย |
| `inter_athena.conf` ใส่ `sql_userid` / `sql_password` | ไม่มีคีย์นี้ ใช้ `login_server_id/pw`, `char_server_id/pw`, `map_server_id/pw`, `web_server_id/pw`, `ipban_db_id/pw`, `log_db_id/pw` (ใส่ใน `conf/import/inter_conf.txt`) |
| `inter-server.conf` | ปัจจุบันคือ `conf/inter_server.yml` |
| `src/config/packets.h` | `src/config/packets.hpp` (ค่าเริ่มต้น `PACKETVER 20211103`) |
| `<version>55</version>` ต้องตรง server | rAthena ไม่ตรวจ ให้ตรงที่วันที่ exe |
| ติ๊ก Disable Packet Encryption | ไม่ควร (ดูหัวข้อ 3) |
| `_M`/`_F` ใช้ได้ทันที | ค่าเริ่มต้น `new_account: no` ต้องเปิดก่อน |
| ไม่ได้พูดถึง `s1`/`p1` | ต้องเปลี่ยน ไม่งั้นเป็นช่องโหว่ |
| ได้ exe 3 ตัว | 4 ตัว (มี `web-server.exe`) |
