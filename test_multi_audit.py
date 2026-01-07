
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.attacks.exploits import vulnerability_scout
from rich.console import Console

console = Console()

def run_multi_test():
    targets = [
        "http://testphp.vulnweb.com",
        "https://demo.testfire.net",
        "http://example.com"
    ]
    
    console.print("[bold cyan]🚀 INITIATING SMART VULNERABILITY AUDIT[/]")
    
    for url in targets:
        console.print(f"\n[bold yellow]🔍 Analyzing Target: {url}[/]")
        try:
            # This calls the full Enterprise Scout logic
            vulnerability_scout(url)
        except Exception as e:
            console.print(f"[bold red][!] Error: {e}[/]")

if __name__ == "__main__":
    run_multi_test()
