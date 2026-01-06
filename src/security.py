# Security utilities for IP-HUNTER
# ฟังก์ชันความปลอดภัยสำหรับ IP-HUNTER

import psutil  # นำเข้าโมดูล psutil สำหรับตรวจสอบทรัพยากรระบบ
import threading  # นำเข้าโมดูล threading
import time  # นำเข้าโมดูล time

# Global security limits  # ค่าจำกัดความปลอดภัยทั่วโลก
SECURITY_LIMITS = {
    'max_threads': 1000,  # จำนวนเธรดสูงสุดที่อนุญาต
    'max_sockets': 500,  # จำนวน socket สูงสุดที่อนุญาต
    'max_memory_percent': 80.0,  # เปอร์เซ็นต์หน่วยความจำสูงสุดที่อนุญาต
    'max_cpu_percent': 90.0,  # เปอร์เซ็นต์ CPU สูงสุดที่อนุญาต
    'check_interval': 5.0  # ช่วงเวลาตรวจสอบทรัพยากร (วินาที)
}

# Global controls
stop_event = threading.Event()
active_threads = 0
active_sockets = 0
thread_lock = threading.Lock()
socket_lock = threading.Lock()

def check_system_resources():
    """Check if system resources are within safe limits"""
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram_usage = psutil.virtual_memory().percent
        
        if cpu_usage > SECURITY_LIMITS['max_cpu_percent'] or ram_usage > SECURITY_LIMITS['max_memory_percent']:
            return False
        return True
    except:
        return True

def increment_thread_counter():
    """Increment active thread counter with safety check"""
    global active_threads
    with thread_lock:
        active_threads += 1

def decrement_thread_counter():
    """Decrement active thread counter"""
    global active_threads
    with thread_lock:
        active_threads = max(0, active_threads - 1)

def increment_socket_counter():
    """Increment active socket counter with safety check"""
    global active_sockets
    with socket_lock:
        active_sockets += 1

def decrement_socket_counter():
    """Decrement active socket counter"""
    global active_sockets
    with socket_lock:
        active_sockets = max(0, active_sockets - 1)

def validate_target(target):
    """Robust validation for target IP or Domain/URL"""
    if not target: return False
    import re
    ip_pattern = r'^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    domain_pattern = r'^([a-zA-Z0-9][-a-zA-Z0-9]*\.)+[a-zA-Z]{2,}(/.*)?$'
    url_pattern = r'^https?://([a-zA-Z0-9][-a-zA-Z0-9]*\.)+[a-zA-Z]{2,}(/.*)?$'

    if re.match(ip_pattern, target) or re.match(domain_pattern, target) or re.match(url_pattern, target):
        return True
    return False

class ResourceMonitor:
    """Monitor system resources during attacks"""
    # ตรวจสอบทรัพยากรระบบระหว่างการโจมตี

    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Start resource monitoring"""
        # เริ่มการตรวจสอบทรัพยากร
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop resource monitoring"""
        # หยุดการตรวจสอบทรัพยากร
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def _monitor_loop(self):
        """Main monitoring loop"""
        # ลูปการตรวจสอบหลัก
        while self.monitoring:
            try:
                if not check_system_resources():
                    from src.utils.logging import add_system_log
                    add_system_log("[bold red]CRITICAL:[/] System resources exhausted! Stopping all attacks...")
                    stop_event.set()
                    self.monitoring = False
                    break
                time.sleep(SECURITY_LIMITS['check_interval'])
            except Exception as e:
                print(f"Monitoring error: {e}")
                break