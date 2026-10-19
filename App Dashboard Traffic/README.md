# Bangkok Smart Mobility & Transit Analytics Dashboard (Production Deployed)

ระบบแดชบอร์ดอัจฉริยะวิเคราะห์สภาพการจราจรและโครงข่ายขนส่งสาธารณะในกรุงเทพมหานคร เชื่อมโยงและประมวลผลข้อมูลขนาดใหญ่จาก 3 แหล่งข้อมูล:
1. **CCTV Traffic Sensors**: 15,774 รายการ (176 กล้องตรวจวัดทั่วกรุงเทพฯ)
2. **Bus Stops & Passenger Transit**: 78,644 รายการ (4,201 ป้ายหยุดรถโดยสาร ทั่ว 50 เขต)
3. **Multimodal Travel Cost & Time Study**: สถิติเปรียบเทียบเวลาเดินทางและค่าใช้จ่าย 3 ระบบหลัก (รถเมล์, เรือด่วน, รถไฟฟ้า)

---

## สถานะการ Deploy (Production Status)

- **Production Cloud Live URL (Vercel)**: [https://bangkok-traffic-dashboard.vercel.app](https://bangkok-traffic-dashboard.vercel.app)
- **Official Creator & Developer**: [TON-AI Tech](https://ton-ai-tech.web.app/)
- **PWA Native Mobile App**: รองรับการติดตั้งแบบ Web App (Add to Home Screen) พร้อม `manifest.json`
- **Fallback Offline File**: [index.html](file:///e:/Agentic/App%20Dashboard%20Traffic/index.html) หรือ [dashboard.html](file:///e:/Agentic/App%20Dashboard%20Traffic/dashboard.html)

---

## เครดิตผู้พัฒนา (Credits)

แอปพลิเคชันนี้ออกแบบและพัฒนาโดย **[TON-AI Tech](https://ton-ai-tech.web.app/)**
- เว็บไซต์ทางการ: [https://ton-ai-tech.web.app/](https://ton-ai-tech.web.app/)
- โซลูชัน: Smart Mobility Analytics, AI Traffic Vision & Native Mobile Web Applications

---

## ฟังก์ชันเด่นของระบบ

- **Executive KPI Dashboard**: สรุปตัวเลขสถิติภาพรวมสำคัญ จุดคอขวดวิกฤต (Peak V/C) และป้ายรถเมล์ยอดนิยม
- **Traffic & Speed Analytics with GIS Map**: แผนที่ระบุพิกัดกล้อง CCTV 176 จุดตามสีระดับความหนาแน่น พร้อมกราฟพฤติกรรมจราจร 24 ชม.
- **Bus Network Analytics**: กราฟวิเคราะห์ Top 15 เขต และตาราง Leaderboard 25 ป้ายรถเมล์ที่มีผู้โดยสารสูงสุด
- **Transit Modes Comparison & Commuter Estimator**: เครื่องคำนวณและจำลองค่าใช้จ่าย-เวลาเดินทางตามระยะทาง
- **Advanced Data Explorer**: ระบบ Live Search, ตัวกรอง 50 เขต, ระบบแบ่งหน้า (Pagination) และฟังก์ชัน Export ข้อมูลเป็น CSV
