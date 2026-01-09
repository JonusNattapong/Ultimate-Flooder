import time
import random
from rich.text import Text
from rich.progress import Progress, ProgressColumn, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.columns import Columns
from rich.align import Align
from rich.layout import Layout

console = Console()

class CyberSpinnerColumn(ProgressColumn):
    """15 Custom Cyberpunk Spinner styles"""
    def __init__(self, style_id=None):
        super().__init__()
        self.themes = {
            1: ["( . )", "( .)", "( . )", "( . )", "( . )", "( . )"],  # Cyber Pulse
            2: ["<===>", "<=-->", "<--- >", "< -- >", "<  -->", "<===>"],  # Neon Wave
            3: ["[> ]", "[=> ]", "[==> ]", "[===> ]", "[====>]"],  # Scanner Beam
            4: ["[* ]", "[** ]", "[*** ]", "[**** ]", "[ *** ]"],  # Matrix Flow
            5: ["{ --- }", "{=---=}", "{==--==}", "{=== ===}", "{ --- }"],  # Ghost Grip
            6: ["| / - \\ ", "/ - \\ |", "- \\ | /", "\\ | / -"],  # Satellite Sweep
            7: ["(( ))", "( ( ))", "( ( ))", "(( ) )", "(( ))"],  # Data Pulse
            8: ["o O o", "O o O", "o O o", "O o O"],  # Neural Link
            9: ["[#---]", "[##--]", "[###-]", "[####]"],  # Breach Protocol
            10: ["< . >", "< .. >", "< ... >", "< . >"],  # Phantom Signal
            11: ["[#-#-#]", "[##-#-#]", "[###-#]", "[####-]"],  # Glitch Grid
            12: ["[0x3F]", "[0xA1]", "[0xCC]", "[0xEE]"],  # Hex Harvest
            13: ["^ v < >", "> ^ v <", "< > ^ v", "v < > ^"],  # Vortex Scan
            14: ["[ \\ ]", "[ | ]", "[ / ]", "[ - ]"],  # Stealth Radar
            15: ["o-o-o", "-o-o-", "o-o-o", "-o-o-"],  # Node Connect
        }
        self.style_id = style_id if style_id else random.randint(1, 15)
        self.frames = self.themes.get(self.style_id, self.themes[1])

    def render(self, task=None):
        idx = int(time.time() * 8) % len(self.frames)
        colors = ["green", "cyan", "magenta", "yellow", "bright_blue"]
        color = colors[self.style_id % len(colors)]
        return Text(self.frames[idx], style=f"bold {color}")

class GlowBarColumn(BarColumn):
    """A customized bar column with a neon glow effect"""
    def render(self, task):
        bar = super().render(task)
        if task.percentage is not None:
            # Create a glow effect based on progress
            if task.percentage < 33:
                self.complete_style = "bold red"
            elif task.percentage < 66:
                self.complete_style = "bold yellow"
            else:
                self.complete_style = "bold green"
        return bar

def create_cyber_progress(description="[cyan]Processing...[/]", total=None, transient=True):
    """Creates a pre-configured Progress instance with Cyber Spinner and Glow Bar"""
    return Progress(
        CyberSpinnerColumn(),
        TextColumn("[bold cyan]⫸[/] [progress.description]{task.description}"),
        GlowBarColumn(
            bar_width=40,
            complete_style="bold green",
            finished_style="bold bright_green",
            pulse_style="bold white"
        ),
        TaskProgressColumn(text_format="[bold white]{task.percentage:>3.0f}%[/]"),
        TextColumn(" [bold magenta]📡[/]"),
        console=console,
        transient=transient,
        refresh_per_second=15
    )

