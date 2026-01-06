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


def start_tor(tor_path=None, port=9050, bridges=None):  # ฟังก์ชันรัน Tor
    """Start Tor process"""  # ของฟังก์ชัน
    import subprocess  # นำเข้าโมดูล subprocess
    import time  # นำเข้าโมดูล time
    
    if tor_path is None:  # ถ้าไม่ได้ระบุ path
        tor_path = find_tor_executable()  # หา path อัตโนมัติ
    
    if tor_path is None:  # ถ้ายังไม่พบ
        return False, "Tor executable not found"  # คืนค่าผลลัพธ์
    
    try:  # ลองรัน Tor
        # Create torrc content  # สร้าง config
        if bridges:  # ถ้ามี bridges
            torrc_content = create_torrc_with_bridges(bridges)  # สร้าง config กับ bridges
        else:  # ถ้าไม่มี bridges
            torrc_content = f"""# Minimal Tor configuration for IP-HUNTER
SocksPort {port}
ExitPolicy reject *:*
"""  # config ขั้นต่ำ
        
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
        
        # Wait for Tor to start (up to 60 seconds with bridges)  # รอ Tor เริ่มทำงาน (สูงสุด 60 วินาทีถ้ามี bridges)
        wait_time = 60 if bridges else 30  # ตั้งเวลารอ
        for i in range(wait_time):  # วนลูปตามเวลารอ
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
        
        return False, f"Tor failed to start within {wait_time} seconds"  # คืนค่าผลลัพธ์
    
    except Exception as e:  # จัดการข้อผิดพลาด
        return False, f"Error starting Tor: {str(e)}"  # คืนค่าผลลัพธ์


def auto_start_tor_if_needed(port=9050):  # ฟังก์ชัน auto-start Tor ถ้าจำเป็น
    """Automatically start Tor if not running"""  # ของฟังก์ชัน
    if check_tor_running(port):  # ถ้า Tor รันอยู่แล้ว
        return True, "Tor is already running"  # คืนค่าผลลัพธ์
    
    # Try to start Tor  # พยายามรัน Tor
    success, message = start_tor(port=port)  # เรียกฟังก์ชัน start_tor
    return success, message  # คืนค่าผลลัพธ์


# Stealth and Anti-Trace Functions  # ฟังก์ชันสำหรับ stealth และป้องกันการ trace
def randomize_timing(base_delay=0.1, max_delay=2.0):  # ฟังก์ชัน randomize timing
    """Add random delays to prevent timing analysis"""  # ของฟังก์ชัน
    import time  # นำเข้าโมดูล time
    import random  # นำเข้าโมดูล random
    
    delay = random.uniform(base_delay, max_delay)  # สุ่ม delay
    time.sleep(delay)  # รอตาม delay ที่สุ่ม


def generate_stealth_headers():  # ฟังก์ชันสร้าง headers แบบ stealth
    """Generate advanced stealth headers to avoid fingerprinting"""  # ของฟังก์ชัน
    import random  # นำเข้าโมดูล random
    
    # Base headers  # headers พื้นฐาน
    headers = {  # พจนานุกรม headers
        "User-Agent": random.choice(USER_AGENTS),  # User Agent แบบสุ่ม
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # Accept แบบสมจริง
        "Accept-Language": "en-US,en;q=0.9",  # ภาษาที่ยอมรับ
        "Accept-Encoding": "gzip, deflate, br",  # การเข้ารหัสที่ยอมรับ
        "DNT": "1",  # Do Not Track
        "Connection": "keep-alive",  # การเชื่อมต่อ
        "Upgrade-Insecure-Requests": "1",  # อัปเกรดเป็น HTTPS
        "Sec-Fetch-Dest": "document",  # Security headers
        "Sec-Fetch-Mode": "navigate",  # Security headers
        "Sec-Fetch-Site": "none",  # Security headers
        "Sec-Fetch-User": "?1",  # Security headers
        "Cache-Control": "max-age=0",  # ไม่ใช้ cache
        "Referer": random.choice(REFERERS) if random.random() > 0.3 else "",  # Referer แบบสุ่ม (บางครั้งไม่มี)
    }
    
    # Add random additional headers to vary fingerprint  # เพิ่ม headers เพิ่มเติมแบบสุ่ม
    optional_headers = {  # headers ที่อาจเพิ่ม
        "X-Requested-With": "XMLHttpRequest",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "X-Real-IP": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "CF-RAY": f"{random.randint(1000000000000000,9999999999999999)}-{random.choice(['CDG', 'FRA', 'LHR', 'AMS'])}",
        "X-Forwarded-Proto": "https",
        "X-Forwarded-Host": random.choice(["example.com", "google.com", "cloudflare.com"]),
    }
    
    # Add 1-3 random optional headers  # เพิ่ม headers เพิ่มเติม 1-3 ตัวแบบสุ่ม
    for header in random.sample(list(optional_headers.keys()), random.randint(1, 3)):  # สุ่มเลือก headers
        headers[header] = optional_headers[header]  # เพิ่มเข้าไป
    
    return headers  # คืนค่า headers


