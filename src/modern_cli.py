# Modern CLI Interface for IP-HUNTER
# อินเทอร์เฟซ CLI สมัยใหม่สำหรับ IP-HUNTER

import os
import time
import threading
import psutil
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

from .config import BANNER, CONFIG
from .classes import Menu, AttackDispatcher
from .security import check_system_resources, active_threads, active_sockets

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
        stats_table.add_row("Active Threads", str(active_threads), "")
        stats_table.add_row("Active Sockets", str(active_sockets), "")
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

    @staticmethod
    def display_banner():
        """Display the ASCII banner with colors"""
        banner_text = Text(BANNER, style="bold cyan")
        panel = Panel(
            Align.center(banner_text),
            title="[bold red]IP-HUNTER v2.0[/bold red]",
            title_align="center",
            border_style="red",
            padding=(1, 2)
        )
        console.print(panel)

        # Subtitle
        subtitle = Panel(
            "[bold yellow]Advanced DDoS Tool - Coded for Educational Purposes Only[/bold yellow]",
            border_style="yellow",
            padding=(0, 1)
        )
        console.print(subtitle)
        console.print()

    @staticmethod
    def display_menu():
        """Display the attack menu in a modern table format"""
        table = Table(title="[bold magenta] Attack Selection Menu[/bold magenta]", show_header=True, header_style="bold blue")
        table.add_column("ID", style="cyan", justify="center", width=4)
        table.add_column("Attack Type", style="white", width=35)
        table.add_column("Layer", style="green", justify="center", width=6)
        table.add_column("Root Required", style="red", justify="center", width=12)

        layer_mapping = {
            "1": "7", "2": "7", "3": "4", "4": "4", "5": "7", "6": "4",
            "7": "C2", "8": "7", "9": "4", "10": "4", "11": "4", "12": "7",
            "13": "7", "14": "7", "15": "7", "16": "7", "17": "Scan"
        }

        for key, attack in Menu.ATTACKS.items():
            layer = layer_mapping.get(key, "?")
            root_needed = "✓" if attack["needs_root"] else "✗"
            root_style = "red" if attack["needs_root"] else "green"

            table.add_row(
                f"[bold]{key}[/bold]",
                attack["name"],
                f"[bold cyan]{layer}[/bold cyan]",
                f"[{root_style}]{root_needed}[/{root_style}]"
            )

        console.print(table)
        console.print()

        # Instructions
        instructions = Panel(
            "[bold white]Choose an attack by entering the ID number[/bold white]\n"
            "[dim]Type 'q', 'quit', or 'exit' to quit the program[/dim]",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(instructions)

    @staticmethod
    def get_choice():
        """Get user choice with modern prompt"""
        try:
            choice = Prompt.ask("[bold green]Enter your choice[/bold green]").strip().lower()

            if choice in ['q', 'quit', 'exit']:
                ModernCLI.display_goodbye()
                return None

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
            
            return {
                "target": target,
                "ports": ports,
                "port_text": port_input, # for display
                "threads": threads,
                "duration": 0, # Not used
                "proxies": [] # Not used
            }

        # Standard attack parameters
        attack_info = Menu.ATTACKS.get(choice)
        if not attack_info:
            return None

        # Categorize attack
        is_l7 = choice in ["1", "2", "5", "8", "12", "13", "14", "15", "16"]
        is_l4 = choice in ["3", "4"]
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
            f"[dim]{description}[/dim]\n\n"
            f"[bold white]Target Example:[/bold white] [green]{example}[/green]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(panel)

        # Target input
        target_prompt = "[bold yellow]Target (IP or URL)[/bold yellow]" if is_l7 else "[bold yellow]Target (IP Address)[/bold yellow]"
        target = Prompt.ask(target_prompt).strip()
        if not target:
            console.print("[bold red]❌ Target cannot be empty![/bold red]")
            return ModernCLI.get_attack_params(choice)

        from .security import validate_target
        if not validate_target(target):
            console.print("[bold red]❌ Invalid target format![/bold red]")
            return ModernCLI.get_attack_params(choice)

        # Port input
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

        if is_l7:
            max_requests = IntPrompt.ask("[bold yellow]Total Requests (0 for unlimited)[/bold yellow]", default=0)
            proxy_file = Prompt.ask(f"[bold yellow]Proxy file[/bold yellow] [dim]({CONFIG['PROXY_FILE']})[/dim]", default="").strip()
            if proxy_file:
                from .utils import load_file_lines
                if os.path.isfile(proxy_file):
                    proxies = load_file_lines(proxy_file)
                    console.print(f"[green]✅ Loaded {len(proxies)} proxies[/green]")

        return {
            "target": target,
            "port": port,
            "threads": threads,
            "duration": duration,
            "max_requests": max_requests,
            "proxies": proxies
        }

    @staticmethod
    def display_attack_start(choice, params):
        """Display attack start information with real-time monitoring"""
        global current_monitor

        attack_info = Menu.ATTACKS.get(choice)
        if not attack_info:
            return

        # Attack summary table
        table = Table(title="[bold red]🚀 Attack Configuration[/bold red]", show_header=True, header_style="bold red")
        table.add_column("Parameter", style="cyan", width=12)
        table.add_column("Value", style="white", width=25)

        table.add_row("Attack Type", attack_info["name"])
        table.add_row("Target", params["target"])
        
        if choice == "17":
            table.add_row("Ports", params["port_text"])
        else:
            table.add_row("Port", str(params["port"]))

        table.add_row("Threads", str(params["threads"]))

        if choice != "17":
            table.add_row("Duration", f"{params['duration']}s")
            table.add_row("Proxies", str(len(params["proxies"])))

        console.print(table)
        console.print()

        # System check
        with console.status("[bold green]Checking system resources...[/bold green]", spinner="dots"):
            if not check_system_resources():
                console.print("[bold red]⚠️  Warning: System resources are running low![/bold red]")
                time.sleep(1)

        # Initialize monitor
        current_monitor = AttackMonitor(
            attack_info["name"], 
            params["target"], 
            params["duration"],
            params.get("max_requests", 0)
        )
        current_monitor.start_monitoring()

        # Start attack animation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("[bold green]Initializing attack...", total=None)
            time.sleep(1)
            progress.update(task, description="[bold green]Attack starting...[/bold green]")
            time.sleep(0.5)

        console.print("[bold green]✅ Attack launched successfully![/bold green]")
        console.print("[bold yellow]💡 Press Ctrl+C to stop the attack[/bold yellow]")
        console.print("[bold cyan]📊 Real-time monitoring active...[/bold cyan]")
        console.print()

        # Start attack in background
        from .classes import AttackDispatcher
        
        if choice == "17":
            # Port scanner is synchronous or handles its own threads
            AttackDispatcher.execute(choice, params)
            return

        attack_thread = threading.Thread(

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
    def display_attack_complete():
        """Display attack completion message"""
        panel = Panel(
            "[bold green]✅ Attack completed successfully![/bold green]\n"
            "[dim]Resource monitoring stopped[/dim]",
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
    def run():
        """Main CLI loop"""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        ModernCLI.display_banner()

        while True:
            ModernCLI.display_menu()
            choice = ModernCLI.get_choice()

            if choice is None:  # User wants to quit
                break

            try:
                params = ModernCLI.get_attack_params(choice)
                if params is None:
                    continue

                ModernCLI.display_attack_start(choice, params)
                ModernCLI.display_attack_complete()

            except KeyboardInterrupt:
                console.print("\n[bold yellow]⚠️  Attack interrupted by user[/bold yellow]")
            except Exception as e:
                ModernCLI.display_error(str(e))

            # Wait for user to continue
            console.print()
            input("[bold blue]Press Enter to continue...[/bold blue]")
            os.system('cls' if os.name == 'nt' else 'clear')
            ModernCLI.display_banner()