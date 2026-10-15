# ติดตั้งตัวเกม (Client) บน Windows — SEVER GAME Prontera

ใช้กับเซิร์ฟที่ตั้งด้วย repo นี้ (rAthena Renewal, `PACKETVER 20211103`)

> ⚠️ ตัวเกมเป็นลิขสิทธิ์ของ Gravity **ห้าม commit ไฟล์ client เข้า repo**

## วิธีง่ายที่สุด: ตัวติดตั้งคลิกเดียว (แนะนำ)

ไฟล์เดียว [`installer/Install-Prontera.bat`](../installer/Install-Prontera.bat) ทำขั้น 1–5 และ 7 ด้านล่างให้อัตโนมัติ แล้วสร้างไอคอน **Prontera** บนเดสก์ท็อปและ Start menu

1. เอาไฟล์ `Install-Prontera.bat` มาไว้ในเครื่อง แล้ว**ดับเบิลคลิก**
   ถ้าขึ้น "Windows protected your PC" ให้กด **More info → Run anyway**
2. Windows จะถามสิทธิ์ (กด **Yes**) ตอนติดตั้ง ตัวเกม kRO, Visual C++ และ Python 2.7
3. ตัวติดตั้ง kRO เป็น**ภาษาเกาหลี**: กดปุ่มขวาล่างไปเรื่อยๆ ตอนเลือกโฟลเดอร์ให้เปลี่ยนเป็น `C:\RO` และหน้าสุดท้าย**เอาติ๊กที่จะเปิดเกมออก**
4. ถ้า WARP ถาม `Do you want the CDClient DLL copied as well?` พิมพ์ `y` แล้ว Enter
5. ขึ้น `Done!` แล้วดับเบิลคลิกไอคอน **Prontera** แล้วไปขั้น 7 (สมัครไอดี)

- ไฟล์ทุกอย่างโหลดจาก**ต้นทางจริง** (Gravity, nemo.herc.ws, python.org, Microsoft, GitHub) และแพตช์ exe **บนเครื่องผู้เล่นเอง** เราไม่ได้แจกไฟล์ของ Gravity
- รันซ้ำได้ ขั้นที่เสร็จแล้วจะข้าม ถ้าเน็ตหลุดให้รันใหม่ ไฟล์จะโหลดต่อจากเดิม
- ถ้าเคยโหลด `RAG_SETUP_220120.exe` ไว้ใน `Downloads` แล้ว ตัวติดตั้งจะใช้ไฟล์นั้นต่อ
- โหลดไฟล์ `.bat` ไม่ได้ หรือไฟล์หายไปเอง (Windows Defender ลบ): เปิด **PowerShell** แล้ววางบรรทัดนี้แทน ตัวติดตั้งจะรันในหน้าต่างนั้นเลยโดยไม่ต้องมีไฟล์
  ```
  [Net.ServicePointManager]::SecurityProtocol='Tls12'; iex (iwr -UseBasicParsing https://raw.githubusercontent.com/itpppc/SEVER-GAME-prontera/main/installer/Install-Prontera.bat).Content
  ```
- log อยู่ที่ `C:\RO-tools\install-log.txt` (ส่งไฟล์นี้มาถ้าติดปัญหา)
- เปลี่ยน IP เซิร์ฟ: แก้บรรทัด `$ServerIP = '...'` บนสุดของไฟล์ด้วย Notepad
- ถ้า WARP แบบอัตโนมัติไม่สำเร็จ ตัวติดตั้งจะเปิดหน้าต่าง WARP ให้กด 4 ครั้งตามที่บอกบนจอ (session ทำไว้ให้แล้วที่ `C:\RO-tools\prontera-warp.yml`)

---

## วิธีทำเอง (ถ้าตัวติดตั้งมีปัญหา)

ทำตามลำดับ ห้ามข้ามขั้น

