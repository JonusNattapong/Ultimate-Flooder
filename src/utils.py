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


# Tor Management Functions  # ฟังก์ชันจัดการ Tor
def check_tor_running(port=9050):  # ฟังก์ชันตรวจสอบว่า Tor รันอยู่หรือไม่
    """Check if Tor is running on specified port"""  # ของฟังก์ชัน
    import socket  # นำเข้าโมดูล socket
    try:  # ลองเชื่อมต่อกับ Tor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # สร้าง socket
        sock.settimeout(1)  # ตั้ง timeout 1 วินาที
        result = sock.connect_ex(('127.0.0.1', port))  # พยายามเชื่อมต่อ
        sock.close()  # ปิด socket
        return result == 0  # คืนค่า True ถ้าเชื่อมต่อได้
    except:  # ถ้าเกิดข้อผิดพลาด
        return False  # คืนค่า False


def find_tor_executable():  # ฟังก์ชันหาไฟล์ tor.exe
    """Find Tor executable path on the system"""  # ของฟังก์ชัน
    import platform  # นำเข้าโมดูล platform
    
    system = platform.system().lower()  # ตรวจสอบระบบปฏิบัติการ
    
    if system == "windows":  # ถ้าเป็น Windows
        # Common Tor Browser locations  # ตำแหน่งทั่วไปของ Tor Browser
        possible_paths = [  # ลิสต์ตำแหน่งที่เป็นไปได้
            r"C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe",  # Program Files
            r"C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe",  # Program Files x86
            os.path.expanduser(r"~\Desktop\Tor Browser\Browser\TorBrowser\Tor\tor.exe"),  # Desktop
            os.path.expanduser(r"~\Downloads\Tor Browser\Browser\TorBrowser\Tor\tor.exe"),  # Downloads
            os.path.expanduser(r"~\AppData\Local\Tor Browser\Browser\TorBrowser\Tor\tor.exe"),  # AppData
        ]
        
        for path in possible_paths:  # วนลูปตรวจสอบแต่ละตำแหน่ง
            if os.path.exists(path):  # ถ้าพบไฟล์
                return path  # คืนค่า path
        
        # Try to find in PATH  # ลองหาใน PATH
        try:  # ลองใช้ where command
            import subprocess  # นำเข้าโมดูล subprocess
            result = subprocess.run(['where', 'tor'], capture_output=True, text=True)  # รันคำสั่ง where tor
            if result.returncode == 0:  # ถ้าพบ
                return result.stdout.strip().split('\n')[0]  # คืนค่า path แรก
        except:  # ถ้าเกิดข้อผิดพลาด
            pass
    
    elif system == "linux":  # ถ้าเป็น Linux
        # Try common locations  # ลองตำแหน่งทั่วไป
        possible_paths = [  # ลิสต์ตำแหน่งที่เป็นไปได้
            "/usr/bin/tor",  # ทั่วไป
            "/usr/local/bin/tor",  # local
            "/opt/tor-browser/Browser/TorBrowser/Tor/tor",  # Tor Browser
        ]
        
        for path in possible_paths:  # วนลูปตรวจสอบ
            if os.path.exists(path):  # ถ้าพบ
                return path  # คืนค่า path
        
        # Try which command  # ลองใช้ which
        try:  # ลองรัน which tor
            import subprocess  # นำเข้าโมดูล subprocess
            result = subprocess.run(['which', 'tor'], capture_output=True, text=True)  # รันคำสั่ง which tor
            if result.returncode == 0:  # ถ้าพบ
                return result.stdout.strip()  # คืนค่า path
        except:  # ถ้าเกิดข้อผิดพลาด
            pass
    
    elif system == "darwin":  # ถ้าเป็น macOS
        # macOS Tor Browser location  # ตำแหน่ง Tor Browser บน macOS
        possible_paths = [  # ลิสต์ตำแหน่ง
            "/Applications/Tor Browser.app/Contents/MacOS/Tor/tor",  # Applications
            os.path.expanduser("~/Applications/Tor Browser.app/Contents/MacOS/Tor/tor"),  # User Applications
        ]
        
        for path in possible_paths:  # วนลูปตรวจสอบ
            if os.path.exists(path):  # ถ้าพบ
                return path  # คืนค่า path
    
    return None  # คืนค่า None ถ้าไม่พบ


def start_tor(tor_path=None, port=9050):  # ฟังก์ชันรัน Tor
    """Start Tor process"""  # ของฟังก์ชัน
    import subprocess  # นำเข้าโมดูล subprocess
    import time  # นำเข้าโมดูล time
    
    if tor_path is None:  # ถ้าไม่ได้ระบุ path
        tor_path = find_tor_executable()  # หา path อัตโนมัติ
    
    if tor_path is None:  # ถ้ายังไม่พบ
        return False, "Tor executable not found"  # คืนค่าผลลัพธ์
    
    try:  # ลองรัน Tor
        # Create torrc content for minimal config  # สร้าง config ขั้นต่ำ
        torrc_content = f"""# Minimal Tor configuration for IP-HUNTER
SocksPort {port}
ExitPolicy reject *:*
"""  # config ที่ reject all exit และใช้ socks port ที่กำหนด
        
        # Write torrc to temp file  # เขียน config ไปยังไฟล์ temp
        import tempfile  # นำเข้าโมดูล tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.torrc', delete=False) as f:  # สร้างไฟล์ temp
            f.write(torrc_content)  # เขียน config
            torrc_path = f.name  # เก็บ path
        
        # Start Tor process  # รัน Tor process
        process = subprocess.Popen(  # ใช้ Popen รัน Tor
            [tor_path, '-f', torrc_path],  # คำสั่งรัน Tor ด้วย config file
            stdout=subprocess.PIPE,  # เก็บ stdout
            stderr=subprocess.PIPE,  # เก็บ stderr
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0  # ซ่อนหน้าต่างบน Windows
        )
        
        # Wait for Tor to start (up to 30 seconds)  # รอ Tor เริ่มทำงาน (สูงสุด 30 วินาที)
        for i in range(30):  # วนลูป 30 ครั้ง
            if check_tor_running(port):  # ตรวจสอบว่า Tor รันแล้ว
                return True, f"Tor started successfully on port {port}"  # คืนค่าผลลัพธ์
            time.sleep(1)  # รอ 1 วินาที
        
        # If still not running, kill process  # ถ้ายังไม่รัน, สังหาร process
        process.terminate()  # สังหาร process
        process.wait()  # รอให้จบ
        
        # Clean up temp file  # ลบไฟล์ temp
        try:  # ลองลบไฟล์
            os.unlink(torrc_path)  # ลบไฟล์
        except:  # ถ้าลบไม่ได้
            pass
        
        return False, "Tor failed to start within 30 seconds"  # คืนค่าผลลัพธ์
    
    except Exception as e:  # จัดการข้อผิดพลาด
        return False, f"Error starting Tor: {str(e)}"  # คืนค่าผลลัพธ์


def auto_start_tor_if_needed(port=9050):  # ฟังก์ชัน auto-start Tor ถ้าจำเป็น
    """Automatically start Tor if not running"""  # ของฟังก์ชัน
    if check_tor_running(port):  # ถ้า Tor รันอยู่แล้ว
        return True, "Tor is already running"  # คืนค่าผลลัพธ์
    
    # Try to start Tor  # พยายามรัน Tor
    success, message = start_tor(port=port)  # เรียกฟังก์ชัน start_tor
    return success, message  # คืนค่าผลลัพธ์