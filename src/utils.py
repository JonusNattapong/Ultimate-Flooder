import os  # นำเข้าโมดูล os สำหรับการทำงานกับระบบไฟล์
import random  # นำเข้าโมดูล random สำหรับสุ่มค่า
import ctypes  # นำเข้าโมดูล ctypes สำหรับเรียกใช้ Windows API
import time
from src.config import USER_AGENTS, REFERERS  # นำเข้า User Agents และ Referers จาก config

# System logs global state
SYSTEM_LOGS = []

def add_system_log(msg):
    """Add a timestamped log entry to global dashboard"""
    # Force localized timestamp
    timestamp = time.strftime("%H:%M:%S")
    SYSTEM_LOGS.append(f"[bold dim][{timestamp}][/] {msg}")
    # Keep last 50 logs for display cycle
    if len(SYSTEM_LOGS) > 50:
        SYSTEM_LOGS.pop(0)

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


def generate_noise_traffic(num_requests=5):  # ฟังก์ชันสร้าง noise traffic
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


# VPN Management Functions  # ฟังก์ชันจัดการ VPN
def check_vpn_running(interface_name=None):  # ฟังก์ชันตรวจสอบ VPN
    """Check if VPN is running by checking network interfaces"""  # ของฟังก์ชัน
    import subprocess  # นำเข้าโมดูล subprocess
    import platform  # นำเข้าโมดูล platform
    
    system = platform.system().lower()  # ตรวจสอบระบบปฏิบัติการ
    
    try:  # ลองตรวจสอบ VPN
        if system == "windows":  # ถ้าเป็น Windows
            # Check for VPN adapters  # ตรวจสอบ VPN adapters
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)  # รัน ipconfig
            output = result.stdout.lower()  # แปลงเป็น lowercase
            vpn_indicators = ['vpn', 'tap', 'tun', 'ppp', 'nordvpn', 'expressvpn', 'protonvpn']  # คำบ่งชี้ VPN
            
            for indicator in vpn_indicators:  # วนลูปตรวจสอบ
                if indicator in output:  # ถาพบ indicator
                    return True, f"VPN detected ({indicator})"  # คืนค่าผลลัพธ์
        
        elif system in ["linux", "darwin"]:  # ถ้าเป็น Linux หรือ macOS
            # Check network interfaces  # ตรวจสอบ network interfaces
            result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)  # รัน ip route
            output = result.stdout.lower()  # แปลงเป็น lowercase
            
            # Look for VPN-related routes  # มองหา routes ที่เกี่ยวข้องกับ VPN
            vpn_indicators = ['tun', 'tap', 'ppp', 'vpn']  # คำบ่งชี้ VPN
            for indicator in vpn_indicators:  # วนลูปตรวจสอบ
                if indicator in output:  # ถาพบ indicator
                    return True, f"VPN detected ({indicator})"  # คืนค่าผลลัพธ์
        
        return False, "No VPN detected"  # คืนค่าผลลัพธ์ถ้าไม่พบ VPN
    
    except Exception as e:  # จัดการข้อผิดพลาด
        return False, f"Error checking VPN: {str(e)}"  # คืนค่าผลลัพธ์


def get_vpn_ip():  # ฟังก์ชันได้ IP ของ VPN
    """Get current public IP (useful for VPN verification)"""  # ของฟังก์ชัน
    import requests  # นำเข้าโมดูล requests
    
    try:  # ลองได้ IP
        response = requests.get('https://api.ipify.org', timeout=5)  # ส่ง request ไปยัง ipify
        if response.status_code == 200:  # ถ้าสำเร็จ
            return response.text.strip()  # คืนค่า IP
    except:  # ถ้าเกิดข้อผิดพลาด
        pass
    
    return None  # คืนค่า None ถ้าไม่ได้


# Proxy Chain Management Functions  # ฟังก์ชันจัดการ proxy chains
def create_proxy_chain(proxy_list, max_length=3):  # ฟังก์ชันสร้าง proxy chain
    """Create a randomized proxy chain for maximum anonymity"""  # ของฟังก์ชัน
    if not proxy_list or len(proxy_list) < 2:  # ถ้า proxy น้อยกว่า 2
        return proxy_list  # คืนค่า proxy list เดิม
    
    # Randomly select proxies for chain  # สุ่มเลือก proxy สำหรับ chain
    chain_length = min(max_length, len(proxy_list))  # ความยาว chain
    selected_proxies = random.sample(proxy_list, chain_length)  # สุ่มเลือก proxy
    
    # Shuffle for randomization  # สลับเพื่อ randomization
    random.shuffle(selected_proxies)  # สลับลำดับ
    
    return selected_proxies  # คืนค่า proxy chain


def setup_proxy_chain(proxy_list):  # ฟังก์ชันตั้งค่า proxy chain (updated)
    """Setup a chain of proxies for maximum anonymity"""  # ของฟังก์ชัน
    from src.config import CONFIG  # นำเข้า config
    
    if not CONFIG['PROXY_CHAIN_ENABLED']:  # ถ้าไม่ได้เปิดใช้งาน proxy chain
        return proxy_list[0] if proxy_list else None  # คืนค่า proxy แรกหรือ None
    
    # Create chain  # สร้าง chain
    chain = create_proxy_chain(proxy_list, CONFIG['PROXY_CHAIN_MAX_LENGTH'])  # สร้าง chain
    
    if len(chain) == 1:  # ถ้า chain มีแค่ 1 ตัว
        return chain[0]  # คืนค่า proxy นั้น
    
    # For multiple proxies, return the first one  # สำหรับหลาย proxy, คืนตัวแรก
    # In advanced implementation, would chain them properly  # ใน implementation จริงต้อง chain อย่างถูกต้อง
    return chain[0]  # คืนค่า proxy แรกใน chain


