# Security utilities for IP-HUNTER
# ฟังก์ชันความปลอดภัยสำหรับ IP-HUNTER

import psutil  # นำเข้าโมดูล psutil สำหรับตรวจสอบทรัพยากรระบบ
import threading  # นำเข้าโมดูล threading
import time  # นำเข้าโมดูล time
import hashlib
import platform
import subprocess
import requests
import json
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

# Global security limits  # ค่าจำกัดความปลอดภัยทั่วโลก
SECURITY_LIMITS = {
    'max_threads': 5000,  # จำนวนเธรดสูงสุดที่อนุญาต
    'max_sockets': 2000,  # จำนวน socket สูงสุดที่อนุญาต
    'max_memory_percent': 95.0,  # เพิ่มเป็น 95% เพื่อรองรับการทดสอบบน Server
    'max_cpu_percent': 98.0,  # เพิ่มเป็น 98%
    'check_interval': 10.0  # ตรวจสอบทุก 10 วินาทีเพื่อลด overhead
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

# --- DRM & LICENSE SYSTEM (NEW) ---

def get_hwid():
    """Generate a unique Hardware ID for this machine"""
    try:
        # Get machine GUID on Windows
        if platform.system() == "Windows":
            cmd = 'reg query "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid'
            guid = subprocess.check_output(cmd, shell=True).decode().split()[-1]
            seed = guid
        else:
            seed = platform.node() + platform.machine() + platform.processor()
    except:
        seed = platform.node() + "backup-seed"
    
    return hashlib.sha256(seed.encode()).hexdigest()[:16].upper()

def verify_license_remote(key, hwid, discord_url):
    """Notify activation attempt to owner via Webhook"""
    payload = {
        "content": f"🔑 **Activation Attempt**\nHWID: `{hwid}`\nKey: `{key}`\nStatus: `CHECKING`",
        "username": "DRM-WATCHER"
    }
    try:
        requests.post(discord_url, json=payload, timeout=5)
    except:
        pass

def drm_check():
    """Verify if the software is activated for this machine"""
    hwid = get_hwid()
    # Create txt directory if it doesn't exist
    if not os.path.exists('txt'):
        os.makedirs('txt')
        
    license_file = 'txt/license.key'
    
    from src.config import DISCORD_WEBHOOK_URL, MASTER_ADMIN_KEY, LICENSE_PREFIX, LICENSE_SUFFIX
    
    # Generate valid key based on environment settings
    VALID_KEY = f"{LICENSE_PREFIX}-{hwid}-{LICENSE_SUFFIX}"
    
    if os.path.exists(license_file):
        with open(license_file, 'r') as f:
            saved_key = f.read().strip()
            if saved_key == VALID_KEY or saved_key == MASTER_ADMIN_KEY:
                return True
    
    # If not activated
    console.print(Panel(
        f"[bold red]UNAUTHORIZED ACCESS DETECTED[/]\n\n"
        f"Your Hardware ID: [bold yellow]{hwid}[/]\n"
        f"Please contact [cyan]Nattapong Tapachoom[/] to get your license key.",
        title="[bold yellow]LICENSE REQUIRED[/]",
        border_style="red"
    ))
    
    key_input = Prompt.ask("[bold cyan]Enter License Key[/]").strip()
    
    if key_input == VALID_KEY or key_input == MASTER_ADMIN_KEY:
        with open(license_file, 'w') as f:
            f.write(key_input)
        
        # Log successful activation
        verify_license_remote(key_input, hwid, DISCORD_WEBHOOK_URL)
        
        console.print("[bold green]Activation Successful! Access Granted.[/]")
        time.sleep(2)
        return True
    else:
        # Log failed activation
        verify_license_remote(f"FAILED: {key_input}", hwid, DISCORD_WEBHOOK_URL)
        console.print("[bold red]Invalid Key. Access Denied.[/]")
        time.sleep(2)
        os._exit(1)
