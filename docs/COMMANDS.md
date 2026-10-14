# คำสั่งในเกม (@ / #) — SEVER GAME Prontera

ตรวจกับซอร์ส rAthena ล่าสุด (`conf/atcommands.yml`, `conf/groups.yml`, `src/map/atcommand.cpp`) แล้ว

- `@คำสั่ง` = ใช้กับตัวเอง
- `#คำสั่ง "ชื่อตัวละคร" ...` = ใช้กับผู้เล่นคนอื่น (char command) เช่น `#kill "Poring Lover"`
- ดูคำสั่งที่ตัวเองใช้ได้: `@commands` · ดูวิธีใช้: `@help <คำสั่ง>`
- ไฟล์ที่กำหนดสิทธิ์: **`conf/groups.yml`** และชื่อ/alias คำสั่งอยู่ที่ **`conf/atcommands.yml`** (rAthena เปลี่ยนจาก `.conf` เป็น `.yml` แล้ว) ปรับแต่งของเซิร์ฟเวอร์นี้ให้แก้ที่ [`config/import/groups.yml`](../config/import/groups.yml) แล้วรัน `scripts/apply-config.sh` ตามด้วย `@reloadatcommand` ในเกม (โหลดทั้งคำสั่งและกลุ่มสิทธิ์ใหม่ ไม่ต้องรีสตาร์ท)

## กลุ่มสิทธิ์ (group_id ในตาราง `login`)

| group_id | ชื่อ | ได้อะไร |
|---|---|---|
| 0 | Player | ค่าเริ่มต้นของ rAthena ใช้ได้แค่ `@changedress`, `@resurrect` — **เซิร์ฟนี้เพิ่มคำสั่งผู้เล่นด้านล่างให้แล้ว** |
| 1 | Super Player | คำสั่งผู้เล่นทั้งหมด + `@go` |
| 2 | Support | + `@who`, `@where`, `@jumpto`, `@broadcast` |
| 3 | Script Manager | + `@loadnpc`, `@unloadnpc`, `@hidenpc`, `@shownpc` |
| 4 | Event Manager | + `@monster`, `@item`, `@zeny`, `@killmonster2`, `@pvpon` ฯลฯ |
| 5 | VIP | Player + `@rates`, `@who` |
| 10 | Law Enforcement | + `@kick`, `@ban`, `@block`, `@jail`, `@mute`, `@recall`, `@warp`, `@hide` |
| 99 | Admin | ทุกคำสั่ง (`all_commands`) |

ตั้ง GM: `scripts/make-gm.sh <userid> 99` หรือ SQL `UPDATE login SET group_id = 99 WHERE userid = 'admin';` แล้วล็อกอินใหม่

## 1. คำสั่งผู้เล่น (group 0 ของเซิร์ฟนี้)

| คำสั่ง | Alias | ใช้ทำอะไร |
|---|---|---|
| `@autoloot <on\|off\|%>` | | เก็บของดรอปเข้าตัวอัตโนมัติ เช่น `@autoloot 100` |
| `@autolootitem +<ID>` / `-<ID>` / `reset` | `@alootid` | เก็บเฉพาะไอเทม ID ที่เลือก (ต้องใช้ **ID** พร้อม `+`/`-`) |
| `@autotrade` | `@at` | เปิดร้าน (Vending) ค้างไว้ แล้วออฟไลน์ |
| `@refresh` | | ซิงก์ตำแหน่ง/สถานะใหม่ แก้ตัวค้าง |
| `@mobinfo <ชื่อ\|ID>` | `@mi`, `@monsterinfo` | ข้อมูลมอนสเตอร์ สเตตัส EXP ดรอป |
| `@iteminfo <ชื่อ\|ID>` | `@ii` | ข้อมูลไอเทม ประเภท ราคา |
| `@whodrops <ชื่อ\|ID>` | | มอนสเตอร์ตัวไหนดรอปไอเทมนี้ |
| `@whereis <ชื่อ\|ID>` | | มอนสเตอร์เกิดแมพไหน |
| `@servertime` | `@time`, `@date` | เวลาเซิร์ฟเวอร์ |
| `@rates` | | เรต EXP / Drop ปัจจุบัน |
| `@showexp` / `@showzeny` | | เปิด/ปิดแสดง EXP / Zeny ที่ได้ |
| `@noks` | | กันคนแย่งมอน (Kill Steal) |
| `@commands`, `@help <cmd>` | `@h` | ดูรายการ/วิธีใช้คำสั่ง |

## 2. วาร์ปและจัดการตัวละคร (GM)

