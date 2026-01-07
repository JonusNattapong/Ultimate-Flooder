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
from rich.prompt import Prompt, IntPrompt
from rich.columns import Columns
from rich.align import Align
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.style import Style
from rich.layout import Layout
from rich.padding import Padding

from src.config import BANNER, CONFIG, update_config_key
from src.core.menu import Menu
from src.core.dispatcher import AttackDispatcher
from src import security
from src.utils import (
    load_file_lines, auto_start_tor_if_needed, 
    generate_stealth_headers, check_vpn_running, 
    add_system_log, SYSTEM_LOGS, stealth_mode_init
)
from src.utils.ui import CyberSpinnerColumn
from src.utils.network import get_vpn_ip
from src.utils.system import cleanup_temp_files

# Initialize Rich Console
console = Console()

class AttackMonitor:
    """Real-time attack monitoring system"""

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
        """Update attack statistics"""
        self.packets_sent += packets
        self.bytes_sent += bytes_sent
        self.active_connections = connections
        self.packets_failed += failed

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            time.sleep(1)  # Update every second

    def get_stats_panel(self):
        """Generate the statistics panel"""
        elapsed = time.time() - self.start_time
        
        if self.max_requests > 0:
            progress_percent = min(100, (self.packets_sent / self.max_requests) * 100)
            time_info = f"{self.packets_sent:,}/{self.max_requests:,} reqs"
        else:
            progress_percent = min(100, (elapsed / self.duration) * 100)
            time_info = f"{max(0, self.duration - int(elapsed))}s left"

        # System stats
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
        except:
            cpu_percent = 0
            memory_percent = 0
            memory_used = 0
            memory_total = 0

        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="stats", size=8),
            Layout(name="system", size=6),
            Layout(name="progress", size=4)
        )

        # Header
        header_panel = Panel(
            f"[bold cyan]🎯 {self.attack_name}[/bold cyan]\n"
            f"[bold white]Target:[/bold white] {self.target}\n"
            f"[bold white]Duration:[/bold white] {self.duration}s",
            border_style="cyan",
            padding=(0, 1)
        )
        layout["header"].update(header_panel)

        # Attack Statistics
        stats_table = Table(show_header=True, header_style="bold magenta", show_edge=False)
        stats_table.add_column("Metric", style="cyan", width=15)
        stats_table.add_column("Value", style="white", width=15)
        stats_table.add_column("Rate/sec", style="green", width=10)

        packets_per_sec = self.packets_sent / max(1, elapsed)
        bytes_per_sec = self.bytes_sent / max(1, elapsed)
        success_rate = (self.packets_sent / max(1, self.packets_sent + self.packets_failed)) * 100

        stats_table.add_row("Packets Sent", f"{self.packets_sent:,}", f"{packets_per_sec:.0f}")
        stats_table.add_row("Bytes Sent", f"{self.bytes_sent:,}", f"{bytes_per_sec:.0f}")
        stats_table.add_row("Active Threads", str(security.active_threads), "")
        stats_table.add_row("Active Sockets", str(security.active_sockets), "")
        stats_table.add_row("Success Rate", f"{success_rate:.1f}%", "")

        layout["stats"].update(Panel(stats_table, title="[bold magenta]📊 Attack Statistics[/bold magenta]", border_style="magenta", padding=(0, 1)))

        # System Resources
        system_table = Table(show_header=True, header_style="bold yellow", show_edge=False)
        system_table.add_column("Resource", style="cyan", width=12)
        system_table.add_column("Usage", style="white", width=15)
        system_table.add_column("Status", style="green", width=10)

        cpu_status = "🟢" if cpu_percent < 80 else "🔴"
        mem_status = "🟢" if memory_percent < 80 else "🔴"

        system_table.add_row("CPU", f"{cpu_percent:.1f}%", cpu_status)
        system_table.add_row("Memory", f"{memory_used:.1f}/{memory_total:.1f}GB", mem_status)
        system_table.add_row("Network", "Active", "🟢")

        layout["system"].update(Panel(system_table, title="[bold yellow]🖥️  System Resources[/bold yellow]", border_style="yellow", padding=(0, 1)))

        # Progress Bar
        progress_bar = Progress(
            CyberSpinnerColumn(),
            TextColumn("[bold blue]Progress:[/bold blue]"),
            BarColumn(bar_width=30, complete_style="green", finished_style="bold green"),
            TaskProgressColumn(),
            TextColumn(f"[bold white]{time_info}[/bold white]"),
        )

        task = progress_bar.add_task(
            "Attack Progress",
            total=100,
            completed=progress_percent
        )

        layout["progress"].update(Panel(progress_bar, title="[bold blue]⏳ Attack Progress[/bold blue]", border_style="blue", padding=(0, 1)))

        return layout

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

    @staticmethod
    def manage_targets():
        """Target Library Management Sub-menu"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print(Align.center(Text(BANNER, style="bold cyan")))
            
            table = Table(title="💎 [bold magenta]Target Library (Locked Targets)[/bold magenta]", border_style="bright_blue", expand=True)
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
                title="[bold yellow] Target Management Options [/bold yellow]",
                border_style="yellow"
            ))

            op = Prompt.ask("[bold cyan]Select Action[/bold cyan]", choices=["a", "d", "c", "b"], default="b").lower()
            
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
        """Display the top header panel"""
        subtitle = Panel(
            "[bold yellow]Advanced DDoS Tool v2.1.0 - Coded for Educational Purposes Only[/bold yellow]",
            border_style="blue",
            padding=(0, 1)
        )
        console.print(subtitle)
        console.print()

    @staticmethod
    def display_menu():
        """Returns the menu and dashboard layout content"""
        # Menu Table
        table = Table(
            show_header=True,
            header_style="bold blue",
            border_style="blue",
            expand=True
        )
        table.add_column("ID", style="cyan", justify="center", width=4)
        table.add_column("Attack Type", style="white")
        table.add_column("Layer", style="green", justify="center", width=6)
        table.add_column("Root Needed", style="red", justify="center", width=12)

        layer_mapping = {
            "1": "7", "2": "7", "3": "4", "4": "4", "5": "7", "6": "4",
            "7": "C2", "8": "7", "9": "4", "10": "4", "11": "4", "12": "7",
            "13": "7", "14": "7", "15": "7", "16": "7", "17": "Scan", "18": "Bot",
            "19": "CMD", "20": "Net", "21": "OSINT", "22": "AI", "23": "Scout",
            "24": "Cracker", "25": "OSINT", "26": "Proxy", "27": "WiFi",
            "28": "Sniff", "29": "Exploit", "30": "OpSec", "31": "Vuln", "32": "Sniper",
            "33": "L7", "34": "L7", "35": "L4"
        }

        # Dynamically add ID 00 if C2 is running (changed from 19 to avoid conflict)
        attacks = Menu.ATTACKS.copy()
        if ModernCLI.c2_server and ModernCLI.c2_server.running:
            attacks["00"] = {"name": "Enter C2 Interactive Shell", "needs_root": False}

        for key, attack in attacks.items():
            layer = layer_mapping.get(key, "?")
            root_needed = "✓" if attack["needs_root"] else "✗"
            root_style = "red" if attack["needs_root"] else "green"

            table.add_row(
                f"[bold]{key}[/bold]",
                attack["name"],
                f"[bold cyan]{layer}[/bold cyan]",
                f"[{root_style}]{root_needed}[/{root_style}]"
            )

        # 3. Live Logs / Events Dashboard
        if not SYSTEM_LOGS:
            log_content = "[dim]Waiting for network events...[/dim]"
        else:
            # logs are already chronological in SYSTEM_LOGS
            log_content = "\n".join(SYSTEM_LOGS[-12:])

        # 4. Services Status Logic
        services_table = Table(box=None, expand=True)
        services_table.add_column("Service", style="cyan")
        services_table.add_column("Status", style="bold")
        
        c2_status = f"[green]ONLINE (Port {ModernCLI.c2_server.port})[/green]" if ModernCLI.c2_server and ModernCLI.c2_server.running else "[red]OFFLINE[/red]"
        
        if ModernCLI.active_bot:
            if ModernCLI.active_bot.connected:
                bot_status = "[green]RUNNING (Connected)[/green]"
            else:
                bot_status = "[yellow]RETRYING (Auto-Reconnect...)[/yellow]"
        else:
            bot_status = "[red]STOPPED[/red]"
        
        services_table.add_row("C2 Center", c2_status)
        services_table.add_row("Local Bot", bot_status)
        if ModernCLI.c2_server:
            services_table.add_row("Bots Count", f"[white]{len(ModernCLI.c2_server.bots)}[/white]")
        
        # Locked Targets Status
        target_count = len(ModernCLI.locked_targets)
        target_color = "green" if target_count > 0 else "red"
        services_table.add_row("Locked Targets", f"[{target_color}]{target_count}[/{target_color}]")
        
        # --- NEW LAYOUT REARRANGEMENT ---
        
        # Create a single column layout for everything
        layout_content = Table.grid(expand=True)
        layout_content.add_column()

        # 1. Top: ASCII Banner
        layout_content.add_row(Align.center(Text(BANNER, style="bold cyan")))
        layout_content.add_row("")

        # 2. Middle: Menu Table
        layout_content.add_row(table)
        layout_content.add_row("")

        # 3. Bottom: Services and Logs side-by-side to save space
        bottom_grid = Table.grid(expand=True, padding=1)
        bottom_grid.add_column(ratio=1) # Services
        bottom_grid.add_column(ratio=2) # Logs
        
        bottom_grid.add_row(
            Panel(services_table, title="[bold blue]🛰️  Active Services[/bold blue]", border_style="blue"),
            Panel(log_content, title="[bold yellow]🕒 System Logs[/bold yellow]", border_style="yellow", height=10)
        )
        
        layout_content.add_row(bottom_grid)

        return Panel(layout_content, title="[bold magenta] IP-HUNTER v2.1.0 Dashboard [/bold magenta]", border_style="bright_blue")

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
            panel = Panel("[bold cyan]Network Recon / Discovery[/bold cyan]\n[dim]Scans the local network for active devices and services.[/dim]", border_style="cyan")
            console.print(panel)
            subnet = Prompt.ask("[bold yellow]Enter Subnet to Scan (e.g. 192.168.1.0/24 or 10.0.0.0/16)[/bold yellow]", default="auto")
            subnet = None if subnet == "auto" else subnet
            threads = IntPrompt.ask("[bold yellow]Parallel Scan Threads[/bold yellow]", default=250)
            return {"threads": threads, "subnet": subnet, "target": "local", "port": 0, "duration": 0, "proxies": []}

        if choice == "21":  # IP Tracker
            ip = Prompt.ask("[bold cyan]Enter IP Address to Track (Leave empty for yours)[/bold cyan]").strip()
            return {
                "ip": ip if ip else None, 
                "target": ip if ip else "Current IP", 
                "duration": 0, 
                "threads": 1, 
                "port": 0,
                "proxies": []
            }

        if choice == "22": # AI-Adaptive Smart Flood
            panel = Panel("[bold cyan]AI-Adaptive Smart Flood[/bold cyan]\n[dim]Autonomous intensity adjustment based on server feedback.[/dim]", border_style="cyan")
            console.print(panel)
            target = Prompt.ask("[bold yellow]Target URL[/bold yellow]").strip()
            threads = IntPrompt.ask("[bold yellow]Threads[/bold yellow]", default=50)
            duration = IntPrompt.ask("[bold yellow]Duration[/bold yellow]", default=60)
            return {"target": target, "threads": threads, "duration": duration, "proxies": [], "port": 80}

        if choice == "23": # Vulnerability Scout
            panel = Panel("[bold cyan]Vulnerability Scout[/bold cyan]\n[dim]Rapid scan for sensitive files and misconfigurations.[/dim]", border_style="cyan")
            console.print(panel)
            target = Prompt.ask("[bold yellow]Target URL[/bold yellow]").strip()
            return {"target": target, "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "24": # Brute-Force Suite
            panel = Panel("[bold cyan]Brute-Force Suite[/bold cyan]\n[dim]Trial matching common credentials for services.[/dim]", border_style="cyan")
            console.print(panel)
            target = Prompt.ask("[bold yellow]Target Host/IP[/bold yellow]").strip()
            service = Prompt.ask("[bold yellow]Service (FTP/HTTP)[/bold yellow]", default="FTP").strip()
            username = Prompt.ask("[bold yellow]Username[/bold yellow]", default="admin").strip()
            return {"target": target, "service": service, "username": username, "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "25": # Domain OSINT
            panel = Panel("[bold cyan]Domain OSINT Multi-Hunter[/bold cyan]\n[dim]Hunt subdomains and DNS intelligence.[/dim]", border_style="cyan")
            console.print(panel)
            target = Prompt.ask("[bold yellow]Domain (e.g. google.com)[/bold yellow]").strip()
            return {"target": target, "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "26": # Proxy Autopilot
            panel = Panel("[bold cyan]Proxy Autopilot[/bold cyan]\n[dim]Auto-scrapes and validates fresh HTTP/SOCKS proxies.[/dim]", border_style="cyan")
            console.print(panel)
            return {"target": "localhost", "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "27": # WiFi Ghost
            panel = Panel("[bold cyan]WiFi Ghost Recon[/bold cyan]\n[dim]Passive scanning of surrounding airwaves (Requires Admin).[/dim]", border_style="cyan")
            console.print(panel)
            return {"target": "local", "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "28": # Packet Insight
            panel = Panel("[bold cyan]Packet Insight (Sniffer)[/bold cyan]\n[dim]Live deep packet inspection of local traffic.[/dim]", border_style="cyan")
            console.print(panel)
            duration = IntPrompt.ask("[bold yellow]Sniff Duration (seconds)[/bold yellow]", default=10)
            return {"target": "sniffer", "duration": duration, "threads": 1, "port": 0, "proxies": []}

        if choice == "29": # Payload Lab
            panel = Panel("[bold cyan]Payload Lab[/bold cyan]\n[dim]Generate obfuscated payloads for authorized testing.[/dim]", border_style="cyan")
            console.print(panel)
            return {"target": "payload", "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "30": # Identity Cloak
            panel = Panel("[bold cyan]Identity Cloak (OpSec)[/bold cyan]\n[dim]Randomizes MAC address and machine hostname.[/dim]", border_style="cyan")
            console.print(panel)
            return {"target": "privacy", "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "31": # CVE Explorer
            panel = Panel("[bold cyan]CVE Explorer[/bold cyan]\n[dim]Search public vulnerability databases (NVD/CIRCL) by keyword.[/dim]", border_style="cyan")
            console.print(panel)
            keyword = Prompt.ask("[bold yellow]Search Keyword (e.g. windows, apache, cisco)[/bold yellow]").strip()
            return {"target": "CVE-Database", "keyword": keyword, "duration": 0, "threads": 1, "port": 0, "proxies": []}

        if choice == "32": # Web Exposure Sniper
            panel = Panel("[bold red]Web Exposure Sniper[/bold red]\n[dim]Active hunting for data leaks, sensitive files, and misconfigurations on a target website.[/dim]", border_style="red")
            console.print(panel)
            
            # AI Key Management
            api_key = CONFIG.get('OPENROUTER_API_KEY')
            if not api_key:
                console.print("[yellow]⚠️  OpenRouter API Key not found.[/yellow]")
                api_key = Prompt.ask("[bold cyan]Enter OpenRouter API Key (to enable AI recon)[/bold cyan]").strip()
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
                "[bold cyan]Botnet C2 Server Configuration[/bold cyan]",
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
            f"[bold cyan]{attack_info['name']}[/bold cyan]\n"
            f"[dim]{description}[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(panel)

        # Target input
        if ModernCLI.locked_targets:
            console.print(Panel(
                f"[bold cyan]🎯 Target Locked Selection[/bold cyan]\n"
                f"You have [bold yellow]{len(ModernCLI.locked_targets)}[/bold yellow] targets in your library.",
                border_style="cyan"
            ))
            for i, t in enumerate(ModernCLI.locked_targets, 1):
                console.print(f"  [bold cyan][{i}][/bold cyan] {t}")
            
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
        stealth_mode = False # Initialize to fix NameError
        use_vpn = False
        use_proxy_chain = False

        if is_l7:
            max_requests = IntPrompt.ask("[bold yellow]Total Requests (0 for unlimited)[/bold yellow]", default=0)
            proxy_file = Prompt.ask(f"[bold yellow]Proxy file[/bold yellow] [dim]({CONFIG['PROXY_FILE']})[/dim]", default="").strip()
            if proxy_file:
                if os.path.isfile(proxy_file):
                    proxies = load_file_lines(proxy_file)
                    console.print(f"[green]✅ Loaded {len(proxies)} proxies[/green]")
            
            use_tor = Prompt.ask("[bold yellow]Use Tor for anonymity? (y/n)[/bold yellow]", default="n").strip().lower() == 'y'
            if use_tor:
                console.print("[cyan]🔄 Checking Tor status...[/cyan]")
                tor_success, tor_message = auto_start_tor_if_needed(CONFIG['TOR_PORT'])
                if tor_success:
                    console.print(f"[green]✅ {tor_message}[/green]")
                else:
                    console.print(f"[red]❌ {tor_message}[/red]")
                    console.print("[yellow]⚠️  Continuing without Tor...[/yellow]")
                    use_tor = False
            
            stealth_mode = Prompt.ask("[bold yellow]Enable stealth mode (advanced anti-trace)? (y/n)[/bold yellow]", default="n").strip().lower() == 'y'
            if stealth_mode:
                console.print("[cyan]🛡️  Initializing stealth mode...[/cyan]")
                cleanup_success, cleanup_msg = stealth_mode_init()
                if cleanup_success:
                    console.print(f"[green]✅ {cleanup_msg}[/green]")
                else:
                    console.print(f"[red]❌ {cleanup_msg}[/red]")
                console.print("[green]✅ Stealth mode activated[/green]")
            
            # VPN Integration
            use_vpn = Prompt.ask("[bold yellow]Use VPN for additional protection? (y/n)[/bold yellow]", default="n").strip().lower() == 'y'
            if use_vpn:
                console.print("[cyan]🔍 Checking VPN status...[/cyan]")
                vpn_running, vpn_message = check_vpn_running()
                if vpn_running:
                    console.print(f"[green]✅ {vpn_message}[/green]")
                    # Get VPN IP for verification
                    vpn_ip = get_vpn_ip()
                    if vpn_ip:
                        console.print(f"[blue]📍 VPN IP: {vpn_ip}[/blue]")
                else:
                    console.print(f"[red]❌ {vpn_message}[/red]")
                    console.print("[yellow]⚠️  Please connect to VPN manually before running attacks[/yellow]")
                    console.print("[yellow]💡  Supported VPNs: NordVPN, ExpressVPN, ProtonVPN[/yellow]")
                    use_vpn = False
            
            # Proxy Chain Configuration
            use_proxy_chain = False
            if proxies:
                use_proxy_chain = Prompt.ask("[bold yellow]Enable proxy chain rotation? (y/n)[/bold yellow]", default="n").strip().lower() == 'y'
                if use_proxy_chain:
                    console.print("[cyan]🔗 Setting up proxy chain...[/cyan]")
                    from src.utils.network import validate_proxy_chain, create_proxy_chain
                    # Validate and setup proxy chain
                    valid_proxies = validate_proxy_chain(proxies)
                    if len(valid_proxies) >= 2:
                        console.print(f"[green]✅ Proxy chain ready with {len(valid_proxies)} proxies[/green]")
                        proxies = create_proxy_chain(valid_proxies, CONFIG['PROXY_CHAIN_MAX_LENGTH'])
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
                    "[bold yellow]🛰️  IP-HUNTER INTERACTIVE BOTNET SHELL[/bold yellow]\n\n"
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
                    
                    # Send command through the running server
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

        # Special UI for C2 Server
        if str(choice) == "7":
            ModernCLI.c2_server = AttackDispatcher.execute(choice, params)
            console.print("[bold green]✅ C2 Server started in background.[/bold green]")
            time.sleep(1)
            return

        # Special UI for Bot Client
        if str(choice) == "18":
            ModernCLI.active_bot = AttackDispatcher.execute(choice, params)
            console.print("[bold green]✅ Bot instance started in background.[/bold green]")
            time.sleep(1)
            return

        # Attack summary table
        table = Table(title="[bold red]🚀 Attack Configuration[/bold red]", show_header=True, header_style="bold red")
        table.add_column("Parameter", style="cyan", width=12)
        table.add_column("Value", style="white", width=25)

        table.add_row("Attack Type", attack_info["name"])
        table.add_row("Target", params["target"])
        
        if choice == "17":
            table.add_row("Ports", params["port_text"])
        elif choice == "21":
            table.add_row("Task", "Deep OSINT Tracking")
        elif choice == "22":
            table.add_row("Mode", "AI-Adaptive (Smart)")
        elif choice == "23":
            table.add_row("Task", "Vulnerability Search")
        elif choice == "24":
            table.add_row("Service", f"{params['service']} Crack")
        elif choice == "25":
            table.add_row("Task", "Subdomain Hunting")
        elif choice == "19":
            table.add_row("Payload", "ICMP Hybrid Flood")
        else:
            table.add_row("Port", str(params["port"]))

        table.add_row("Threads", str(params["threads"]))

        if choice not in ["17", "20", "21", "23", "25", "31", "32"]:
            table.add_row("Duration", f"{params['duration']}s")
            table.add_row("Proxies", str(len(params["proxies"])))
            if params.get("use_tor"):
                table.add_row("Tor", "Enabled")
            if params.get("stealth_mode"):
                table.add_row("Stealth Mode", "Active")
            if params.get("use_vpn"):
                table.add_row("VPN", "Enabled")
            if params.get("use_proxy_chain"):
                table.add_row("Proxy Chain", "Active")

        console.print(table)
        console.print()

        # Custom UI tools (Synchronous execution)
        if str(choice) in ["17", "20", "21", "23", "24", "25", "31", "32"]:
            AttackDispatcher.execute(choice, params)
            return
                table.add_row("Tor", "Enabled")
            if params.get("stealth_mode"):
                table.add_row("Stealth Mode", "Active")
            if params.get("use_vpn"):
                table.add_row("VPN", "Enabled")
            if params.get("use_proxy_chain"):
                table.add_row("Proxy Chain", "Active")

        console.print(table)
        console.print()

        # Custom UI tools (Synchronous execution)
        if str(choice) in ["17", "20", "21", "23", "24", "25", "31", "32"]:
            AttackDispatcher.execute(choice, params)
            return

        # Special handling for AI-Adaptive (Synchronous due to internal monitoring)
        if str(choice) == "22":
            AttackDispatcher.execute(choice, params)
            return

        # Initialize monitor
        current_monitor = AttackMonitor(
            attack_info["name"], 
            params["target"], 
            params["duration"],
            params.get("max_requests", 0)
        )
        current_monitor.start_monitoring()

        # Start aesthetic attack animation sequence
        with create_cyber_progress("[bold cyan]🛰️  CALIBRATING ATTACK VECTORS...[/bold cyan]") as progress:
            task = progress.add_task("Calibrating", total=100)
            
            time.sleep(0.4)
            console.print("[dim white]  > Allocating thread pools...[/]")
            progress.update(task, advance=30)
            
            time.sleep(0.3)
            console.print("[dim white]  > Establishing bypass tunnels...[/]")
            progress.update(task, advance=30)
            
            time.sleep(0.4)
            console.print("[dim white]  > Finalizing synchronization...[/]")
            progress.update(task, advance=40)

        console.print("[bold bright_green]🚀 ATTACK SEQUENCE INITIALIZED![/bold bright_green]")
        console.print("[bold yellow]💡 Press Ctrl+C to stop the attack[/bold yellow]")
        console.print("[bold cyan]📊 Real-time monitoring active...[/bold cyan]")
        console.print()

        # Start attack in background
        attack_thread = threading.Thread(
            target=AttackDispatcher.execute,
            args=(choice, params, current_monitor),
            daemon=True
        )
        attack_thread.start()

        # Start real-time monitoring display
        try:
            with Live(current_monitor.get_stats_panel(), refresh_per_second=2, screen=True) as live:
                start_time = time.time()
                while time.time() - start_time < params["duration"]:
                    # Check if max requests reached
                    if params.get("max_requests", 0) > 0 and current_monitor.packets_sent >= params["max_requests"]:
                        break
                    
                    live.update(current_monitor.get_stats_panel())
                    time.sleep(0.5)

                    # Check for keyboard interrupt
                    try:
                        import select
                        import sys
                        if select.select([sys.stdin], [], [], 0.0)[0]:
                            if sys.stdin.read(1) == '\x03':  # Ctrl+C
                                raise KeyboardInterrupt
                    except:
                        pass

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
        """Display goodbye message"""
        panel = Panel(
            "[bold cyan]👋 Thank you for using IP-HUNTER![/bold cyan]\n"
            "[dim]Remember: This tool is for educational purposes only[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(panel)

    @staticmethod
    def startup_sequence():
        """Cool startup animation"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Show Banner during startup
        console.print(Align.center(Text(BANNER, style="bold cyan")))
        console.print("\n")
        
        with Progress(
            SpinnerColumn("aesthetic"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, complete_style="cyan", finished_style="bright_green"),
            transient=True
        ) as progress:
            task = progress.add_task("[bold cyan]INITIALIZING IP-HUNTER CORE...[/]", total=100)
            
            steps = [
                "AUTHENTICATING SECURITY TOKENS...",
                "BYPASSING SANDBOX ENVIRONMENTS...",
                "ESTABLISHING SECURE TUNNELS...",
                "PATCHING KERNEL MODULES...",
                "GATHERING INTELLIGENCE...",
                "ACCESS GRANTED"
            ]
            
            for step in steps:
                progress.update(task, description=f"[bold white]{step}[/]", advance=16.7)
                time.sleep(random.uniform(0.2, 0.5))
        
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def run():
        """Main CLI loop with live updates"""
        ModernCLI.startup_sequence()
        os.system('cls' if os.name == 'nt' else 'clear')

        while True:
            # Show the dashboard and menu
            console.print(ModernCLI.display_menu())
            
            # Instructions Panel with Command Center Style
            console.print(Panel(
                Align.center("[bold white]Select an ID to proceed[/bold white] [dim]• Type 'q' to exit • Just hit Enter to refresh[/dim]"),
                title="[bold green] ⚡ COMMAND CENTER [/bold green]",
                border_style="bright_green", 
                padding=(0, 1)
            ))
            
            # Stylish Boxed Input
            console.print("[bold bright_green]╭──╼[/bold bright_green] [bold white][Waiting for Input][/bold white]")
            choice = Prompt.ask("[bold bright_green]╰─> Choice[/bold bright_green]").strip().lower()

            if choice in ['q', 'quit', 'exit']:
                ModernCLI.display_goodbye()
                break

            if not choice:
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            try:
                params = ModernCLI.get_attack_params(choice)
                if params is not None:
                    ModernCLI.display_attack_start(choice, params)
                    
                    # Only show generic completion for tools that aren't persistent background services
                    # (ID 7, 18 are background persistent services)
                    if str(choice) not in ["7", "18"]:
                        ModernCLI.display_attack_complete(choice)
                        console.print("[bold blue]Press Enter to return to dashboard...[/bold blue]")
                        input()
                
                os.system('cls' if os.name == 'nt' else 'clear')

            except KeyboardInterrupt:
                console.print("\n[bold yellow]⚠️  Action interrupted by user[/bold yellow]")
                time.sleep(1)
                os.system('cls' if os.name == 'nt' else 'clear')
            except Exception as e:
                ModernCLI.display_error(str(e))
                time.sleep(2)
                os.system('cls' if os.name == 'nt' else 'clear')