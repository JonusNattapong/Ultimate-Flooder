import time
import random
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.live import Live

console = Console()

class AnimatedBanner:
    """Animated banner system for startup and loading effects"""

    def __init__(self):
        self.console = console

    def animate_startup(self, duration=4.0):
        """Animate the startup banner with particle effects"""
        start_time = time.time()

        # Simple animation - could be enhanced with more effects
        with self.console.status("[bold green]Initializing IP-HUNTER...[/bold green]", spinner="dots"):
            time.sleep(duration)

        self.console.print("[bold green]✓[/bold green] System ready!")

    def animate_loading(self, message, duration=0.8):
        """Animate a loading message"""
        with self.console.status(f"[bold cyan]{message}[/bold cyan]", spinner="dots"):
            time.sleep(duration)

# Global instance
animated_banner = AnimatedBanner()