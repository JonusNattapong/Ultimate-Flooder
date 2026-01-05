# Modern CLI Interface for Ultimate Flooder
# อินเทอร์เฟซ CLI สมัยใหม่สำหรับ Ultimate Flooder

import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich.columns import Columns
from rich.align import Align
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.style import Style
from rich.layout import Layout
from rich.padding import Padding

from .config import BANNER, CONFIG
from .classes import Menu, AttackDispatcher
from .security import check_system_resources

# Initialize Rich Console
console = Console()

class ModernCLI:
    """Modern CLI interface using Rich library"""

    @staticmethod
    def display_banner():
        """Display the ASCII banner with colors"""
        banner_text = Text(BANNER, style="bold cyan")
        panel = Panel(
            Align.center(banner_text),
            title="[bold red]Ultimate Flooder v2.0[/bold red]",
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
        table = Table(title="[bold magenta]🚀 Attack Selection Menu[/bold magenta]", show_header=True, header_style="bold blue")
        table.add_column("ID", style="cyan", justify="center", width=4)
        table.add_column("Attack Type", style="white", width=35)
        table.add_column("Layer", style="green", justify="center", width=6)
        table.add_column("Root Required", style="red", justify="center", width=12)

        layer_mapping = {
            "1": "7", "2": "7", "3": "4", "4": "4", "5": "7", "6": "4",
            "7": "C2", "8": "7", "9": "4", "10": "4", "11": "4", "12": "7",
            "13": "7", "14": "7", "15": "7", "16": "7"
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

        # Standard attack parameters
        attack_info = Menu.ATTACKS.get(choice)
        if not attack_info:
            return None

        panel = Panel(
            f"[bold cyan]{attack_info['name']} Configuration[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(panel)

        # Target input
        target = Prompt.ask("[bold yellow]Target (IP or URL)[/bold yellow]").strip()
        if not target:
            console.print("[bold red]❌ Target cannot be empty![/bold red]")
            return ModernCLI.get_attack_params(choice)

        from .security import validate_target
        if not validate_target(target):
            console.print("[bold red]❌ Invalid target format! Please enter a valid IP or URL.[/bold red]")
            return ModernCLI.get_attack_params(choice)

        # Port input
        try:
            port = IntPrompt.ask(
                "[bold yellow]Port[/bold yellow]",
                default=CONFIG['DEFAULT_PORT']
            )

            if not (1 <= port <= 65535):
                console.print("[bold red]❌ Port must be between 1 and 65535[/bold red]")
                return ModernCLI.get_attack_params(choice)

        except ValueError:
            console.print("[bold red]❌ Invalid port number[/bold red]")
            return ModernCLI.get_attack_params(choice)

        # Threads input
        try:
            threads = IntPrompt.ask(
                "[bold yellow]Threads[/bold yellow]",
                default=CONFIG['DEFAULT_THREADS']
            )

            if not (1 <= threads <= 1000):
                console.print("[bold red]❌ Threads must be between 1 and 1000[/bold red]")
                return ModernCLI.get_attack_params(choice)

        except ValueError:
            console.print("[bold red]❌ Invalid thread count[/bold red]")
            return ModernCLI.get_attack_params(choice)

        # Duration input
        try:
            duration = IntPrompt.ask(
                "[bold yellow]Duration (seconds)[/bold yellow]",
                default=CONFIG['DEFAULT_DURATION']
            )

            if not (1 <= duration <= 3600):
                console.print("[bold red]❌ Duration must be between 1 and 3600 seconds[/bold red]")
                return ModernCLI.get_attack_params(choice)

        except ValueError:
            console.print("[bold red]❌ Invalid duration[/bold red]")
            return ModernCLI.get_attack_params(choice)

        # Proxy file input
        proxy_file = Prompt.ask(
            f"[bold yellow]Proxy file[/bold yellow] [dim]({CONFIG['PROXY_FILE']})[/dim]",
            default=""
        ).strip()

        # Validate proxy file
        proxies = []
        if proxy_file:
            from .utils import load_file_lines
            if not os.path.isfile(proxy_file):
                console.print(f"[bold red]❌ Proxy file not found: {proxy_file}[/bold red]")
            elif os.path.getsize(proxy_file) > 1024 * 1024:
                console.print("[bold red]❌ Proxy file too large (max 1MB)[/bold red]")
            else:
                proxies = load_file_lines(proxy_file)
                console.print(f"[green]✅ Loaded {len(proxies)} proxies from {proxy_file}[/green]")

        return {
            "target": target,
            "port": port,
            "threads": threads,
            "duration": duration,
            "proxies": proxies
        }

    @staticmethod
    def display_attack_start(choice, params):
        """Display attack start information"""
        attack_info = Menu.ATTACKS.get(choice)
        if not attack_info:
            return

        # Attack summary table
        table = Table(title="[bold red]🚀 Attack Configuration[/bold red]", show_header=True, header_style="bold red")
        table.add_column("Parameter", style="cyan", width=12)
        table.add_column("Value", style="white", width=25)

        table.add_row("Attack Type", attack_info["name"])
        table.add_row("Target", params["target"])
        table.add_row("Port", str(params["port"]))
        table.add_row("Threads", str(params["threads"]))
        table.add_row("Duration", f"{params['duration']}s")
        table.add_row("Proxies", str(len(params["proxies"])))

        console.print(table)
        console.print()

        # System check
        with console.status("[bold green]Checking system resources...[/bold green]", spinner="dots"):
            if not check_system_resources():
                console.print("[bold red]⚠️  Warning: System resources are running low![/bold red]")
                time.sleep(1)

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
        console.print()

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
            "[bold cyan]👋 Thank you for using Ultimate Flooder![/bold cyan]\n"
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
                AttackDispatcher.execute(choice, params)
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