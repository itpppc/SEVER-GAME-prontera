# เนื้อหารามเกียรติ์ ระยะ 1 (ฝั่งเซิร์ฟเวอร์)

ภาพตัวอย่างแนวทาง UI: https://claude.ai/artifact/CRCaYSMUBPE3chT4hZCa29

## มีอะไรบ้าง

| ส่วน | ไฟล์ | รายละเอียด |
|---|---|---|
| ไอเทม 11 ชิ้น (ID 990000–990010) | `custom/db/item_db.yml` | น้ำมนต์อโยธยา, สมุนไพรหิมพานต์, โอสถสังกรณีตรีชวา (ชุบชีวิต), ศรพรหมาสตร์, ตรีเพชรหนุมาน, คทากุมภกรรณ, กริชเจ็ดคด, แหวนพระราม, เกราะนาคมรกต, ชฎาเทวราช, โล่สุริยะ |
| มอนสเตอร์ 3 ตัว (ID 31901–31903) | `custom/db/mob_db.yml` | ยักษ์เฝ้าประตูลงกา, บอสกุมภกรรณ, MVP ทศกัณฐ์ |
| หน้าตามอนสเตอร์ | `custom/db/mob_avail.yml` | ยืมหน้าตา Orc Warrior, Minorous, Dark Lord จึงไม่ต้องแพตช์ตัวเกม |
| สกิลมอนสเตอร์ | `custom/db/mob_skill_db.txt` | ทศกัณฐ์เรียกยักษ์ลูกน้อง, ไฟกำแพง, อุกกาบาต |
| NPC และภารกิจ | `custom/npc/ramakien.txt` | NPC "Sage of Ayodhya" ที่ Prontera (147,189): เล่าเรื่อง, ภารกิจ "A Ring for Sita" (ปราบยักษ์ 10 ตัว รับแหวนพระราม + น้ำมนต์ 5), ร้านค้า, วาร์ปไปประตูลงกา (Base Lv 60+) |
| จุดเกิด | `custom/npc/ramakien.txt` | ใน `prt_maze02`: ยักษ์ 20 ตัว, กุมภกรรณเกิดทุก 1–1.2 ชม., ทศกัณฐ์เกิดทุก 2–2.2 ชม. |

## ข้อจำกัดตอนนี้

- **ข้อความในเกมเป็นภาษาอังกฤษ** เพราะตัวเกมตั้งเป็น `langtype 0` (เกาหลี) ภาษาไทยจะแสดงเป็นตัวอักษรเพี้ยน ต้องทดสอบตั้งค่าภาษาไทยในตัวเกมก่อน
- **ไอเทมใหม่จะแสดงเป็น "Unknown Item"** (ชื่อและรูปไม่ขึ้น) จนกว่าจะส่ง patch `itemInfo` ให้ผู้เล่น แต่ใช้งาน สวมใส่ และค่าพลังทำงานครบ
- ชฎาเทวราชใช้รูปบนหัวเดียวกับ Crown ไปก่อน

## วิธีนำขึ้นเซิร์ฟเวอร์ AWS

รันใน EC2 Instance Connect ทีละบรรทัด:

```bash
cd ~/SEVER-GAME-prontera
git pull
scripts/apply-config.sh
cd rathena && ./athena-start stop && ./athena-start start --enlog
```

ตรวจว่าโหลดสำเร็จ: `grep -iE "error|warning" log/map-server.log | grep -iE "ramakien|RK_|9900|319" | tail`
ถ้าไม่มีบรรทัดไหนขึ้นมา แปลว่าผ่าน

## ทดสอบในเกม (บัญชี GM)

- `@warp prontera 147 187` แล้วคุยกับ Sage of Ayodhya
- `@item 990000 5` เสกน้ำมนต์มาลองใช้
- `@monster 31903` เรียกทศกัณฐ์มาลองตี
- `@mapmoblist prt_maze02` ดูว่ายักษ์และบอสเกิดครบ

## ถ้าต้องการยกเลิก

ลบ `custom/npc/ramakien.txt` และไฟล์ใน `custom/db/` ออก, รัน `scripts/apply-config.sh`, คืนไฟล์ต้นแบบด้วย `cd rathena && for f in item_db.yml mob_db.yml mob_avail.yml mob_skill_db.txt; do cp db/import-tmpl/$f db/import/$f; done` แล้วรีสตาร์ทเซิร์ฟเวอร์