def create_attack_config_panel(choice, attack_info):
    """Create a detailed configuration panel for each attack ID"""
    from src.core.menu import Menu

    attack = Menu.ATTACKS.get(choice, {})
    name = attack.get('name', 'Unknown Attack')
    category = attack.get('category', 'Unknown')
    needs_root = attack.get('needs_root', False)

    # Create layout for config page
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=6),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3)
    )

    # Header with attack details
    header_panel = Panel(
        Align.center(f"[bold bright_green]{name}[/bold bright_green]\n"
                    f"[dim cyan]{category} Attack[/dim cyan]\n"
                    f"[yellow]ID: {choice}[/yellow] | [red]Root Required: {'Yes' if needs_root else 'No'}[/red]"),
        title="[bold white] ATTACK CONFIGURATION [/bold white]",
        border_style="green",
        padding=(1, 2)
    )
    layout["header"].update(header_panel)

    # Body with parameter inputs
    body_layout = Layout()
    body_layout.split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1)
    )

    # Left side: Basic parameters
    basic_params = Table.grid(expand=True)
    basic_params.add_column()
    basic_params.add_row("[bold cyan]Basic Parameters:[/bold cyan]")
    basic_params.add_row("")

    # Add common parameters based on attack type
    if category == "Layer 7":
        basic_params.add_row("• Target URL/IP")
        basic_params.add_row("• Port (default: 80/443)")
        basic_params.add_row("• Threads (1-1000)")
        basic_params.add_row("• Duration (seconds)")
        basic_params.add_row("• Proxy List (optional)")
        basic_params.add_row("• User-Agent Rotation")
        basic_params.add_row("• Stealth Mode")
    elif category == "Layer 4":
        basic_params.add_row("• Target IP")
        basic_params.add_row("• Target Port")
        basic_params.add_row("• Threads (1-1000)")
        basic_params.add_row("• Duration (seconds)")
        basic_params.add_row("• Packet Size")
        basic_params.add_row("• Spoofing Options")
    elif category == "Amplification":
        basic_params.add_row("• Target IP")
        basic_params.add_row("• Amplification Factor")
        basic_params.add_row("• Duration (seconds)")
        basic_params.add_row("• Reflection Servers")
    elif category == "Scanning & Recon":
        basic_params.add_row("• Target (IP/URL/Domain)")
        basic_params.add_row("• Scan Type (Port/Network)")
        basic_params.add_row("• Port Range")
        basic_params.add_row("• Threads")
        basic_params.add_row("• Stealth Mode")
    else:
        basic_params.add_row("• Target")
        basic_params.add_row("• Custom Parameters")

    left_panel = Panel(basic_params, title="[bold blue] PARAMETERS [/bold blue]", border_style="blue")
    body_layout["left"].update(left_panel)

    # Right side: Advanced options
    advanced_options = Table.grid(expand=True)
    advanced_options.add_column()
    advanced_options.add_row("[bold magenta]Advanced Options:[/bold magenta]")
    advanced_options.add_row("")
    advanced_options.add_row("• TOR Integration")
    advanced_options.add_row("• VPN Auto-Connect")
    advanced_options.add_row("• Noise Traffic Generation")
    advanced_options.add_row("• Proxy Chain Setup")
    advanced_options.add_row("• Custom Headers")
    advanced_options.add_row("• Rate Limiting Bypass")
    advanced_options.add_row("• Anti-Detection Measures")

    right_panel = Panel(advanced_options, title="[bold magenta] ADVANCED [/bold magenta]", border_style="magenta")
    body_layout["right"].update(right_panel)

    layout["body"].update(body_layout)

    # Footer with navigation
    footer_panel = Panel(
        Align.center("[bold white]Use ↑↓ arrows to navigate • Enter to select • ESC to go back[/bold white]"),
        border_style="dim white",
        padding=(0, 1)
    )
    layout["footer"].update(footer_panel)

    return layout

def create_monitoring_dashboard(attack_name, target, duration, stats):
    """Create a real-time monitoring dashboard for attacks"""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="stats", ratio=1),
        Layout(name="logs", ratio=1),
        Layout(name="footer", size=2)
    )

    # Header
    header = Panel(
        Align.center(f"[bold bright_green]{attack_name}[/bold bright_green]\n"
                    f"[dim cyan]Target: {target}[/dim cyan]\n"
                    f"[yellow]Duration: {duration}s[/yellow]"),
        title="[bold white] LIVE MONITORING [/bold white]",
        border_style="green"
    )
    layout["header"].update(header)

    # Stats section
    stats_table = Table.grid(expand=True, padding=1)
    stats_table.add_column(ratio=1)
    stats_table.add_column(ratio=1)
    stats_table.add_column(ratio=1)

    stats_table.add_row(
        f"[bold green]Packets Sent:[/bold green]\n{stats.get('packets_sent', 0)}",
        f"[bold blue]Bytes Sent:[/bold blue]\n{stats.get('bytes_sent', 0)}",
        f"[bold yellow]Active Connections:[/bold yellow]\n{stats.get('active_connections', 0)}"
    )
    stats_table.add_row(
        f"[bold red]Failed Packets:[/bold red]\n{stats.get('packets_failed', 0)}",
        f"[bold cyan]Success Rate:[/bold cyan]\n{stats.get('success_rate', 0)}%",
        f"[bold magenta]Speed:[/bold magenta]\n{stats.get('speed', 0)} pps"
    )

    stats_panel = Panel(stats_table, title="[bold cyan] REAL-TIME STATS [/bold cyan]", border_style="cyan")
    layout["stats"].update(stats_panel)

    # Logs section
    logs_content = "\n".join(stats.get('logs', ['Monitoring started...']))
    logs_panel = Panel(logs_content, title="[bold green] ACTIVITY LOG [/bold green]", border_style="green")
    layout["logs"].update(logs_panel)

    # Footer
    footer = Panel(
        Align.center("[bold white]Press 'q' to stop • 'p' to pause • 'r' to resume[/bold white]"),
        border_style="dim white"
    )
    layout["footer"].update(footer)

    return layout
