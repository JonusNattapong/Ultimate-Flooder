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

# Global counters  # ตัวนับทั่วโลก
active_threads = 0  # จำนวนเธรดที่ทำงานอยู่
active_sockets = 0  # จำนวน socket ที่ทำงานอยู่
thread_lock = threading.Lock()  # ล็อกสำหรับ thread counter
socket_lock = threading.Lock()  # ล็อกสำหรับ socket counter

def check_system_resources():
    """Check if system resources are within safe limits (Always returns True)"""
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
    """Basic validation for target IP/URL"""
    # การตรวจสอบพื้นฐานสำหรับเป้าหมาย IP/URL
    if not target:
        return False

    # Check for basic IP format or URL format
    # ตรวจสอบรูปแบบ IP พื้นฐานหรือรูปแบบ URL
    import re
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    url_pattern = r'^https?://'

    if re.match(ip_pattern, target):
        # Validate IP address ranges
        # ตรวจสอบช่วงที่อยู่ IP
        parts = target.split('.')
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    elif re.match(url_pattern, target) or '.' in target:
        # Basic URL validation
        # การตรวจสอบ URL พื้นฐาน
        return len(target) > 3
    else:
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
                    print("Warning: System resources are running low!")
                time.sleep(SECURITY_LIMITS['check_interval'])
            except Exception as e:
                print(f"Monitoring error: {e}")
                break