| ต้องใช้ | ใช้ทำอะไร | ที่มา |
|---|---|---|
| ตัวติดตั้ง kRO `RAG_SETUP_220120.exe` | ภาพ เสียง แมพ (`data.grf`) | Gravity (ทางการ) |
| exe `2021-11-03_Ragexe_1635926200` | ตัวเกมรุ่นที่ตรงกับเซิร์ฟ | nemo.herc.ws |
| ROenglishRE | เมนู/ไอเทมภาษาอังกฤษ + ไฟล์ระบบที่ exe ต้องใช้ | GitHub llchrisll |
| WARP | แพตช์ exe ให้ต่อเซิร์ฟเรา | GitHub Neo-Mind |
| Python 2.7 | ใช้รันสคริปต์โหลด exe (ครั้งเดียว) | python.org |

สร้างโฟลเดอร์ไว้ 2 อัน: `C:\RO` (ตัวเกม) และ `C:\RO-tools` (เครื่องมือ)

---

## ขั้น 1: ติดตั้งตัวเกม kRO

1. โหลด http://rofull.gnjoy.com/RAG_SETUP_220120.exe (ไฟล์ใหญ่หลาย GB)
2. เปิดไฟล์ หน้าจอเป็นภาษาเกาหลี กด `다음` (ถัดไป) → `설치` (ติดตั้ง) → `완료` (เสร็จ)
3. เลือกที่ติดตั้งเป็น `C:\RO` (อย่าลงใน Program Files)

> ❌ **ห้ามเปิด `Ragnarok.exe` / ตัวอัปเดตของ kRO และห้ามใช้ RSU** ตัวอัปเดตจะเปลี่ยน `data.grf` เป็นรูปแบบใหม่ (ปี 2025 ขึ้นไป) ที่ exe ปี 2021 อ่านไม่ได้

## ขั้น 2: โหลด exe 2021-11-03

1. ติดตั้ง **Python 2.7.15** จาก https://www.python.org/downloads/release/python-2715/ เลือก **Windows x86 MSI installer** กดถัดไปตามค่าเริ่มต้น (จะลงที่ `C:\Python27`)
2. โหลด http://nemo.herc.ws/get4.py บันทึกไว้ใน `C:\RO-tools`
3. กดปุ่ม Windows พิมพ์ `cmd` แล้วเปิด Command Prompt จากนั้นพิมพ์

```bat
cd C:\RO-tools
C:\Python27\python.exe get4.py 2021-11-03_Ragexe_1635926200 7d6d0f5400b5cfc8fe6aa366fa293f310f54e3580f0baef5dae617f7b7b575cf
```

4. เสร็จแล้วใน `C:\RO-tools` จะมีไฟล์ `.exe` ที่ชื่อขึ้นต้นด้วย `2021-11-03_Ragexe_1635926200`

> ถ้า Windows Defender เตือน ให้กด Allow **เฉพาะไฟล์นี้** อย่าปิดแอนติไวรัสทั้งเครื่อง
> ต้องใช้รุ่น `_1635926200` เท่านั้น (เป็นรุ่น RE ที่ rAthena รองรับ) รุ่นอื่นวันเดียวกันอาจต่อไม่ได้

## ขั้น 3: ไฟล์ภาษาอังกฤษ (ROenglishRE)

1. เปิด https://github.com/llchrisll/ROenglishRE กด **Code → Download ZIP** แตกไฟล์ไว้ที่ `C:\RO-tools\ROenglishRE`
2. เข้าโฟลเดอร์ `Tools` ดับเบิลคลิก `ClientGenerator.bat` แล้วตอบ
   - `Please select the mode:` → พิมพ์ `1` (Renewal)
   - `Please select the Client Date:` → พิมพ์ `9` (2021-10-28 ซึ่งใกล้ 2021-11-03 ที่สุด)
   - `Proceed?(Y/N):` → พิมพ์ `Y`
