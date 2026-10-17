# game-core: ระบบต่อสู้หลัก (รามเกียรติ์)

โค้ดกติกาการต่อสู้ที่ไม่ผูกกับเอนจินหรือหน้าเว็บ เป็น JavaScript ES module + JSDoc (`// @ts-check`) รันได้ทั้งในเบราว์เซอร์และ Node โดยไม่ต้อง build และไม่มี dependency

```bash
cd game-core
npm test          # node --test (29 tests)
npm run typecheck # tsc strict ผ่าน JSDoc (ต้องมี typescript)
```

## โครงสร้าง

| ไฟล์ | หน้าที่ |
|---|---|
| `src/core/` | `Faction` (ayodhya/lanka), `EventBus`, `makeRng` (mulberry32 แบบเดียวกับ website/rpg) |
| `src/combat/combatant.js` | หน่วยรบพื้นฐาน: HP/MP, สถานะ, ท่อรับดาเมจ (guard → mitigate → defeat interceptors → ko) |
| `src/combat/battle.js` | สนามรบ: ลำดับเทิร์นตาม `spd`, `beginTurn`/`endTurn`, ลม (`wind` 0-100), AOE `inRadius`, log เหตุการณ์ |
| `src/combat/skill.js` | `Skill` (Template Method: เช็ค → จ่าย MP/คูลดาวน์ → `execute`) และ `Strike` |
| `src/classes/` | `WanonWarrior` (คืนชีพด้วยลม), `NagaSorcerer` (บ่วงนาคบาศ) |
| `src/boss/thotsakan.js` | `ThotsakanBoss` + `HeartBox` (ระบบกล่องดวงใจ 2 เฟส) |
| `src/objectives/sea-causeway.js` | `SeaCauseway` จองถนนข้ามทะเล 0-100% |

## กติกาหลัก

**คืนชีพด้วยลม (Wind Revival)** passive ของนักรบวานร: เมื่อ HP เป็น 0 และ `battle.wind >= 40` จะฟื้นด้วย HP 30% และล้างสถานะควบคุม ใช้ได้ 1 ครั้งต่อการต่อสู้ ไม่ทำงานถ้าลมสงบ หรือโดนท่าที่มีแท็ก `sealsRevival` สกิล `เรียกลมพระพาย` เพิ่มลม +30

**บ่วงนาคบาศ (Naga Binding)** AOE แบบเล็งพื้น ระยะร่าย 6 รัศมี 2: ดาเมจเวท 60% ของ `matk` แล้วรัดศัตรูที่รอด 2 เทิร์น (เดินไม่ได้ ข้ามเทิร์น) พอหลุดจะได้ `bindResist` 1 เทิร์นกันโดนรัดซ้ำไม่จบ หน่วย `ccImmune` (บอส) โดนดาเมจแต่ไม่โดนรัด ไม่โดนพวกเดียวกัน

**ทศกัณฐ์ ระบบกล่องดวงใจ**
1. เฟส `heartSealed`: บล็อกดาเมจทุกชนิด (รวม true damage) และส่ง event `blocked`
2. `HeartBox` เป็นวัตถุบนสนาม ไม่มีเทิร์น ไม่นับตอนตัดสินแพ้ชนะ รับดาเมจจากฝ่ายตรงข้ามเท่านั้น (`friendlyFire`, `noSource` ถูกบล็อก)
3. กล่องแตก → `exposeHeart()` (idempotent) → เฟส `heartExposed` รับดาเมจได้ และคลั่ง atk/matk ×1.25 บันทึก `heartBrokenBy` ไว้ให้รางวัล

**จองถนนข้ามทะเล** นับเป็น "ก้อนหิน" จำนวนเต็ม 1000 ก้อน = 100% (กันทศนิยมคลาด)
- อโยธยา `build()` เพิ่ม, ลงกา (กองทัพปลา) `interrupt()` ลด, จำกัด 50 ก้อนต่อครั้ง กันโกง
- ถึง 25/50/75% แล้วล็อกเป็น checkpoint ถูกรื้อต่ำกว่านั้นไม่ได้, ครบ 100% = `completed` ล็อกถาวร
- `resolveRound()` คิดผลสุทธิของทั้งรอบพร้อมกัน ลำดับการกดไม่มีผล และแบ่งเครดิตให้ผู้เล่นรวมได้พอดีเป๊ะ (largest remainder)

## ต่อกับเกมผลัดกันตี (website/rpg)

ชื่อและจังหวะตรงกับ `website/rpg/engine.js`: `atk/def/spd`, `cds` (+1 เพราะ `beginTurn` ลดก่อน), สถานะลดตอนจบเทิร์นของตัวเอง, สถานะที่ใส่ตัวเองไม่ลดในเทิร์นนั้น (`fresh`), event รูปแบบ `{ t, who, ... }` เช่น `dmg`, `ko`, `status`, `expire`, `skip` เพิ่ม `blocked`, `revive`, `resist`, `phase`, `wind`, `causeway`

```js
import { Battle, WanonWarrior, NagaSorcerer, Faction } from './game-core/src/index.js';
const battle = new Battle({ seed: 1, wind: 50 });
battle.bus.on((ev) => render(ev));          // หรือใช้ผลลัพธ์ skill.use(...).events
for (const u of battle.turnOrder()) {
  if (battle.beginTurn(u).skip) continue;
  u.skills.strike?.use(u, battle, target);
  battle.endTurn(u);
}
battle.nextRound();
```

## ไอเดียเทสต์ที่ครอบคลุมแล้ว (test/)

- ลม 39 ไม่ฟื้น / 40 ฟื้น / ฟื้นครั้งเดียว / `sealsRevival` / ล้างบ่วงตอนฟื้น / ประจุไม่หายเมื่อฟื้นไม่สำเร็จ
- บ่วงนาค: โดนเฉพาะศัตรูในวง, ไม่โดนพวกเดียวกัน, ข้าม 2 เทิร์นแล้วได้ `bindResist`, ร่ายซ้ำโดนต้าน, บอสต้าน, ตายจากดาเมจไม่ติดบ่วง, ไม่หัก MP ตอนร่ายพลาด
- ทศกัณฐ์: เฟส 1 กันทุกชนิดดาเมจ, กล่องไม่รับดาเมจพวกเดียวกัน, กล่องแตก → เฟส 2 + event ครั้งเดียว, กล่องไม่มีเทิร์นและไม่นับแพ้ชนะ
- ถนน: ฝ่ายผิด/จำนวนผิด/เกินเพดาน, ไม่ต่ำกว่า 0 และ checkpoint, ครบ 100% แล้วล็อก, ผลสุทธิของรอบ, เครดิตรวมพอดี
