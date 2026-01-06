import os  # นำเข้าโมดูล os สำหรับการทำงานกับระบบไฟล์
import random  # นำเข้าโมดูล random สำหรับสุ่มค่า
import ctypes  # นำเข้าโมดูล ctypes สำหรับเรียกใช้ Windows API
from src.config import USER_AGENTS, REFERERS  # นำเข้า User Agents และ Referers จาก config


def get_random_headers():  # ฟังก์ชันสร้าง HTTP headers แบบสุ่ม
    """Generate random headers for requests"""  # ของฟังก์ชัน
    return {  # คืนค่าพจนานุกรมที่มี headers
        "User-Agent": random.choice(USER_AGENTS),  # เลือก User Agent แบบสุ่ม
        "Accept": "*/*",  # ยอมรับทุกประเภทเนื้อหา
        "Connection": "keep-alive",  # เปิดการเชื่อมต่อแบบต่อเนื่อง
        "Cache-Control": "no-cache",  # ไม่ใช้แคช
        "Pragma": "no-cache",  # ไม่ใช้แคช (สำหรับเซิร์ฟเวอร์เก่า)
        "Referer": random.choice(REFERERS)  # เลือก Referer URL แบบสุ่ม
    }


def load_file_lines(filename, default=None):  # ฟังก์ชันโหลดข้อมูลจากไฟล์
    """Load lines from a file, return default if file doesn't exist"""  # ของฟังก์ชัน
    if not os.path.exists(filename):  # ตรวจสอบว่าไฟล์มีอยู่หรือไม่
        return default or []  # คืนค่าเริ่มต้นถ้าไฟล์ไม่มี
    try:  # ลองเปิดไฟล์
        with open(filename, 'r') as f:  # เปิดไฟล์ในโหมดอ่าน
            return [line.strip() for line in f if line.strip()]  # คืนค่าบรรทัดที่ไม่ว่าง
    except Exception as e:  # จัดการข้อผิดพลาด
        print(f"Error loading {filename}: {e}")  # แสดงข้อผิดพลาด
        return default or []  # คืนค่าเริ่มต้น


def check_root_privileges():  # ฟังก์ชันตรวจสอบสิทธิ์ root/admin
    """Check if running with root privileges"""  # ของฟังก์ชัน
    try:  # ลองตรวจสอบสิทธิ์ในระบบ Linux/Unix
        return os.geteuid() == 0  # คืนค่า True ถ้าเป็น root
    except AttributeError:  # ถ้าเป็น Windows ที่ไม่มี geteuid
        # Windows doesn't have geteuid  # 
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # ตรวจสอบสิทธิ์ admin บน Windows