def validate_proxy_chain(chain):  # ฟังก์ชันตรวจสอบ proxy chain
    """Validate that all proxies in chain are working"""  # ของฟังก์ชัน
    import requests  # นำเข้าโมดูล requests
    
    valid_proxies = []  # ลิสต์ proxy ที่ valid
    
    for proxy in chain:  # วนลูปตรวจสอบแต่ละ proxy
        try:  # ลอง test proxy
            # Parse proxy URL  # แยก proxy URL
            if proxy.startswith('socks'):  # ถ้าเป็น SOCKS
                proxy_dict = {'http': proxy, 'https': proxy}  # สร้าง dict
            else:  # ถ้าเป็น HTTP
                proxy_dict = {'http': proxy, 'https': proxy}  # สร้าง dict
            
            # Test with a simple request  # ทดสอบด้วย request ง่ายๆ
            response = requests.get('http://httpbin.org/ip', proxies=proxy_dict, timeout=10)  # ส่ง request
            if response.status_code == 200:  # ถ้าสำเร็จ
                valid_proxies.append(proxy)  # เพิ่มเข้า valid list
        except:  # ถ้าเกิดข้อผิดพลาด
            continue  # ข้ามไป
    
    return valid_proxies  # คืนค่า proxy ที่ valid


def ip_tracker(target_ip=None):
    """Deep OSINT IP Tracker - Get detailed geolocation and network intel"""
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    import re
    
    console = Console()
    
    # If no IP provided, get current public IP
    if not target_ip:
        try:
            target_ip = requests.get('https://api.ipify.org', timeout=5).text.strip()
        except:
            console.print("[bold red] Error: Could not determine your public IP.[/]")
            return

    # Check for private IP ranges
    private_patterns = [
        r'^10\.',                   # 10.0.0.0 – 10.255.255.255
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.', # 172.16.0.0 – 172.31.255.255
        r'^192\.168\.',             # 192.168.0.0 – 192.168.255.255
        r'^127\.',                  # 127.0.0.0 – 127.255.255.255
        r'^169\.254\.'              # APIPA
    ]
    
    is_private = any(re.match(pattern, target_ip) for pattern in private_patterns)
    
    if is_private:
        console.print(f"\n[bold yellow]  🛰️  INITIATING DEEP TRACKING: {target_ip}[/]")
        console.print(Panel(
            f"[bold yellow]⚠️  Local/Private IP Detected[/bold yellow]\n\n"
            f"ไอพี [white]{target_ip}[/white] เป็นไอพีภายในเครือข่าย (LAN)\n"
            f"ระบบ OSINT ไม่สามารถระบุที่อยู่ทางภูมิศาสตร์ของไอพีส่วนตัวได้\n"
            f"กรุณาใช้ไอพีสาธารณะ (Public IP) เพื่อค้นหาข้อมูลที่อยู่",
            border_style="yellow", title="IP-Tracker Info"
        ))
        return

    console.print(f"\n[bold yellow]  🛰️  INITIATING DEEP TRACKING: {target_ip}[/]")
    with console.status("[bold cyan]INTELLIGENCE GATHERING FROM OSINT DATABASE...[/bold cyan]", spinner="pulse"):
        try:
            fields = "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query,reverse"
            response = requests.get(f"http://ip-api.com/json/{target_ip}?fields={fields}", timeout=10)
            data = response.json()
            
            if data.get('status') == 'fail':
                console.print(f"[bold red] Tracking Failed:[/] {data.get('message', 'Unknown error')}")
                return

            table = Table(title=f" DEEP INTEL REPORT: {target_ip}", border_style="bold blue", title_style="bold underline white")
            table.add_column("Category", style="cyan", no_wrap=True)
            table.add_column("Information", style="white")

            table.add_row(" Location", f"{data.get('city', 'N/A')}, {data.get('regionName', 'N/A')} ({data.get('region', 'N/A')}), {data.get('country', 'N/A')}")
            table.add_row(" Zip/Postal", data.get('zip', 'N/A'))
            table.add_row(" Timezone", data.get('timezone', 'N/A'))
            table.add_row(" ISP", data.get('isp', 'N/A'))
            table.add_row(" Organization", data.get('org', 'N/A'))
            table.add_row(" ASN", data.get('as', 'N/A'))
            table.add_row(" Reverse DNS", data.get('reverse', 'N/A'))
            
            lat, lon = data.get('lat'), data.get('lon')
            table.add_row(" Coordinates", f"Lat: {lat}, Lon: {lon}")
            google_maps = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            table.add_row(" Physical Map", f"[link={google_maps}][underline blue]Open in Google Maps[/link]")

            is_proxy = "[bold red]YES[/]" if data.get('proxy') else "[bold green]NO[/]"
            is_mobile = "[bold yellow]YES (Cellular)[/]" if data.get('mobile') else "[bold green]NO[/]"
            is_hosting = "[bold magenta]YES (Data Center)[/]" if data.get('hosting') else "[bold green]NO[/]"
            
            table.add_row(" Proxy/VPN", is_proxy)
            table.add_row(" Mobile Net", is_mobile)
            table.add_row(" Hosting/DC", is_hosting)

            console.print("\n")
            console.print(Panel(table, border_style="blue", expand=False))
            console.print(f"[dim]Data provided by ip-api.com OSINT database[/dim]")
            
            add_system_log(f"[cyan]OSINT:[/] Generated intel report for {target_ip}")
            
        except Exception as e:
            console.print(f"[bold red] Error connected to OSINT server:[/] {str(e)}")
            add_system_log(f"[red]ERROR:[/] OSINT lookup failed for {target_ip}")
