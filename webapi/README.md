# webapi: ข้อมูลสดสำหรับเว็บไซต์ (คนออนไลน์ + อันดับ)

บริการเล็ก ๆ ที่รันบนเครื่องเกม (EC2) อ่านฐานข้อมูล rAthena แบบ **อ่านอย่างเดียว** แล้วส่ง JSON ให้เว็บ
Read-only stats service for the website. Runs on the game server next to rAthena.

```
ผู้เล่นเปิดเว็บ (HTTPS) -> Vercel /api/status (api/status.js, cache 30 วิ) -> EC2 :8090/status (webapi/stats_api.py, cache 30 วิ) -> MariaDB (user webstats, SELECT เฉพาะบางคอลัมน์)
```

## แสดงอะไรบ้าง / What it publishes

- จำนวนตัวละครที่ออนไลน์ (`online`) และสถานะพอร์ตเกม 6900/6121/5121 (`serversUp`)
- 10 อันดับเลเวลสูงสุด: ชื่อตัวละคร อาชีพ เลเวล
- 10 อันดับนักล่า MVP: ชื่อตัวละคร จำนวน MVP
- กิลด์ที่ครองปราสาท: ชื่อปราสาท กิลด์ หัวหน้ากิลด์

ไม่ส่งข้อมูลส่วนตัว: ไม่มี account id, อีเมล, IP, รหัสผ่าน ตัวละครของ GM (group 2 ขึ้นไป) ไม่ติดอันดับ
DB user `webstats` อ่านได้แค่คอลัมน์ที่ใช้ (`char`, `login.group_id`, `guild`, `guild_castle`, `mvplog.kill_char_id`) อ่าน email/user_pass ไม่ได้ และเขียนอะไรไม่ได้เลย

## ติดตั้งบนเครื่องเกม / Install (server thread will guide)

1. `bash webapi/install.sh` (อ่านชื่อ DB จาก `.env` ของเซิร์ฟเวอร์, รันซ้ำได้)
2. เปิด inbound **TCP 8090** ใน security group (ห้ามเปิด 3306)
3. อันดับ MVP ต้องเปิด log ใน rAthena: `log_mvpdrop: yes` ใน `conf/import/log_conf.txt` แล้วรีสตาร์ท map-server (ค่าเริ่มต้นของ rAthena คือ `no` ตารางจึงว่าง)

ถอนการติดตั้ง: `bash webapi/install.sh --remove`

ใช้แรมราว 15 MB (จำกัดที่ 64 MB) เหมาะกับเครื่อง 1 GB เริ่มเองหลังรีบูต (systemd `sever-webapi`)

## ฝั่งเว็บ / Website side

- `api/status.js` (Vercel function) เรียก `http://54.206.105.93:8090/status` ถ้า IP เครื่องเปลี่ยน ให้ตั้ง Environment Variable `GAME_STATS_URL` ใน Vercel เป็น URL ใหม่ (แนะนำ Elastic IP จะได้ไม่เปลี่ยน)
- `website/assets/config.js` -> `statsApi: "/api/status"` ใส่ `""` เพื่อปิด
- ถ้าเครื่องเกมไม่ตอบ เว็บจะแสดง "—" และกล่อง "ยังไม่มีอันดับ" เหมือนเดิม ไม่แสดงตัวเลขปลอม

## ทดสอบ / Check

```
curl -s http://127.0.0.1:8090/status     # บนเครื่องเกม
systemctl status sever-webapi
journalctl -u sever-webapi -n 50
```
