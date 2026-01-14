import time
import threading
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.core.dispatcher import AttackDispatcher
from src.core.menu import Menu
from src.config import CONFIG

# Target for testing
TARGET = "http://localhost:8081/"
IP_TARGET = "localhost"
DURATION = 2
THREADS = 5

def test_attack(choice):
    print(f"\n[+] Testing ID {choice}: {Menu.ATTACKS[choice]['name']}")
    
    # Prepare parameters based on ID type
    is_l7 = choice in ["1", "2", "5", "8", "12", "13", "14", "15", "16", "31", "32", "33", "34"]
    target = TARGET if is_l7 or choice == "22" else IP_TARGET
    
    params = {
        "target": target,
        "port": 8081,
        "threads": THREADS,
        "duration": DURATION,
        "max_requests": 0,
        "proxies": [],
        "use_tor": False,
        "stealth_mode": False,
        "use_vpn": False,
        "use_proxy_chain": False
    }

    try:
        # We need to handle IDs that are synchronous differently or skip them if they require interaction
        # For this test, we mostly care about attack functions (IDs 1-6, 8-16, 19, 22, 33-35)
        
        if choice in ["7", "18", "0", "26", "29", "30"]:
            print(f"[-] Skipping ID {choice} (Management/Service/Persistent)")
            return

        # Execute
        result = AttackDispatcher.execute(choice, params)
        
        # Give it some time to run if it's threaded
        time.sleep(DURATION + 1)
        print(f"[✓] Completed ID {choice}")
        
    except Exception as e:
        print(f"[✗] Error testing ID {choice}: {e}")

def main():
    print(f"Starting test for all IDs against {TARGET}")
    
    # Get all attack IDs from Menu
    ids = sorted([k for k in Menu.ATTACKS.keys() if k.isdigit()], key=int)
    
    for attack_id in ids:
        if int(attack_id) >= 1:
            test_attack(attack_id)

if __name__ == "__main__":
    main()
