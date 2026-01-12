
import json
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.utils.logging import add_system_log

console = Console()
TARGETS_FILE = "txt/target_library.json"

def load_targets():
    if not os.path.exists(TARGETS_FILE):
        return []
    try:
        with open(TARGETS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_targets(targets):
    os.makedirs(os.path.dirname(TARGETS_FILE), exist_ok=True)
    with open(TARGETS_FILE, 'w') as f:
        json.dump(targets, f, indent=4)

def target_mgmt():
    """ID 0: Target Library Management"""
    while True:
        targets = load_targets()
        table = Table(title="[bold green]Target Library[/]", expand=True)
        table.add_column("ID", style="green")
        table.add_column("Target", style="white")
        table.add_column("Port", style="cyan")
        table.add_column("Notes", style="dim")

        for idx, t in enumerate(targets):
            table.add_row(str(idx), t.get('target'), str(t.get('port')), t.get('notes', '-'))

        console.clear()
        console.print(Panel(table, border_style="bright_green"))
        console.print("[green](a)[/] Add Target  [green](d)[/] Delete Target  [green](q)[/] Quit")
        
        choice = input("\nAction: ").lower()
        if choice == 'q':
            break
        elif choice == 'a':
            target = input("Target: ").strip()
            port = input("Port: ").strip()
            notes = input("Notes: ").strip()
            if target:
                targets.append({"target": target, "port": port, "notes": notes})
                save_targets(targets)
                add_system_log(f"[green]LIBRARY:[/] Added {target} to library")
        elif choice == 'd':
            idx = input("ID to delete: ").strip()
            if idx.isdigit() and int(idx) < len(targets):
                removed = targets.pop(int(idx))
                save_targets(targets)
                add_system_log(f"[yellow]LIBRARY:[/] Removed {removed['target']} from library")
