# Modern CLI Interface for IP-HUNTER
# อินเทอร์เฟซ CLI สมัยใหม่สำหรับ IP-HUNTER

import os
import time
import threading
import psutil
import socket
import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.columns import Columns
from rich.align import Align
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.style import Style
from rich.layout import Layout
from rich.padding import Padding
from rich.box import DOUBLE_EDGE, HEAVY_EDGE

import platform
from src.config import BANNER, CONFIG, update_config_key
from src.core.menu import Menu
from src.core.dispatcher import AttackDispatcher
from src import security
from src.utils import (
    load_file_lines, auto_start_tor_if_needed, check_tor_running,
    generate_stealth_headers, check_vpn_running, auto_connect_vpn,
    add_system_log, SYSTEM_LOGS, stealth_mode_init,
    send_telemetry
)
from src.attacks.tools import proxy_autopilot
from src.utils.ui import create_cyber_progress, create_attack_config_panel, create_monitoring_dashboard
from src.utils.network import get_vpn_ip
from src.utils.system import cleanup_temp_files
from src.core.ai_orchestrator import AIOrchestrator, TargetProfile, AttackSuggestion

# Initialize Rich Console with optimized settings for Windows
console = Console(force_terminal=True, color_system="auto")

# Matrix Hacker theme: green ASCII header and helpers
MATRIX_ASCII = r"""
██╗██████╗       ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
██║██╔══██╗      ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
██║██████╔╝█████╗███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██║██╔═══╝ ╚════╝██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██║██║           ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═╝╚═╝           ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                                       
"""

def matrix_header(typewriter=False, speed=0.002):
    """Display a Matrix-style ASCII header (fast typewriter optional)"""
    panel = Panel(Text(MATRIX_ASCII, style="green"), border_style="bright_green")
    if not typewriter:
        console.print(panel)
        return
    # Typewriter effect (fast and optional)
    for line in MATRIX_ASCII.splitlines():
        console.print(Text(line, style="green"))
        time.sleep(speed)
    console.print(Panel(Text("[bold green]IP-HUNTER — MATRIX MODE[/bold green]"), border_style="bright_green"))