3. ผลลัพธ์อยู่ที่ `Tools\Client\`
   แล้วเปลี่ยนไฟล์ lua เป็นชุดที่ทำมาสำหรับเกมรุ่นนี้ (ชุดล่าสุดใช้กับข้อมูลเกมปี 2022 ไม่ได้): โหลด https://github.com/llchrisll/ROenglishRE/archive/db598f1d0f120f8027f9ab4652042eafb6257e73.zip (25 ม.ค. 2022) ลบโฟลเดอร์ `Tools\Client\data\luafiles514` แล้วคัดลอก `Renewal\data\luafiles514` จาก zip นั้นมาไว้แทน
4. **สำรองก่อน:** คัดลอก `C:\RO\DATA.INI` และ `C:\RO\cps.dll` ไปไว้ที่ `C:\RO-tools\backup`
5. คัดลอก**ทุกอย่าง**ใน `Tools\Client\` ไปวางใน `C:\RO` ถ้าถามให้เลือก **Replace**
6. เปิด `C:\RO\DATA.INI` ด้วย Notepad แก้ให้เป็นแบบนี้ (เลขน้อยถูกอ่านก่อน ถ้าไม่มี `rdata.grf` ใน `C:\RO` ให้ลบบรรทัดนั้นแล้วเลื่อนเลข)

```ini
[Data]
0=server.grf
1=rdata.grf
2=data.grf
```

> `server.grf` คือไฟล์เสริมของเซิร์ฟเราในอนาคต (เช่น รูปไอเทมใหม่) ยังไม่มีก็ไม่เป็นไร ห้ามเอา `data.grf` ไว้ก่อน `rdata.grf`

## ขั้น 4: ใส่ IP เซิร์ฟ (clientinfo)

เปิดไฟล์ทั้ง 2 นี้ด้วย Notepad: `C:\RO\data\clientinfo.xml` และ `C:\RO\data\sclientinfo.xml`
ในทั้งสองไฟล์ แก้เฉพาะในส่วน `<connection>` ให้เป็น (ค่าอื่นปล่อยไว้ตามเดิม)

```xml
<display>Prontera</display>
<address>IP_ของเซิร์ฟ</address>   <!-- = PUBLIC_IP ใน .env เช่น IP ของ AWS -->
<port>6900</port>
<langtype>0</langtype>
```

> ❌ **ห้ามเพิ่ม `<passwordencrypt />` หรือ `<passwordencrypt2 />`** ถ้ามีจะสมัครไอดีด้วย `_M`/`_F` ไม่ได้
> `<version>` ใส่อะไรก็ได้ rAthena ไม่ตรวจค่านี้

ถ้าไม่มีไฟล์ ให้สร้างใหม่ด้วยเนื้อหานี้ (บันทึกทั้งสองชื่อ)

```xml
<?xml version="1.0" encoding="euc-kr" ?>
<clientinfo>
  <desc>Ragnarok Client Information</desc>
  <servicetype>korea</servicetype>
  <servertype>primary</servertype>
  <connection>
    <display>Prontera</display>
    <address>IP_ของเซิร์ฟ</address>
    <port>6900</port>
    <version>55</version>
    <langtype>0</langtype>
    <registrationweb>www.ragnarok.com</registrationweb>
    <aid><admin>2000000</admin></aid>
  </connection>
