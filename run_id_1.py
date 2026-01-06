import sys
import os
import time
import threading

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.core.dispatcher import AttackDispatcher
from src.security import ResourceMonitor
from src.utils.logging import add_system_log

class MockMonitor:
    def __init__(self):
        self.packets_sent = 0
        self.bytes_sent = 0
        self.packets_failed = 0
    def update_stats(self, packets=0, bytes_sent=0, failed=0):
        self.packets_sent += packets
        self.bytes_sent += bytes_sent
        self.packets_failed += failed
        if packets > 0:
            print(f"  [+] Packets Sent: {self.packets_sent}", end="\r")

def test_id_1():
    print("🧪 Testing ID 1: Layer 7 HTTP Flood (Basic)")
    print("Target: 127.0.0.1 (Localhost)")
    print("Duration: 5 seconds")
    print("Threads: 2")
    
    monitor = MockMonitor()
    params = {
        "target": "127.0.0.1",
        "port": 80,
        "duration": 5,
        "threads": 2,
        "proxies": [],
        "max_requests": 0
    }

    # Start the attack via Dispatcher
    print("\n[!] Launching attack...")
    AttackDispatcher.execute("1", params, monitor)
    
    # Wait for completion
    start = time.time()
    while time.time() - start < 6: # Wait slightly longer than duration
        time.sleep(1)
        
    print(f"\n\n[✅] Test Finished")
    print(f"Total Success: {monitor.packets_sent}")
    print(f"Total Failed: {monitor.packets_failed}")

if __name__ == "__main__":
    test_id_1()
