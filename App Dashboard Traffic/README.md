# Bangkok Smart Mobility & Transit Analytics Dashboard (Production Deployed)

ระบบแดชบอร์ดอัจฉริยะวิเคราะห์สภาพการจราจรและโครงข่ายขนส่งสาธารณะในกรุงเทพมหานคร เชื่อมโยงและประมวลผลข้อมูลขนาดใหญ่จาก 3 แหล่งข้อมูล:
1. **CCTV Traffic Sensors**: 15,774 รายการ (176 กล้องตรวจวัดทั่วกรุงเทพฯ)
2. **Bus Stops & Passenger Transit**: 78,644 รายการ (4,201 ป้ายหยุดรถโดยสาร ทั่ว 50 เขต)
3. **Multimodal Travel Cost & Time Study**: สถิติเปรียบเทียบเวลาเดินทางและค่าใช้จ่าย 3 ระบบหลัก (รถเมล์, เรือด่วน, รถไฟฟ้า)

---

## สถานะการ Deploy (Production Status)

- **Production Server**: ทำงานอยู่ในโหมด Background Daemon (Multi-threaded HTTP Server)
- **Production Live URL**: [http://localhost:5555/](http://localhost:5555/)
- **Fallback Standalone File**: [index.html](file:///e:/Agentic/index.html) (เปิดดูแบบ Offline ได้ 100%)

---

## วิธีการเปิดใช้งาน (Quick Access)

1. **เปิดผ่านเบราว์เซอร์ทันที**: คลิกเข้าที่ [http://localhost:5555/](http://localhost:5555/)
2. **เปิดผ่าน Batch File ในโฟลเดอร์**: ดับเบิลคลิกที่ [START_DASHBOARD.bat](file:///e:/Agentic/START_DASHBOARD.bat)
3. **เปิดไฟล์ HTML โดยตรง**: ดับเบิลคลิกที่ [index.html](file:///e:/Agentic/index.html) หรือ [dashboard.html](file:///e:/Agentic/dashboard.html)

---

## ฟังก์ชันเด่นของระบบ

- **Executive KPI Dashboard**: สรุปตัวเลขสถิติภาพรวมสำคัญ จุดคอขวดวิกฤต (Peak V/C) และป้ายรถเมล์ยอดนิยม
- **Traffic & Speed Analytics with GIS Map**: แผนที่ระบุพิกัดกล้อง CCTV 176 จุดตามสีระดับความหนาแน่น พร้อมกราฟพฤติกรรมจราจร 24 ชม.
- **Bus Network Analytics**: กราฟวิเคราะห์ Top 15 เขต และตาราง Leaderboard 25 ป้ายรถเมล์ที่มีผู้โดยสารสูงสุด
- **Transit Modes Comparison & Commuter Estimator**: เครื่องคำนวณและจำลองค่าใช้จ่าย-เวลาเดินทางตามระยะทาง
- **Advanced Data Explorer**: ระบบ Live Search, ตัวกรอง 50 เขต, ระบบแบ่งหน้า (Pagination) และฟังก์ชัน Export ข้อมูลเป็น CSV