def matrix_loader(duration=2.5, fps=18):
    """Matrix-style loading animation used on startup.

    This renders a 2-column live panel: system checks (left) and a matrix stream (right),
    with a progress bar footer. It's lightweight and uses only Rich primitives.
    """
    import shutil

    # Ensure terminal size functions gracefully fall back
    try:
        term_width = shutil.get_terminal_size((80, 24)).columns
    except Exception:
        term_width = 80

    steps = [
        "KERNEL_CORE: SYSCALL_INIT",
        "SESS_AUTH: AUTHENTICATING_USER",
        "SECURE_LAYER: BYPASSING_SANDBOX",
        "NET_TUNNEL: ESTABLISHING_NODES",
        "MODULE_PATCH: MEM_INJECTION",
        "INTEL_RECON: DATA_SYNC"
    ]

    start = time.time()
    frame = 0
    total_frames = max(1, int(duration * fps))

    # Detect plain PowerShell / limited terminals and adjust animation accordingly
    is_windows = os.name == 'nt'
    is_windows_terminal = bool(os.environ.get('WT_SESSION') or os.environ.get('TERM_PROGRAM') == 'Windows Terminal')

    # Gentle fallback for plain PowerShell (reduce FPS and stream density)
    if is_windows and not is_windows_terminal:
        fps = min(fps, 8)
        duration = max(duration, 2.0)
        stream_rows = 3
    else:
        stream_rows = 6

    with Live(refresh_per_second=fps, transient=True) as live:
        while True:
            elapsed = time.time() - start
            pct = min(100.0, (elapsed / duration) * 100.0)
            done = int((pct / 100.0) * 40)
            p_bar = "█" * done + "▒" * (40 - done)

            # Build left column (checks)
            completed = int((elapsed / duration) * len(steps))
            left_text = Text()
            for i, s in enumerate(steps):
                if i < completed:
                    left_text.append(f"[green]✔ {s}[/]\n")
                else:
                    left_text.append(f"[dim]  {s}[/]\n")

            # Build matrix-like middle stream (random hex/data) smaller than terminal width
            stream_lines = []
            for _ in range(stream_rows):
                # Limit per-line width to avoid overflowing terminal and causing artifacts
                if is_windows and not is_windows_terminal:
                    chunk_len = max(6, min(24, term_width // 12))
                else:
                    chunk_len = max(8, min(32, term_width // 8))
                line = " ".join("".join(random.choice("0123456789ABCDEF") for _ in range(chunk_len)))
                stream_lines.append(line)
            mid_text = Text("\n".join(stream_lines), style="green")

            # Compose table view
            view = Table.grid(expand=True)
            view.add_column(ratio=1)
            view.add_column(ratio=2)
            view.add_row(
                Panel(left_text, title="[bold green]SYSTEM CHECKS[/bold green]", border_style="bright_green"),
                Panel(mid_text, title="[bold green]MATRIX STREAM[/bold green]", border_style="bright_green")
            )

            footer = Align.center(Text.from_markup(f"[bold green]{p_bar}[/] [dim]{pct:>5.1f}%[/]  [dim]Initializing...[/dim]"))
            container = Table.grid(expand=True)
            container.add_row(view)
            container.add_row(Panel(footer, border_style="green"))

            live.update(Panel(container, border_style="bright_green"))

            frame += 1
            if elapsed >= duration:
                break
            time.sleep(1.0 / fps)

    # Clear console after animation to avoid overlapping output
    try:
        console.clear()
    except Exception:
        # Best-effort clear; continue if clearing fails
        pass

    # Final success message
    console.print(Panel(Text("[bold bright_green]ACCESS GRANTED — WELCOME[/bold bright_green]"), border_style="bright_green", padding=(1, 2)))


class AttackMonitor:
    """Real-time attack monitoring system - Movie Style HUD"""

    def __init__(self, attack_name, target, duration, max_requests=0):
        self.attack_name = attack_name
        self.target = target
        self.duration = duration
        self.max_requests = max_requests
        self.start_time = time.time()
        self.packets_sent = 0
        self.packets_failed = 0
        self.bytes_sent = 0
        self.active_connections = 0
        self.monitoring = False
        self.monitor_thread = None
        self._lock = threading.Lock()
        
        # Initialize Layout for Cyberpunk HUD - Compact & High-Tech
        self.layout = Layout()
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", size=18), # Locked size to prevent jumping/flickering
            Layout(name="footer", size=3)
        )
        self.layout["body"].split_row(
            Layout(name="left", ratio=3),
            Layout(name="right", ratio=1)
        )
        self.layout["left"].split_column(
            Layout(name="stats_top", size=10),
            Layout(name="logs_bottom", ratio=1)
        )

    def start_monitoring(self):
        """Start the monitoring thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def update_stats(self, packets=0, bytes_sent=0, connections=0, failed=0):
        """Update attack statistics (Thread-Safe)"""
        with self._lock:
            self.packets_sent += packets
            self.bytes_sent += bytes_sent
            if connections > 0:
                self.active_connections = connections
            self.packets_failed += failed

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            time.sleep(1)

    def get_stats_panel(self):
        """Generate a Cinema-style Matrix/Hacker HUD - Optimized for absolute stability & zero flicker"""
        with self._lock:
            elapsed = time.time() - self.start_time
            p_sent = self.packets_sent
            p_failed = self.packets_failed
            b_sent = self.bytes_sent
            a_conns = self.active_connections
        
        # Consistent frame counter
        v_frame = int(time.time() * 2)
        
        if self.max_requests > 0:
            progress_percent = min(100, (self.packets_sent / self.max_requests) * 100)
        else:
            progress_percent = min(100, (elapsed / self.duration) * 100)

        # Cache cpu/mem to avoid high-frequency jitter (Every 2 seconds)
        if not hasattr(self, '_last_sys_check') or time.time() - self._last_sys_check > 2.0:
            try:
                self._cpu = psutil.cpu_percent()
                self._mem = psutil.virtual_memory().percent
            except:
                self._cpu = self._mem = 0
            self._last_sys_check = time.time()

        # --- HEADER SECTION ---
        phase_idx = int(elapsed / 2) % 4
        phase = ["[dim]INIT[/]", "[bold green]SYNC[/]", "[bold green]FLOW[/]", "[bold green]PEAK[/]"][phase_idx]
        
        # Fixed length target display to prevent shifting
        safe_target = (self.target[:30] + '..') if len(self.target) > 32 else self.target.ljust(32)
        
        header_content = Text.from_markup(
            f" [bold red]•[/][bold white] ROOT_SESSION [/][bold red]•[/]   "
            f"[bold green]TARGET:[/][white] {safe_target} [/]   "
            f"[bold green]PHASE:[/][bold green] {phase} [/]   "
            f"[bold white]T+ {int(elapsed):>4}s[/]"
        )
        
        header_panel = Panel(
            Align.center(header_content, vertical="middle"),
            border_style="bright_green",
            box=DOUBLE_EDGE,
            padding=(0,1)
        )
        self.layout["header"].update(header_panel)

        # --- LEFT STATS TOP ---
        pps = p_sent / max(1, elapsed)
        bps = b_sent / max(1, elapsed) / 1024 / 1024 # MB/s
        total_p = p_sent + p_failed
        success_rate = (p_sent / max(1, total_p)) * 100
        
        net_table = Table(show_header=True, header_style="bold magenta", box=HEAVY_EDGE, expand=True, show_edge=True)
        net_table.add_column("VECTOR_METRIC", style="bold cyan", ratio=1)
        net_table.add_column("LIVE_FEED", style="bold white", ratio=1, justify="center")
        net_table.add_column("STATUS", justify="right", ratio=1)
        
        net_table.add_row("⚡ PACKET_VELOCITY", f"{pps:,.0f} PPS", "[bold green]ONLINE[/]")
        net_table.add_row("🌊 BITSTREAM_FLOW", f"{bps:.2f} MB/s", "[bold white]ACTIVE[/]")
        net_table.add_row("📦 TOTAL_PAYLOAD", f"{p_sent:,}", "[bold magenta]INJECTING[/]")
        
        status_color = "green" if success_rate > 90 else "white" if p_sent == 0 else "yellow" if success_rate > 50 else "red"
        net_table.add_row("🎯 INTEGRITY_INDEX", f"{success_rate:.1f}%", f"[bold {status_color}]SYNCED[/]")

        self.layout["stats_top"].update(Panel(net_table, title="[ REALTIME_INTEL_STREAM ]", border_style="bright_green", padding=(0,1)))

        # --- LEFT LOGS BOTTOM ---
        # Persistent logs instead of random ones per frame
        if not hasattr(self, '_cached_logs'):
            self._cached_logs = [
                "> INJECTING PAYLOAD DATA...",
                "> BYPASSING SECURE_TUNNEL...",
                "> ENCRYPTING DATASTREAM...",
                "> TARGET_BUFFER_SYNC..."
            ]
        
        log_content = Text()
        for log in self._cached_logs:
            log_content.append(f"{log}\n", style="dim green")
        
        self.layout["logs_bottom"].update(Panel(log_content, title="[ KERNEL_LOG_PIPE ]", border_style="green"))

        # --- RIGHT SIDE: SYSTEM INFO ---
        sys_table = Table.grid(padding=0)
        sys_table.add_column(style="bold yellow")
        sys_table.add_column(style="white", justify="right")
        
        sys_table.add_row(" CPU_USE", f"{self._cpu}%")
        sys_table.add_row(" MEM_USE", f"{self._mem}%")
        sys_table.add_row(" THREADS", f"{security.active_threads:>4}")
        sys_table.add_row(" SOCKETS", f"{security.active_sockets:>4}")
        sys_table.add_row("", "")
        
        seed = int(time.time() / 5) * 12345
        sys_table.add_row("[red] CRYPTO[/]", f"[dim]{abs(hash(seed)) % 0xFFFFFFFF:X}[/]")
        sys_table.add_row("[red] CYPHER[/]", "[dim]AES-GCM[/]")
        
        status_msg = "OPTIMAL" if success_rate > 5 or self.packets_sent == 0 else "WARN"
        status_color = "green" if status_msg == "OPTIMAL" else "red"
        sys_table.add_row("", "")
        sys_table.add_row(" STATUS", f"[bold {status_color}]{status_msg}[/]")
        
        # Pulse indicator
        pulse = "⚡" if (v_frame // 2) % 2 == 0 else " "
        sys_table.add_row("", "")
        sys_table.add_row(f" [magenta]{pulse}[/] SIGNAL", "[magenta]ACTIVE[/]")

        self.layout["right"].update(Panel(sys_table, title="[ HUB_STATUS ]", border_style="green", padding=(1,1)))


        # --- FOOTER: PROGRESS ---
        # Locked width bar
        done = int((progress_percent / 100) * 50)
        p_bar = "█" * done + "▒" * (50 - done)
        footer_content = Align.center(
            Text.from_markup(f"[bold green]TARGET:[/] [white]{self.target[:25]:<25}[/] [bold green]PROG:[/] [bold green]{p_bar}[/] [bold white]{progress_percent:>5.1f}%[/]")
        )
        self.layout["footer"].update(Panel(footer_content, border_style="bright_green", box=DOUBLE_EDGE))

        return self.layout

# Global monitor instance
current_monitor = None

class ModernCLI:
    """Modern CLI interface using Rich library"""
    
    # Background services tracking
    c2_server = None
    active_bot = None
    active_monitors = []
    
    # Locked Targets Library
    locked_targets = []

    # Status Caching for smoother menu
    _cached_tor_status = None
    _last_tor_check = 0
    
    # AI Orchestrator
    ai_orch = AIOrchestrator()

    @staticmethod
    def manage_targets():
        """Target Library Management Sub-menu - Optimized for speed"""
        while True:
            console.clear()
            console.print(Align.center(Text(BANNER, style="bold cyan")))

            
            table = Table(title="💎 [bold green]Target Library (Locked Targets)[/bold green]", border_style="bright_green", expand=True)
            table.add_column("ID", style="cyan", justify="center", width=4)
            table.add_column("Target Address", style="white")
            table.add_column("Status", style="green", justify="center")

            for idx, target in enumerate(ModernCLI.locked_targets, 1):
                table.add_row(str(idx), target, "[bold green]LOCKED[/bold green]")
            
            if not ModernCLI.locked_targets:
                table.add_row("-", "No targets in library", "[dim]Empty[/dim]")

            console.print(table)
            
            console.print(Panel(
                "[bold white][A][/bold white] Add New Target  |  "
                "[bold white][D][/bold white] Delete Target  |  "
                "[bold white][C][/bold white] Clear All  |  "
                "[bold white][B][/bold white] Back to Menu",
                title="[bold green] Target Management Options [/bold green]",
                border_style="bright_green"
            ))

            op = Prompt.ask("[bold green]Select Action[/bold green]", choices=["a", "d", "c", "b"], default="b").lower()
            
            if op == 'a':
                new_target = Prompt.ask("[bold green]Enter Target (IP or URL)[/bold green]").strip()
                if new_target and new_target not in ModernCLI.locked_targets:
                    ModernCLI.locked_targets.append(new_target)
                    add_system_log(f"[green]LIBRARY:[/] Added {new_target} to targets list")
            elif op == 'd':
                if not ModernCLI.locked_targets:
                    continue
                try:
                    # Let user enter ID or Target Address
                    del_input = Prompt.ask("[bold red]Enter ID or Target to remove[/bold red]").strip()
                    
                    if del_input.isdigit():
                        idx = int(del_input) - 1
                        if 0 <= idx < len(ModernCLI.locked_targets):
                            removed = ModernCLI.locked_targets.pop(idx)
                            add_system_log(f"[yellow]LIBRARY:[/] Removed {removed} from targets list")
                    elif del_input in ModernCLI.locked_targets:
                        ModernCLI.locked_targets.remove(del_input)
                        add_system_log(f"[yellow]LIBRARY:[/] Removed {del_input} from targets list")
                    else:
                        console.print("[bold red]❌ Target/ID not found in library[/bold red]")
                        time.sleep(1)
                except Exception as e:
                    console.print(f"[bold red]❌ Error: {e}[/bold red]")
                    time.sleep(1)
            elif op == 'c':
                ModernCLI.locked_targets.clear()
                add_system_log("[red]LIBRARY:[/] Cleared all locked targets")
            elif op == 'b':
                break

    @staticmethod
    def display_banner():
        """Display the top header panel in Matrix style"""
        matrix_header()
        subtitle = Panel(
            "[bold green]Advanced DDoS Tool v2.1.0 - Matrix Mode — Educational Purposes Only[/bold green]",
            border_style="bright_green",
            padding=(0, 1)
        )
        console.print(subtitle)
        console.print()

    @staticmethod
    def display_menu():
        """Returns the menu with a Classic Terminal / Hacker aesthetic"""
        # Classic Header (Matrix-themed)
        classic_banner = Align.center(Text(BANNER, style="bold green"))
        
        # Menu Columns (3 columns for classic density)
        menu_grid = Table.grid(expand=True, padding=0)

        menu_grid.add_column(ratio=1)
        menu_grid.add_column(ratio=1)
        menu_grid.add_column(ratio=1)

        attacks = Menu.ATTACKS
        keys = sorted([k for k in attacks.keys() if k.isdigit()], key=int)
        
        # Distribute keys into 3 columns
        total = len(keys)
        per_col = (total + 2) // 3
        
        rows = []
        for i in range(per_col):
            row_data = []
            for j in range(3):
                idx = i + (j * per_col)
                if idx < total:
                    k = keys[idx]
                    name = attacks[k]["name"]
                    # Classic look: [01] Attack Name
                    row_data.append(f"[bold green][{k.zfill(2)}][/bold green] [white]{name[:28]}[/white]")
                else:
                    row_data.append("")
            rows.append(row_data)

        for r in rows:
            menu_grid.add_row(*r)

        # Status Line (Classic Style) with Caching for smoothness
        c2_status = "[bold green]ONLINE[/bold green]" if ModernCLI.c2_server and ModernCLI.c2_server.running else "[bold red]OFFLINE[/bold red]"
        
        # Only check TOR every 5 seconds to prevent menu lag
        if time.time() - ModernCLI._last_tor_check > 5.0 or ModernCLI._cached_tor_status is None:
            ModernCLI._cached_tor_status = "[bold green]ACTIVE[/bold green]" if check_tor_running() else "[bold red]INACTIVE[/bold red]"
            ModernCLI._last_tor_check = time.time()
        
        tor_status = ModernCLI._cached_tor_status
        target_count = len(ModernCLI.locked_targets)

        
        status_line = Padding(
            Text.from_markup(
                f"STATUS: C2:{c2_status} | TOR:{tor_status} | TARGETS:[bold green]{target_count}[/bold green] | "
                f"SYSTEM:[bold green]{platform.system().upper()}[/bold green]"
            ),
            (1, 0)
        )

        # Build final classic layout
        layout = Table.grid(expand=True)
        layout.add_column()
        layout.add_row(classic_banner)
        layout.add_row(Panel(menu_grid, title="[bold white] CORE COMMANDS [/bold white]", border_style="bright_green"))
        layout.add_row(status_line)
        
        # Mini Logs at the bottom
        if SYSTEM_LOGS:
            logs = "\n".join(SYSTEM_LOGS[-5:])
            layout.add_row(Panel(logs, title="[bold green] SYSTEM_OUTPUT [/bold green]", border_style="bright_green"))

        return layout

    @staticmethod
    def get_choice():
        """Get user choice with modern prompt"""
        try:
            choice = Prompt.ask("[bold green]Enter your choice[/bold green]").strip().lower()

            if choice in ['q', 'quit', 'exit']:
                ModernCLI.display_goodbye()
                return None

            if choice == "00" and ModernCLI.c2_server and ModernCLI.c2_server.running:
                return "00"

            if choice not in Menu.ATTACKS:
                console.print("[bold red]❌ Invalid choice! Please select a valid option.[/bold red]")
                return ModernCLI.get_choice()

            return choice

        except KeyboardInterrupt:
            ModernCLI.display_goodbye()
            return None
        except EOFError:
            ModernCLI.display_goodbye()
            return None

    @staticmethod
    def get_attack_params(choice):
        """Get attack parameters with modern prompts"""
        if choice == "00": # C2 Shell
            return {}

        if choice == "0": # Target Management
            ModernCLI.manage_targets()
            return None

        if choice == "20":  # Network Recon
            panel = Panel("[bold green]Network Recon / Discovery[/bold green]\n[dim]Scans the local network for active devices and services.[/dim]", border_style="bright_green")
            console.print(panel)
            subnet = Prompt.ask("[bold green]Enter Subnet to Scan (e.g. 192.168.1.0/24 or 10.0.0.0/16)[/bold green]", default="auto")
            subnet = None if subnet == "auto" else subnet
            threads = IntPrompt.ask("[bold green]Parallel Scan Threads[/bold green]", default=250)
            return {"threads": threads, "subnet": subnet, "target": "local", "port": 0, "duration": 0, "proxies": []}

        if choice == "21":  # IP Tracker
            ip = Prompt.ask("[bold green]Enter IP Address to Track (Leave empty for yours)[/bold green]").strip()
            return {
                "ip": ip if ip else None, 
                "target": ip if ip else "Current IP", 
                "duration": 0, 
                "threads": 1, 
                "port": 0,
                "proxies": []
            }

        if choice == "22": # AI-Adaptive Smart Flood
            panel = Panel("[bold green]AI-Adaptive Smart Flood[/bold green]\n[dim]Autonomous intensity adjustment based on server feedback.[/dim]", border_style="bright_green")
            console.print(panel)
            target = Prompt.ask("[bold green]Target URL[/bold green]").strip()
            threads = IntPrompt.ask("[bold green]Threads[/bold green]", default=50)
            duration = IntPrompt.ask("[bold green]Duration[/bold green]", default=60)
            return {"target": target, "threads": threads, "duration": duration, "proxies": [], "port": 80}

        if choice == "23": # Vulnerability Scout
            panel = Panel("[bold green]Vulnerability Scout[/bold green]\n[dim]Rapid scan for sensitive files and misconfigurations.[/dim]", border_style="bright_green")
            console.print(panel)
            target = Prompt.ask("[bold green]Target URL[/bold green]").strip()
            return {"target": target, "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "24": # Brute-Force Suite
            panel = Panel("[bold green]Brute-Force Suite[/bold green]\n[dim]Trial matching common credentials for services.[/dim]", border_style="bright_green")
            console.print(panel)
            target = Prompt.ask("[bold green]Target Host/IP[/bold green]").strip()
            service = Prompt.ask("[bold green]Service (FTP/HTTP)[/bold green]", default="FTP").strip()
            username = Prompt.ask("[bold green]Username[/bold green]", default="admin").strip()
            return {"target": target, "service": service, "username": username, "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "25": # Domain OSINT
            panel = Panel("[bold green]Domain OSINT Multi-Hunter[/bold green]\n[dim]Hunt subdomains and DNS intelligence.[/dim]", border_style="bright_green")
            console.print(panel)
            target = Prompt.ask("[bold green]Domain (e.g. google.com)[/bold green]").strip()
            return {"target": target, "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "26": # Proxy Autopilot
            panel = Panel("[bold green]Proxy Autopilot[/bold green]\n[dim]Auto-scrapes and validates fresh HTTP/SOCKS proxies.[/dim]", border_style="bright_green")
            console.print(panel)
            return {"target": "localhost", "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "27": # WiFi Ghost
            panel = Panel("[bold green]WiFi Ghost Recon[/bold green]\n[dim]Passive scanning of surrounding airwaves (Requires Admin).[/dim]", border_style="bright_green")
            console.print(panel)
            return {"target": "local", "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "28": # Packet Insight
            panel = Panel("[bold green]Packet Insight (Sniffer)[/bold green]\n[dim]Live deep packet inspection of local traffic.[/dim]", border_style="bright_green")
            console.print(panel)
            duration = IntPrompt.ask("[bold green]Sniff Duration (seconds)[/bold green]", default=10)
            return {"target": "sniffer", "duration": duration, "threads": 1, "port": 0, "proxies": []}

        if choice == "29": # Payload Lab
            panel = Panel("[bold green]Payload Lab[/bold green]\n[dim]Generate obfuscated payloads for authorized testing.[/dim]", border_style="bright_green")
            console.print(panel)
            return {"target": "payload", "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "30": # Identity Cloak
            panel = Panel("[bold green]Identity Cloak (OpSec)[/bold green]\n[dim]Randomizes MAC address and machine hostname.[/dim]", border_style="bright_green")
            console.print(panel)
            return {"target": "privacy", "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "31": # CVE Explorer
            panel = Panel("[bold green]CVE Explorer[/bold green]\n[dim]Search public vulnerability databases (NVD/CIRCL) by keyword.[/dim]", border_style="bright_green")
            console.print(panel)
            keyword = Prompt.ask("[bold green]Search Keyword (e.g. windows, apache, cisco)[/bold green]").strip()
            return {"target": "CVE-Database", "keyword": keyword, "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "32": # Web Exposure Sniper
            panel = Panel("[bold green]Web Exposure Sniper[/bold green]\n[dim]Active hunting for data leaks, sensitive files, and misconfigurations on a target website.[/dim]", border_style="bright_green")
            console.print(panel)
            
            # AI Key Management
            api_key = CONFIG.get('OPENROUTER_API_KEY')
            if not api_key:
                console.print("[yellow]⚠️  OpenRouter API Key not found.[/yellow]")
                api_key = Prompt.ask("[bold green]Enter OpenRouter API Key (to enable AI recon)[/bold green]").strip()
                if api_key:
                    CONFIG['OPENROUTER_API_KEY'] = api_key
                    save = Prompt.ask("[yellow]Save this key permanently to config.py?[/yellow]", choices=["y", "n"], default="y")
                    if save == "y":
                        if update_config_key('OPENROUTER_API_KEY', api_key):
                            console.print("[bold green]✅ API Key saved permanently.[/bold green]")
                        else:
                            console.print("[bold red]❌ Failed to save key to file.[/bold red]")
                    else:
                        console.print("[bold green]✅ API Key set for this session only.[/bold green]")
            
            target = Prompt.ask("[bold yellow]Target URL (e.g. target-web.com)[/bold yellow]").strip()
            return {"target": target, "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "7":  # C2 Server
            panel = Panel(
                "[bold green]Botnet C2 Server Configuration[/bold green]",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(panel)

            try:
                c2_port = IntPrompt.ask(
                    "[bold yellow]C2 Port[/bold yellow]",
                    default=CONFIG['C2_DEFAULT_PORT']
                )

                if not (1 <= c2_port <= 65535):
                    console.print("[bold red]❌ Port must be between 1 and 65535[/bold red]")
                    return ModernCLI.get_attack_params(choice)

                return {"c2_port": c2_port}

            except ValueError:
                console.print("[bold red]❌ Invalid port number[/bold red]")
                return ModernCLI.get_attack_params(choice)

        if choice == "18":  # Bot Client
            panel = Panel(
                "[bold cyan]Local Bot Client Configuration[/bold cyan]\n"
                "[dim]Start a local bot instance to connect to your C2 server.[/dim]",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(panel)

            c2_host = Prompt.ask("[bold yellow]C2 Server Host[/bold yellow]", default="127.0.0.1")
            c2_port = IntPrompt.ask("[bold yellow]C2 Server Port[/bold yellow]", default=CONFIG['C2_DEFAULT_PORT'])
            
            return {"c2_host": c2_host, "c2_port": c2_port}

        if choice == "17":  # Port Scanner
            panel = Panel(
                f"[bold cyan]Port Scanner Configuration[/bold cyan]\n\n"
                f"[bold white]Example Ranges:[/bold white]\n"
                f"• Web: 80,443\n"
                f"• Games: 25565,30120,7777\n"
                f"• Databases: 3306,5432\n"
                f"• Full: 1-65535",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(panel)

            target = Prompt.ask("[bold yellow]Target (IP or Hostname)[/bold yellow]").strip()
            if not target:
                return ModernCLI.get_attack_params(choice)

            port_input = Prompt.ask("[bold yellow]Ports (e.g. 80,443 or 1-1024)[/bold yellow]", default="1-1000").strip()
            
            # Parse ports
            ports = []
            try:
                if "-" in port_input:
                    start, end = map(int, port_input.split("-"))
                    ports = list(range(start, end + 1))
                else:
                    ports = [int(p.strip()) for p in port_input.split(",")]
            except:
                console.print("[bold red]❌ Invalid port format![/bold red]")
                return ModernCLI.get_attack_params(choice)

            threads = IntPrompt.ask("[bold yellow]Threads[/bold yellow]", default=100)
            stealth = Prompt.ask("[bold yellow]Enable Stealth Mode (SYN Scan)?[/bold yellow]", choices=["y", "n"], default="y") == "y"
            
            return {
                "target": target,
                "ports": ports,
                "port_text": port_input, # for display
                "threads": threads,
                "stealth_mode": stealth,
                "duration": 0, # Not used
                "proxies": [] # Not used
            }

        # Standard attack parameters
        attack_info = Menu.ATTACKS.get(choice)
        if not attack_info:
            return None

        # Categorize attack
        is_l7 = choice in ["1", "2", "5", "8", "12", "13", "14", "15", "16", "33", "34"]
        is_l4 = choice in ["3", "4", "19", "35"]
        is_amp = choice in ["6", "9", "10", "11"]

        # Display category-specific panel
        if is_l7:
            example = "http://example.com"
            description = "Layer 7 (Application) attack targeting web services."
        elif is_l4:
            example = "1.2.3.4"
            description = "Layer 4 (Transport) attack targeting network protocols."
        elif is_amp:
            example = "Target IP"
            description = "Amplification attack using vulnerable reflection servers."
        else:
            example = "Target"
            description = "Special attack configuration."

        panel = Panel(
            f"[bold green]{attack_info['name']}[/bold green]\n"
            f"[dim]{description}[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(panel)

        # Target input
        if ModernCLI.locked_targets:
            console.print(Panel(
                f"[bold green]🎯 Target Locked Selection[/bold green]\n"
                f"You have [bold yellow]{len(ModernCLI.locked_targets)}[/bold yellow] targets in your library.",
                border_style="cyan"
            ))
            for i, t in enumerate(ModernCLI.locked_targets, 1):
                console.print(f"  [bold green][{i}][/bold green] {t}")
            
            t_choice = Prompt.ask("[bold yellow]Select ID or enter NEW target address[/bold yellow]").strip()
            
            try:
                t_idx = int(t_choice) - 1
                if 0 <= t_idx < len(ModernCLI.locked_targets):
                    target = ModernCLI.locked_targets[t_idx]
                else:
                    target = t_choice
            except ValueError:
                target = t_choice
        else:
            target_prompt = "[bold yellow]Target (IP or URL)[/bold yellow]" if is_l7 else "[bold yellow]Target (IP Address)[/bold yellow]"
            target = Prompt.ask(target_prompt).strip()

        if not target:
            console.print("[bold red]❌ Target cannot be empty![/bold red]")
            return ModernCLI.get_attack_params(choice)

        if not security.validate_target(target):
            console.print("[bold red]❌ Invalid target format![/bold red]")
            return ModernCLI.get_attack_params(choice)

        # AI Reconnaissance & Suggestion Hook
        if Confirm.ask("[bold green]Perform AI Deep Recon & Strategy Suggestion?[/bold green]", default=False):
            suggestions = ModernCLI._run_ai_recon(target)
            if suggestions:
                selected = ModernCLI._display_ai_suggestions(suggestions)
                if selected:
                    # Auto-fill parameters from AI suggestion
                    console.print(f"[bold green]✅ AI Strategy Applied:[/] [white]{selected.attack_name}[/white]")
                    params.update({
                        "threads": selected.recommended_threads,
                        "duration": selected.recommended_duration,
                        "use_tor": selected.use_tor,
                        "stealth_mode": selected.use_stealth,
                        "ai_suggestion": selected
                    })
                    # Special case: AI might suggest a different attack vector than current choice
                    if selected.attack_id != choice:
                        console.print(f"[bold yellow]⚠️  AI recommends switching to {selected.attack_name} (ID {selected.attack_id})[/bold yellow]")
                        if Confirm.ask("Switch to recommended attack?", default=True):
                            choice = selected.attack_id
                            # Re-fetch attack_info for correct display later
                            attack_info = Menu.ATTACKS.get(choice)

        # Port input
        port = 0
        if choice != "19": # ICMP doesn't need port
            try:
                default_port = 80 if is_l7 else (CONFIG['DEFAULT_PORT'])
                port = IntPrompt.ask(
                    "[bold yellow]Port[/bold yellow]",
                    default=default_port
                )
            except ValueError:
                console.print("[bold red]❌ Invalid port number[/bold red]")
                return ModernCLI.get_attack_params(choice)

        # Threads input
        threads = IntPrompt.ask("[bold yellow]Threads[/bold yellow]", default=CONFIG['DEFAULT_THREADS'])

        # Duration input
        duration = IntPrompt.ask("[bold yellow]Duration (seconds)[/bold yellow]", default=CONFIG['DEFAULT_DURATION'])

        # Max Requests and Proxy (Mostly for L7)
        max_requests = 0
        proxies = []
        use_tor = False
        stealth_mode = False 
        use_vpn = False
        use_proxy_chain = False

        if is_l7:
            max_requests = IntPrompt.ask("[bold yellow]Total Requests (0 for unlimited)[/bold yellow]", default=0)
            proxy_file = Prompt.ask(f"[bold yellow]Proxy file[/bold yellow] [dim]({CONFIG['PROXY_FILE']})[/dim]", default="").strip()
            if proxy_file:
                if os.path.isfile(proxy_file):
                    proxies = load_file_lines(proxy_file)
                    console.print(f"[green]✅ Loaded {len(proxies)} proxies[/green]")
            
            use_tor = CONFIG.get('FORCE_AUTO_PROTECT', False) or Prompt.ask("[bold yellow]Use Tor for anonymity? (y/n)[/bold yellow]", default="y").strip().lower() == 'y'
            if use_tor:
                console.print("[cyan]🔄 Checking Tor status...[/cyan]")
                tor_success, tor_message = auto_start_tor_if_needed(CONFIG['TOR_PORT'])
                if tor_success:
                    console.print(f"[green]✅ {tor_message}[/green]")
                else:
                    console.print(f"[red]❌ {tor_message}[/red]")
                    console.print("[yellow]⚠️  Continuing without Tor...[/yellow]")
                    use_tor = False
            
            stealth_mode = CONFIG.get('FORCE_AUTO_PROTECT', False) or Prompt.ask("[bold yellow]Enable stealth mode (advanced anti-trace)? (y/n)[/bold yellow]", default="y").strip().lower() == 'y'
            if stealth_mode:
                console.print("[cyan]🛡️  Initializing stealth mode...[/cyan]")
                cleanup_success, cleanup_msg = stealth_mode_init()
                if cleanup_success:
                    console.print(f"[green]✅ {cleanup_msg}[/green]")
                else:
                    console.print(f"[red]❌ {cleanup_msg}[/red]")
                console.print("[green]✅ Stealth mode activated[/green]")
            
            # VPN Integration
            use_vpn = CONFIG.get('FORCE_AUTO_PROTECT', False) or Prompt.ask("[bold yellow]Use VPN for additional protection? (y/n)[/bold yellow]", default="y").strip().lower() == 'y'
            if use_vpn:
                console.print("[cyan]🔍 Checking VPN status...[/cyan]")
                # Try auto-connect first
                console.print("[cyan]🛡️  Ensuring VPN protection...[/cyan]")
                auto_connect_vpn()
                
                vpn_running, vpn_message = check_vpn_running()
                if vpn_running:
                    console.print(f"[green]✅ {vpn_message}[/green]")
                    vpn_ip = get_vpn_ip()
                    if vpn_ip:
                        console.print(f"[blue]📍 VPN IP: {vpn_ip}[/blue]")
                else:
                    console.print(f"[red]❌ {vpn_message}[/red]")
                    console.print("[yellow]⚠️  Please connect to VPN manually before running attacks[/yellow]")
                    console.print("[yellow]💡  Supported VPNs: NordVPN, ExpressVPN, ProtonVPN[/yellow]")
                    use_vpn = False
            
            use_proxy_chain = CONFIG.get('FORCE_AUTO_PROTECT', False)
            if not proxies and use_proxy_chain:
                console.print("[cyan]🔄 Auto-scraping proxies for maximum protection...[/cyan]")
                proxies = proxy_autopilot(silent=True)
                if proxies:
                    console.print(f"[green]✅ Auto-loaded {len(proxies)} fresh proxies[/green]")

            if proxies:
                if not CONFIG.get('FORCE_AUTO_PROTECT', False):
                    use_proxy_chain = Prompt.ask("[bold yellow]Enable proxy chain rotation? (y/n)[/bold yellow]", default="y").strip().lower() == 'y'
                
                if use_proxy_chain:
                    console.print("[cyan]🔗 Setting up proxy chain...[/cyan]")
                    from src.utils.network import validate_proxy_chain, create_proxy_chain
                    if len(proxies) >= 2:
                        console.print(f"[green]✅ Proxy chain ready with {len(proxies)} proxies[/green]")
                        proxies = create_proxy_chain(proxies, CONFIG['PROXY_CHAIN_MAX_LENGTH'])
                    else:
                        console.print("[red]❌ Not enough valid proxies for chaining[/red]")
                        use_proxy_chain = False

        return {
            "target": target,
            "port": port,
            "threads": threads,
            "duration": duration,
            "max_requests": max_requests,
            "proxies": proxies,
            "use_tor": use_tor,
            "stealth_mode": stealth_mode,
            "use_vpn": use_vpn,
            "use_proxy_chain": use_proxy_chain
        }

    @staticmethod
    def display_attack_start(choice, params):
        """Display attack start information with real-time monitoring"""
        global current_monitor

        # Special UI for C2 Shell (ID 00)
        if choice == "00":
            if ModernCLI.c2_server and ModernCLI.c2_server.running:
                console.clear()
                console.print(Panel(
                    "[bold yellow][SAT] IP-HUNTER INTERACTIVE BOTNET SHELL[/bold yellow]\n\n"
                    "[white]Commands:[/white]\n"
                    "• [cyan]list[/cyan]             - Show all connected bots\n"
                    "• [cyan]ping[/cyan]             - Ping all bots\n"
                    "• [cyan]attack[/cyan] <t> <p> <d> <m> - Flood command\n"
                    "• [cyan]exit[/cyan]             - Return to menu",
                    title="C2 CENTER", border_style="yellow"
                ))
                
                while True:
                    cmd = Prompt.ask(f"[bold red]C2[/bold red] ([white]{len(ModernCLI.c2_server.bots)} bots[/white])").strip()
                    if not cmd: continue
                    if cmd.lower() in ["exit", "quit", "menu"]:
                        break
                    
                    if cmd.lower() == "list":
                        if not ModernCLI.c2_server.bots:
                            console.print("[dim]📭 No bots connected[/dim]")
                        else:
                            table = Table(title="Connected Bots", box=None)
                            table.add_column("ID", style="cyan")
                            for bid in ModernCLI.c2_server.bots.keys():
                                table.add_row(bid)
                            console.print(table)
                        continue
                    
                    if cmd.lower() == "help":
                        console.print("[cyan]Commands:[/cyan] list, ping, attack <target> <port> <duration> <method>, info, exit")
                        continue
                    
                    if ModernCLI.c2_server:
                        ModernCLI.c2_server.broadcast(cmd)
                        console.print(f"[green]📡 Broadcasted:[/green] {cmd}")
                        time.sleep(0.5)
                
                console.clear()
                return
            else:
                console.print("[bold red]❌ C2 Server is not running! Start it with ID 7 first.[/bold red]")
                time.sleep(2)
                return

        attack_info = Menu.ATTACKS.get(choice)
        if not attack_info:
            return

        if str(choice) == "7":
            ModernCLI.c2_server = AttackDispatcher.execute(choice, params)
            console.print("[bold green]✅ C2 Server started in background.[/bold green]")
            time.sleep(1)
            return

        if str(choice) == "18":
            ModernCLI.active_bot = AttackDispatcher.execute(choice, params)
            console.print("[bold green]✅ Bot instance started in background.[/bold green]")
            time.sleep(1)
            return

        # Advanced Attack Deployment UI
        os.system('cls' if os.name == 'nt' else 'clear')
        # Title Header with Cyberpunk brackets
        header_text = Text.from_markup(f"[bold green]≺[/] [bold bright_white]MISSION_PROTOCOL:[/][bold green] {attack_info['name'].upper()} [/][bold green]≻[/]")
        console.print(Align.center(header_text))
        console.print(Align.center(Text("-" * 80, style="dim white")))

        # 3-Panel Briefing Layout
        briefing_table = Table.grid(expand=True, padding=1)
        briefing_table.add_column(ratio=1) # Left: Intel
        briefing_table.add_column(ratio=1) # Mid: Specs
        briefing_table.add_column(ratio=1) # Right: OpSec

        # --- INTEL PANEL ---
        intel = Table.grid(padding=(0, 1))
        intel.add_row("[bold cyan]TARGET_ADR[/]", f"[white]{params['target']}[/]")
        if choice != "19" and "port" in params:
            intel.add_row("[bold cyan]TARGET_PRT[/]", f"[white]{params['port']}[/]")
        intel.add_row("[bold cyan]STRAT_CAT[/]", f"[dim white]{attack_info.get('category', 'L7/L4 Mixed')}[/]")
        intel.add_row("[bold cyan]LOCK_STAT[/]", "[bold green]TARGET_ACQUIRED[/]")
        
        # --- SPECS PANEL ---
        specs = Table.grid(padding=(0, 1))
        specs.add_row("[bold yellow]ENG_THRDS[/]", f"[white]{params['threads']}[/]")
        if "duration" in params and params["duration"] > 0:
            specs.add_row("[bold yellow]BURST_DUR[/]", f"[white]{params['duration']} sec[/]")
        if params.get("max_requests", 0) > 0:
            specs.add_row("[bold yellow]LIMIT_CAP[/]", f"[white]{params['max_requests']} reqs[/]")
        specs.add_row("[bold yellow]ORBIT_L00P[/]", "[bold green]STABILIZED[/]")

        # --- OPSEC PANEL ---
        def get_status(val): return "[bold green]ACTIVE[/]" if val else "[dim red]BYPASS[/]"
        
        opsec = Table.grid(padding=(0, 1))
        opsec.add_row("[bold green]TOR_PROXY[/]", get_status(params.get("use_tor")))
        opsec.add_row("[bold green]SLTH_MODE[/]", get_status(params.get("stealth_mode")))
        opsec.add_row("[bold green]VPN_CRYPT[/]", get_status(params.get("use_vpn")))
        if params.get("proxies"):
            opsec.add_row("[bold green]PRX_POOL [/]", f"[bold green]{len(params['proxies'])} NODES[/]")

        briefing_table.add_row(
            Panel(intel, title="[bold cyan]📡 TARGET_INTEL[/]", border_style="cyan", box=HEAVY_EDGE),
            Panel(specs, title="[bold yellow]🚀 PAYLOAD_SPECS[/]", border_style="yellow", box=HEAVY_EDGE),
            Panel(opsec, title="[bold green]🛡️ OPSEC_LAYERS[/]", border_style="green", box=HEAVY_EDGE)
        )

        console.print(briefing_table)
        console.print()

        if str(choice) in ["17", "20", "21", "23", "24", "25", "31", "32"]:
            AttackDispatcher.execute(choice, params)
            return

        if str(choice) == "22":
            AttackDispatcher.execute(choice, params)
            return

        current_monitor = AttackMonitor(
            attack_info["name"], 
            params["target"], 
            params["duration"],
            params.get("max_requests", 0)
        )
        current_monitor.start_monitoring()

        from src.utils.ui import create_cyber_progress
        with create_cyber_progress("[bold cyan][SAT] CALIBRATING ATTACK VECTORS...[/bold cyan]") as progress:
            task = progress.add_task("Calibrating", total=100)
            
            # Simulated heavy lifting with more "active" feedback
            steps = [
                ("Allocating thread pools...", 25),
                ("Establishing bypass tunnels...", 25),
                ("Finalizing synchronization...", 25),
                ("Optimizing throughput...", 25)
            ]
            
            for msg, adv in steps:
                progress.console.print(f"[dim white]  > {msg}[/]")
                progress.update(task, advance=adv)
                # Faster transition for smoother feel
                time.sleep(random.uniform(0.1, 0.25))

        console.print("[bold bright_green]🚀 ATTACK SEQUENCE INITIALIZED![/bold bright_green]")

        console.print("[bold yellow]💡 Press Ctrl+C to stop the attack[/bold yellow]")
        console.print("[bold cyan]📊 Real-time monitoring active...[/bold cyan]")
        console.print()

        attack_thread = threading.Thread(
            target=AttackDispatcher.execute,
            args=(choice, params, current_monitor),
            daemon=True
        )
        attack_thread.start()

        try:
            # Live monitoring loop - Locked to 4 FPS with manual refresh control for zero flicker
            # transient=False is ESSENTIAL for Windows Console stability to prevent "blanking"
            with Live(current_monitor.layout, auto_refresh=False, transient=False) as live:
                start_time = time.time()
                while time.time() - start_time < params["duration"]:
                    # Global stop check
                    if stop_event.is_set():
                        break
                        
                    with current_monitor._lock:
                        sent = current_monitor.packets_sent
                    
                    if params.get("max_requests", 0) > 0 and sent >= params["max_requests"]:
                        break

                    # Update statistics data
                    current_monitor.get_stats_panel()
                    # Perform single draw call
                    live.refresh()
                    
                    # Consistent 250ms interval (4 FPS)
                    time.sleep(0.25)
        except KeyboardInterrupt:

            console.print("\n[bold yellow]⚠️  Attack interrupted by user[/bold yellow]")
        finally:
            if current_monitor:
                current_monitor.stop_monitoring()
                current_monitor = None

    @staticmethod
    def display_attack_complete(choice):
        """Display completion message based on tool type"""
        is_attack = str(choice) in ["1", "2", "3", "4", "5", "6", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
        msg = "[bold green]✅ Attack completed successfully![/bold green]" if is_attack else "[bold green]✅ Task completed successfully![/bold green]"
        panel = Panel(
            f"{msg}\n"
            "[dim]Service monitoring session finished[/dim]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
        console.print()

    @staticmethod
    def display_error(error_msg):
        """Display error message"""
        panel = Panel(
            f"[bold red]❌ Error: {error_msg}[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        console.print(panel)
        console.print()

    @staticmethod
    def display_goodbye():
        """Display goodbye message (Matrix themed if enabled)"""
        if CONFIG.get('UI_THEME') == 'matrix':
            # Small Matrix exit effect
            console.print(Panel(Text("[bold green]Shutting down...[/bold green]"), border_style="bright_green"))
            time.sleep(0.15)
            matrix_header(typewriter=False)
            console.print(Panel(
                "[bold green]👋 Thank you for using IP-HUNTER (Matrix Mode)![/bold green]\n"
                "[dim green]Remember: This tool is for educational purposes only[/dim green]",
                border_style="bright_green",
                padding=(1, 2)
            ))
            return

        panel = Panel(
            "[bold cyan]👋 Thank you for using IP-HUNTER![/bold cyan]\n"
            "[dim]Remember: This tool is for educational purposes only[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(panel)

    @staticmethod
    def startup_sequence():
        """Animated startup sequence for IP-HUNTER"""
        threading.Thread(target=send_telemetry, args=({},), daemon=True).start()
        console.clear()
        
        # Startup animation - Matrix style if enabled
        if CONFIG.get('UI_THEME') == 'matrix':
            # Typewriter-style matrix header
            matrix_header(typewriter=True, speed=0.003)
            # Matrix loader with checks and animated stream
            matrix_loader(duration=2.8, fps=18)
            # Clear before rendering banner to prevent overlap
            console.clear()
            # Briefly show the full banner in green
            console.print(Align.center(Text(BANNER, style="bold green")))
            console.print("\n")
        else:
            # ASCII Animation (Cyberpunk Style)
            lines = BANNER.split('\n')
            with Live(Align.center(""), refresh_per_second=20, transient=True) as live:
                for i in range(len(lines)):
                    current = "\n".join(lines[:i+1])
                    live.update(Align.center(Text(current, style="bold cyan")))
                    time.sleep(0.02)
                
                # Flickering "Glitch" Effect
                for _ in range(2):
                    live.update(Align.center(Text(BANNER, style="bold white")))
                    time.sleep(0.04)
                    live.update(Align.center(Text(BANNER, style="bold cyan")))
                    time.sleep(0.04)
            
            console.print(Align.center(Text(BANNER, style="bold cyan")))
            console.print("\n")
        
        boot_steps = [
            "KERNEL_CORE: SYSCALL_INIT",
            "SESS_AUTH: AUTHENTICATING_USER",
            "SECURE_LAYER: BYPASSING_SANDBOX",
            "NET_TUNNEL: ESTABLISHING_NODES",
            "MODULE_PATCH: MEM_INJECTION",
            "INTEL_RECON: DATA_SYNC"
        ]
        
        for step in boot_steps:
            console.print(f"[green][[  [bold]..[/bold]  ]][/green] {step}...", end="\r")
            time.sleep(random.uniform(0.05, 0.12))
            console.print(f"[green][[  [bold]OK[/bold]  ]][/green] {step}")
        
        time.sleep(0.3)
        console.clear()


        if CONFIG.get('TOR_AUTO_START'):
            console.print(f"[yellow][[ WAIT ]][/yellow] INITIATING TOR GATEWAY...", end="\r")
            tor_success, _ = auto_start_tor_if_needed(CONFIG['TOR_PORT'])
            if tor_success:
                console.print(f"[green][[  OK  ]][/green] TOR GATEWAY ACTIVE")
            else:
                console.print(f"[red][[ FAIL ]][/red] TOR GATEWAY FAILED")
                time.sleep(0.5)

        if CONFIG.get('VPN_ENABLED') or CONFIG.get('FORCE_AUTO_PROTECT'):
            console.print(f"[yellow][[ WAIT ]][/yellow] SECURING VPN TUNNEL...", end="\r")
            auto_connect_vpn()
            console.print(f"[green][[  OK  ]][/green] VPN TUNNEL READY")
            
        console.print(f"[green][[ DONE ]][/green] ACCESS GRANTED")
        time.sleep(0.4)
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def _run_ai_recon(target: str):
        """Perform AI profiling and get suggestions"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            transient=True
        ) as progress:
            task = progress.add_task("[bold cyan]AI ORCHESTRATOR: ANALYZING TARGET...", total=100)
            
            # Phase 1: Recon
            progress.update(task, advance=20, description="[bold cyan]AI: IDENTIFYING SERVICES...")
            profile = ModernCLI.ai_orch.analyze_target(target)
            
            # Phase 2: Vulnerability Mapping
            progress.update(task, advance=40, description="[bold cyan]AI: MAPPING VULNERABILITIES...")
            suggestions = ModernCLI.ai_orch.suggest_attack_strategy(profile)
            
            # Phase 3: Optimization
            progress.update(task, advance=40, description="[bold cyan]AI: OPTIMIZING STRATEGY...")
            time.sleep(0.5)
            
            return suggestions

    @staticmethod
    def _display_ai_suggestions(suggestions):
        """Display suggestions and let user select one"""
        console.clear()
        console.print(Align.center(Text("🤖 AI ORCHESTRATOR RECOMMENDATIONS", style="bold cyan")))
        
        table = Table(box=HEAVY_EDGE, expand=True)
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Attack Vector", style="white")
        table.add_column("Rank", justify="center")
        table.add_column("Confidence", justify="right")
        table.add_column("Strategy Reason", style="dim white")
        
        for idx, s in enumerate(suggestions, 1):
            conf_color = "green" if s.confidence > 0.8 else "yellow" if s.confidence > 0.5 else "red"
            rank = "⭐" * (6 - s.priority)
            table.add_row(
                str(idx), 
                s.attack_name, 
                rank, 
                f"[{conf_color}]{s.confidence*100:.1f}%[/]", 
                s.reason
            )
        
        console.print(table)
        console.print(Panel(
            "[bold white]Enter ID to Apply AI Strategy [/bold white] | [bold white]Enter '0' to Skip[/bold white]",
            border_style="cyan"
        ))
        
        sel = IntPrompt.ask("[bold cyan]AI SELECT[/bold cyan]", default=0)
        if 0 < sel <= len(suggestions):
            return suggestions[sel-1]
        return None

    @staticmethod
    def run():
        """Main CLI loop with optimized rendering and interaction"""
        security.drm_check()
        ModernCLI.startup_sequence()
        # Use direct clear for better Windows terminal compatibility
        console.clear()

        while True:
            console.print(ModernCLI.display_menu())
            console.print(Panel(
                Align.center("[bold white]Select an ID to proceed[/bold white] [dim]• Type 'q' to exit • Just hit Enter to refresh[/dim]"),
                title="[bold green] CMD [/bold green]",
                border_style="green",
                padding=(0, 1)
            ))
            
            try:
                choice = Prompt.ask("[bold green]root@ip-hunter[/bold green]:[bold green]~[/bold green]#").strip().lower()

                if choice in ['q', 'quit', 'exit']:
                    ModernCLI.display_goodbye()
                    break

                if not choice:
                    console.clear()
                    continue

                # Display attack configuration page
                attack_info = Menu.ATTACKS.get(choice, {})
                if attack_info:
                    console.clear()
                    console.print(create_attack_config_panel(choice, attack_info))
                    proceed = Confirm.ask("[bold green]Proceed with this attack configuration?[/bold green]", default=True)
                    if not proceed:
                        console.clear()
                        continue

                params = ModernCLI.get_attack_params(choice)
                if params is not None:
                    ModernCLI.display_attack_start(choice, params)
                    if str(choice) not in ["7", "18"]:
                        ModernCLI.display_attack_complete(choice)
                        console.print("[bold blue]Press Enter to return to dashboard...[/bold blue]")
                        input()
                console.clear()
            except KeyboardInterrupt:
                console.print("\n[bold yellow]⚠️  Action interrupted by user[/bold yellow]")
                time.sleep(1)
                console.clear()
            except Exception as e:
                ModernCLI.display_error(str(e))
                time.sleep(2)
                console.clear()