</clientinfo>
```

## ขั้น 5: แพตช์ exe ด้วย WARP

1. เปิด https://github.com/Neo-Mind/WARP กด **Code → Download ZIP** แตกไว้ที่ `C:\RO-tools\WARP` แล้วเปิด `win32\WARP.exe`
2. ช่อง **Source** เลือกไฟล์ exe จากขั้น 2 แล้วกด **Load Source**
3. เปิดแถบเมนูด้านซ้าย → **Session → Load Session file** → เลือก
   `C:\RO-tools\ROenglishRE\Addons\WARP Sessions\2019-06_Translation.yml`
4. กด **Select Recommended**
5. **ติ๊กเพิ่ม** (ถ้ามีในรายการ)
   - `Read data folder first` (**สำคัญที่สุด** ไม่ติ๊กจะไม่อ่านไฟล์ภาษาอังกฤษและ clientinfo)
   - `Disable Game Guard` และ `Disable Cheat Defender Game Guard` ถ้าถามว่าจะ copy CDClient DLL ไหม ให้ตอบ **Yes**
   - `Customize Window title` ใส่ `Prontera`
   - `Always hide License Screen`
   - `Remove admin privilege requirement`
6. **ห้ามติ๊กเพิ่ม** (ปล่อยตามที่ Select Recommended เลือก)
   - หมวด **DISABLE ENCRYPTION** และ **ENCRYPTION KEY CUSTOMIZATION**
   - `Use SSO Login Packet` (session เลือก `Use Old Login Packet` ไว้แล้ว ซึ่งถูกต้อง)
7. กด **Apply Patches** จะได้ไฟล์ `..._patched.exe` อยู่ข้างไฟล์ต้นฉบับ
8. คัดลอก `..._patched.exe` และ `CDClient.dll` (ถ้า WARP สร้างให้) ไปไว้ใน `C:\RO`

## ขั้น 6 (ไม่บังคับ): ตั้งค่าภาพและหน้าจอ

โหลด **OpenSetup** จาก https://nn.ai4rei.net/dev/opensetup/ วางใน `C:\RO` เปิดแล้วเลือกความละเอียด/โหมดหน้าต่าง

## ขั้น 7: เข้าเกมครั้งแรก + ตั้ง GM

1. ดับเบิลคลิก `..._patched.exe` ใน `C:\RO` (ถ้า SmartScreen เตือน: **More info → Run anyway**)
2. **สมัครไอดี** ช่อง ID พิมพ์ชื่อตามด้วย `_M` (ชาย) หรือ `_F` (หญิง) เช่น `tonadmin_M`
   - ชื่อ (ไม่นับ `_M`) ต้อง **6 ตัวขึ้นไป** รหัสผ่านต้อง **6 ตัวขึ้นไป** (`admin` 5 ตัวจะสมัครไม่ได้)
   - สมัครได้ 1 ไอดีต่อ 10 วินาที
   - ถ้าสมัครในเกมไม่ผ่าน สร้างบนเซิร์ฟแทนได้: `scripts/make-account.sh tonadmin` (ถามรหัสผ่านโดยไม่แสดงตัวอักษร)
3. ล็อกอินอีกครั้งด้วยชื่อ**ไม่มี** `_M` เช่น `tonadmin`
4. เลือกเซิร์ฟ **Prontera** → ตั้ง **PIN** 4 หลัก → สร้างตัวละคร → จะเกิดที่ Prontera
5. ตั้งเป็น GM: บนเซิร์ฟรัน `scripts/make-gm.sh tonadmin 99` แล้วออกเกมเข้าใหม่ ทดสอบ `@go 0`, `@item 501 10`

## หลังเข้าเกมได้แล้ว (แนะนำ): web service พอร์ต 8888

client ปี 2020 ขึ้นไปใช้ web-server ของ rAthena เก็บคีย์ลัด/ตั้งค่า UI และตรากิลด์

1. เปิดพอร์ต **8888** (TCP) ใน firewall / AWS Security Group
2. แก้ 2 ไฟล์ใน `C:\RO\data\luafiles514\lua files\service_korea\`: `ExternalSettings_kr.lub` และ `ExternalSettings_kr_sak.lub`
   หาบรรทัด `AssistAddr = "127.0.0.1:8888"` แล้วเปลี่ยนเป็น `AssistAddr = "IP_ของเซิร์ฟ:8888"`

## แจกตัวเกมให้ผู้เล่น

แจกแค่ไฟล์ `installer/Install-Prontera.bat` (ไฟล์เล็ก ไม่มีไฟล์ของ Gravity อยู่ข้างใน) ผู้เล่นดับเบิลคลิกแล้วได้ตัวเกมจากต้นทางเองเหมือนเรา
ไม่แนะนำให้แจกโฟลเดอร์ `C:\RO` ทั้งก้อน เพราะเท่ากับเราเอาไฟล์ลิขสิทธิ์ของ Gravity ไปแจกเอง
ถ้า IP เซิร์ฟเปลี่ยน ผู้เล่นทุกคนต้องรันตัวติดตั้งตัวใหม่ จึงควรใช้ IP ถาวร (AWS: Elastic IP)

---

## แก้ปัญหา

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| เปิดเกมแล้วปิดเอง / crash ทันที | ติดตั้ง DirectX 9.0c (End-User Runtime) และเช็คว่าใน `C:\RO` มี `aossdk.dll`, `binkw32.dll`, `CDClient.dll`, `cps.dll`, `granny2.dll`, `ijl15.dll`, `libcurl.dll`, `Mss32.dll`, `Mp3dec.asi` |
| error `MSVCP140.dll` / `VCRUNTIME140.dll` | ติดตั้ง Microsoft Visual C++ 2015–2022 Redistributable **x86** |
| ภาษาเกาหลีเต็มจอ / Lua error / ไม่เห็นเซิร์ฟเรา | ไม่ได้ติ๊ก `Read data folder first` หรือ copy ไฟล์ขั้น 3 ไม่ครบ |
| ต่อเซิร์ฟไม่ได้ตั้งแต่หน้าล็อกอิน | IP ใน clientinfo ผิด หรือเซิร์ฟปิดอยู่ เช็คด้วย PowerShell `Test-NetConnection IP_ของเซิร์ฟ -Port 6900` |
| ล็อกอินแล้วขึ้น "Unregistered ID" | ยังไม่มีไอดีนี้ในเซิร์ฟ (ยังไม่เคยสมัคร `_M` สำเร็จ หรือ `NEW_ACCOUNT=no`) สร้างบนเซิร์ฟแทนได้เลย: `cd ~/SEVER-GAME-prontera && git pull && scripts/make-account.sh tonadmin` พิมพ์รหัสผ่านเอง (ไม่แสดงตัวอักษร) แล้วล็อกอินด้วย `tonadmin` ไม่มี `_M` |
| สมัคร `_M` แล้ว "Rejected from server" | ชื่อหรือรหัสสั้นกว่า 6 ตัว, มี `passwordencrypt` ใน clientinfo, `NEW_ACCOUNT=no`, หรือสมัครถี่เกิน |
| เลือกเซิร์ฟแล้วค้าง / หลุด | `PUBLIC_IP` ใน `.env` ผิด หรือยังไม่เปิดพอร์ต 6121 / 5121 |
| ล็อกอินแล้วหลุดทันที | ใช้ exe ผิดรุ่น (ต้องเป็น `2021-11-03_Ragexe_1635926200`) หรือติ๊กแพตช์ในหมวด encryption |
| กดไอคอนแล้วขึ้นหน้าต่างเกาหลีที่มีปุ่ม START หรือ `Repacking resource files` | นั่นคือตัวอัปเดต kRO ห้ามกด START ปิดด้วย Ctrl+Shift+Esc > คลิกขวา Ragnarok > End task แล้วรัน `Install-Prontera.bat` ใหม่ (รุ่นใหม่ซ่อมไอคอน ลบไอคอนเกาหลี และตรวจไฟล์เกมให้) |
| ตัวติดตั้งขึ้น `data.grf cannot be used` (เช่น `it has grown to 4.0 GB`) หรือเกมเด้งออกทันทีที่เปิด | ตัวอัปเดต kRO แก้ไฟล์เกมไปแล้ว (data.grf ใหญ่เกิน 4 GB ซึ่งตัวเกมปี 2021 อ่านไม่ได้) พิมพ์ `Y` แล้ว Enter ตัวติดตั้งจะลงเกมชุดใหม่ไว้ที่ `C:\RO` (หรือ `C:\RO2`) โดยไม่ลบโฟลเดอร์เดิม และใช้ไฟล์ที่โหลดไว้แล้ว ไม่ต้องโหลดใหม่ ถ้าตัวติดตั้งเกาหลีเปิดเป็นหน้าจอให้กด ให้เปลี่ยนโฟลเดอร์ตามที่ตัวติดตั้งบอก |
| `Cannot init d3d OR grf file has problem` | ลงเกมใหม่แล้วยังไม่เคยตั้งค่ากราฟิก ดับเบิลคลิก `Setup.exe` ในโฟลเดอร์เกม กด Yes เลือกการ์ดจอ (ไม่ใช่โปรเจกเตอร์) 1024x768 แบบหน้าต่าง แล้วกด OK (ตัวติดตั้งรุ่นใหม่เปิดหน้านี้ให้เองถ้ายังไม่ได้ตั้ง) |
| Lua error ตอนเปิดเกม เช่น `PetInfo` `table index is nil`, `StateIconInfo`, `queryNavi_MapInfo`, `AddRandomOptionNameTable` | ไฟล์ lua ภาษาอังกฤษรุ่นปี 2025 อ้างถึงสัตว์เลี้ยง/ไอคอน/แผนที่ที่เกมปี 2022 ไม่มี รัน `Install-Prontera.bat` ซ้ำหนึ่งรอบ ตัวติดตั้งรุ่นใหม่ใช้ไฟล์ lua ชุดปี 2022 ทั้งชุด และเปลี่ยนชื่อไฟล์เก่าที่ไม่ใช้แล้วเป็น `.off` (ไม่ลบ) |
| `cannot open System\...._sak.lub` หรือ `_Sakray.lub` (เช่น `CPetEvolutionMgr`, `CPrivateAirplaneMgr`) | exe รุ่น Renewal หาไฟล์ชื่อแบบ Sakray แต่ kRO ให้มาแค่ชื่อแบบ `_true` ตัวติดตั้งรุ่นใหม่สร้างให้ครบ รัน `Install-Prontera.bat` ซ้ำหนึ่งรอบ |
| หน้าต่าง `You'll need a new app to open this ms-gamingoverlay link` | เป็นของ Windows (Xbox Game Bar) ไม่เกี่ยวกับเกม กด Esc ได้เลย |
| Windows Defender ลบไฟล์ exe ระหว่างติดตั้ง | กด Allow **เฉพาะไฟล์นั้น** แล้วรันตัวติดตั้งซ้ำ |
| ปุ่ม/รูปบางอันยังเป็นภาษาเกาหลี | ไม่กระทบการเล่น เมนูและไอเทมเป็นอังกฤษแล้ว รูปบางรูปอยู่ในโฟลเดอร์ชื่อเกาหลี ซึ่ง Windows ที่ตั้งภาษาโปรแกรม non-Unicode เป็นไทยอาจหาไม่เจอ |

## แหล่งอ้างอิง

- rAthena รองรับ 2021-11-03 RagexeRE: https://github.com/rathena/rathena/pull/6431
- exe 2021-11-03: http://nemo.herc.ws/downloads/2021-11-03_Ragexe_1635926200/
- ROenglishRE: https://github.com/llchrisll/ROenglishRE · คู่มือ ROTP: https://llchrisll.github.io/ROTPDocs/guides/install/ · FAQ: https://llchrisll.github.io/ROTPDocs/FAQ/ · web service: https://llchrisll.github.io/ROTPDocs/guides/webservice/
- WARP: https://github.com/Neo-Mind/WARP
- ตัวอย่างตั้งค่า client กับ rAthena 20211103: https://github.com/cdelorme/rathena-docker
- OpenSetup: https://nn.ai4rei.net/dev/opensetup/