| คำสั่ง | Alias | ใช้ทำอะไร | group ขั้นต่ำ |
|---|---|---|---|
| `@go <เลข\|ชื่อเมือง>` | | วาร์ปเข้าเมือง: `0` prontera, `1` morocc, `2` geffen, `3` payon, `4` alberta, `5` izlude, `6` aldebaran ... | 1 |
| `@mapmove <map> [x y]` | `@warp`, `@rura` | วาร์ปไปแมพ/พิกัด เช่น `@warp prontera 156 191` | 10 |
| `@jump [x [y]]` | | สุ่มวาร์ปในแมพ (เหมือนปีกแมลงวัน) | 99 |
| `@jumpto <ชื่อ>` | `@goto`, `@warpto` | วาร์ปตัวเราไปหาผู้เล่น | 2 |
| `@recall <ชื่อ>` | | ดึงผู้เล่นมาหาเรา | 10 |
| `#warp "ชื่อ" <map> <x> <y>` | | ส่งผู้เล่นไปแมพที่กำหนด (char command) | 99 |
| `@where <ชื่อ>` / `@who` | | ดูตำแหน่ง / รายชื่อผู้เล่นออนไลน์ | 2 |
| `@kill` | `@die` | ฆ่า**ตัวเอง** | 10 |
| `#kill "ชื่อ"` | | ฆ่าผู้เล่นอื่น | 99 |
| `@raise <ชื่อ>` | `@revive` | ชุบผู้เล่น | 4 |
| `@heal [HP SP]` | | ฟื้น HP/SP | 99 |
| `@hide` | | ล่องหนแบบ GM | 10 |
| `@speed <1-1000>` | | ความเร็วเดิน (150 = ปกติ) | 10 |
| `@jobchange <ID>` | `@job` | เปลี่ยนอาชีพ | 99 |
| `@baselevelup <n>` / `@joblevelup <n>` | `@blvl` / `@jlvl` | เพิ่มเลเวล | 99 |

## 3. เสกไอเทมและเงิน

| คำสั่ง | ใช้ทำอะไร | group |
|---|---|---|
| `@item <ชื่อ\|ID> <จำนวน>` | เสกไอเทม เช่น `@item 501 10` | 4 |
| `@item2 <ID> <จำนวน> <identify> <refine> <broken> <card1> <card2> <card3> <card4>` | เสกแบบละเอียด เช่น `@item2 1201 1 1 10 0 4001 0 0 0` (มีด +10 ใส่การ์ด) | 99 |
| `@zeny <จำนวน>` | เพิ่ม/ลด Zeny (ติดลบ = ลด) | 4 |

## 4. มอนสเตอร์

| คำสั่ง | Alias | ใช้ทำอะไร | group |
|---|---|---|---|
| `@monster <ชื่อ\|ID> [จำนวน]` | `@spawn` | เสกมอนสเตอร์ตรงที่ยืน (`@spawn` คือ alias เดียวกัน ไม่มีระบบเวลาเกิดใหม่) | 4 |
| `@killmonster [map]` | | ฆ่ามอนในแมพ **มีของดรอป** | 99 |
| `@killmonster2` | | ฆ่ามอนในแมพ ไม่ดรอป | 4 |

## 5. ผู้ดูแลเซิร์ฟเวอร์

| คำสั่ง | ใช้ทำอะไร | group |
|---|---|---|
| `@kick <ชื่อ>` | เตะออกจากเกม | 10 |
| `@ban <เวลา> <ชื่อ>` | แบนชั่วคราว รูปแบบเวลา `+1d`, `+12h`, `+30mn`, `+1m` (เดือน), `+1y` เช่น `@ban +1d Poring` | 10 |
| `@unban <ชื่อ>` | ปลดแบน | 99 |
| `@block <ชื่อ>` / `@unblock <ชื่อ>` | แบนถาวร / ปลด | 10 / 99 |
| `@jail <ชื่อ>` / `@unjail <ชื่อ>` | ส่งเข้าคุก / ปล่อย | 10 / 99 |
| `@mute <ชื่อ>` | ห้ามพูด | 10 |
| `@broadcast <ข้อความ>` / `@kami <ข้อความ>` | ประกาศทั้งเซิร์ฟ (มีชื่อ / ไม่มีชื่อ) | 2 / 99 |
| `@mapflag [ชื่อ]` | ดู/เปิด mapflag ของแมพปัจจุบัน (`@mapflag available` ดูรายการ) — ใช้แทน `@mappable` ที่**ไม่มีอยู่จริง** | 99 |
| `@reloadatcommand` | โหลด `atcommands.yml` และ `groups.yml` ใหม่ | 99 |
| `@reloadscript` | โหลด NPC script ทั้งหมดใหม่ | 99 |
| `@reloaditemdb` / `@reloadmobdb` / `@reloadbattleconf` | โหลด DB/คอนฟิกใหม่ | 99 |

## สิ่งที่แก้จากรายการเดิม

| เดิม | ความจริงใน rAthena |
|---|---|
| `@stransport`, `@warpperson` | ไม่มีคำสั่งนี้ ใช้ `@recall` (ดึงมา) และ `#warp "ชื่อ" map x y` (ส่งไป) |
| `@mappable` / `@mapunmappable` | ไม่มี ใช้ `@mapflag` |
| `@kill <ชื่อ>` | `@kill` ฆ่าตัวเอง ใช้ `#kill "ชื่อ"` กับคนอื่น |
| `@spawn` ระบุเวลาเกิดใหม่ | เป็น alias ของ `@monster` |
| `@alootid <ชื่อ>` | ต้องใช้ `+<ItemID>` |
| คำสั่งผู้เล่นใช้ได้ทันที | rAthena ค่าเริ่มต้นให้ group 0 แค่ 2 คำสั่ง เซิร์ฟนี้เพิ่มให้ผ่าน `config/import/groups.yml` |
| `conf/atcommand.conf`, `conf/groups.conf` | ปัจจุบันคือ `conf/atcommands.yml`, `conf/groups.yml` |
