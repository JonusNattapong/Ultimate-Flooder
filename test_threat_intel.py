import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.attacks.exploits import vulnerability_scout
from rich.console import Console

console = Console()

def test_threat_intelligence():
    targets = [
        "http://testphp.vulnweb.com"
    ]

    console.print("[bold cyan]🧠 TESTING THREAT INTELLIGENCE PLATFORM[/]")

    for url in targets:
        console.print(f"\n[bold yellow]🔍 Analyzing Target with Threat Intel: {url}[/]")
        try:
            # This calls the full Enterprise Scout logic with threat intelligence
            vulnerability_scout(url)
        except Exception as e:
            console.print(f"[bold red][!] Error: {e}[/]")

if __name__ == "__main__":
    test_threat_intelligence()