def setup_proxy_chain(proxy_list):  # ฟังก์ชันตั้งค่า proxy chain
    """Setup a chain of proxies for maximum anonymity"""  # ของฟังก์ชัน
    # This is a simplified implementation  # implementation แบบง่าย
    # In practice, would need more sophisticated proxy chaining  # ในทางปฏิบัติต้องซับซ้อนกว่านี้
    if not proxy_list or len(proxy_list) < 2:  # ถ้า proxy น้อยกว่า 2
        return None  # คืนค่า None
    
    # For now, just return the first proxy  # ตอนนี้คืน proxy แรก
    # Advanced implementation would chain them properly  # implementation จริงต้อง chain อย่างถูกต้อง
    return proxy_list[0]  # คืนค่า proxy แรก


def cleanup_temp_files():  # ฟังก์ชัน cleanup temp files
    """Clean up temporary files and logs that might contain traces"""  # ของฟังก์ชัน
    import tempfile  # นำเข้าโมดูล tempfile
    import os  # นำเข้าโมดูล os
    import glob  # นำเข้าโมดูล glob
    
    try:  # ลอง cleanup
        # Clean temp directory  # ล้าง temp directory
        temp_dir = tempfile.gettempdir()  # ได้ temp directory
        temp_files = glob.glob(os.path.join(temp_dir, "ip-hunter-*"))  # หาไฟล์ที่ขึ้นต้นด้วย ip-hunter-
        
        for file_path in temp_files:  # วนลูปไฟล์
            try:  # ลองลบไฟล์
                os.remove(file_path)  # ลบไฟล์
            except:  # ถ้าลบไม่ได้
                pass  # ข้ามไป
        
        return True, f"Cleaned {len(temp_files)} temp files"  # คืนค่าผลลัพธ์
    
    except Exception as e:  # จัดการข้อผิดพลาด
        return False, f"Cleanup failed: {str(e)}"  # คืนค่าผลลัพธ์


def generate_noise_traffic(target_url, num_requests=5):  # ฟังก์ชันสร้าง noise traffic
    """Generate noise traffic to obscure real attacks"""  # ของฟังก์ชัน
    import requests  # นำเข้าโมดูล requests
    
    noise_urls = [  # URLs สำหรับสร้าง noise
        "https://httpbin.org/get",
        "https://api.ipify.org",
        "https://checkip.amazonaws.com",
        "https://icanhazip.com",
        "https://ipinfo.io/ip"
    ]
    
    for i in range(num_requests):  # วนลูปตามจำนวน requests
        try:  # ลองส่ง request
            noise_url = random.choice(noise_urls)  # สุ่มเลือก URL
            headers = generate_stealth_headers()  # สร้าง headers แบบ stealth
            requests.get(noise_url, headers=headers, timeout=5)  # ส่ง GET request
            randomize_timing(0.5, 2.0)  # รอแบบสุ่ม
        except:  # ถ้าเกิดข้อผิดพลาด
            pass  # ข้ามไป


def create_torrc_with_bridges(bridges_list):  # ฟังก์ชันสร้าง torrc กับ bridges
    """Create Tor configuration with bridges for censorship resistance"""  # ของฟังก์ชัน
    if not bridges_list:  # ถ้าไม่มี bridges
        return ""  # คืนค่าว่าง
    
    bridges_config = "\n".join([f"Bridge {bridge}" for bridge in bridges_list])  # สร้าง config bridges
    
    torrc = f"""# Tor configuration with bridges for anti-censorship
UseBridges 1
{bridges_config}
ExitPolicy reject *:*
"""  # config พื้นฐานกับ bridges
    
    return torrc  # คืนค่า config


def stealth_mode_init():  # ฟังก์ชันเริ่มต้น stealth mode
    """Initialize stealth mode with anti-trace measures"""  # ของฟังก์ชัน
    # Clean temp files  # ล้าง temp files
    cleanup_success, cleanup_msg = cleanup_temp_files()  # เรียกฟังก์ชัน cleanup
    
    # Generate initial noise  # สร้าง noise เริ่มต้น
    generate_noise_traffic(num_requests=3)  # สร้าง noise traffic
    
    return cleanup_success, cleanup_msg  # คืนค่าผลลัพธ์