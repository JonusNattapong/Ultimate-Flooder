import requests
import re
import time
import socket
from rich.live import Live
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from src.utils.logging import add_system_log
from src.utils.ui import create_cyber_progress

def ip_tracker(target_ip=None):
    """[ID 21] Professional IP Intelligence & Proxy Detection"""
    console = Console()
    
    if not target_ip:
        try:
            target_ip = requests.get('https://api.ipify.org', timeout=5).text.strip()
        except:
            console.print("[bold red] Error: Could not determine public IP.[/]")
            return

    # Private IP check
    if target_ip.startswith(("10.", "192.168.", "127.", "172.16.", "172.17.", "172.18.", "172.19.", "172.2", "172.3")):
        console.print(Panel(f"[yellow]Target {target_ip} is a Private/Local IP. OSINT disabled.[/]", border_style="yellow"))
        return

    add_system_log(f"[bold cyan]OSINT:[/] Gathering tactical intel for {target_ip}")
    
    with create_cyber_progress("[bold cyan]INTELLIGENCE GATHERING...[/bold cyan]") as progress:
        task = progress.add_task("OSINT", total=100)
        try:
            fields = "status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,reverse,query"
            r = requests.get(f"http://ip-api.com/json/{target_ip}?fields={fields}", timeout=10)
            data = r.json()
            progress.update(task, completed=100)
            
            if data.get("status") == "fail":
                console.print(f"[bold red]API ERROR:[/] {data.get('message')}")
                return

            table = Table(title=f"📡 DEEP TACTICAL INTEL: {target_ip}", border_style="cyan", show_header=True)
            table.add_column("Vector", style="cyan", width=20)
            table.add_column("Finding", style="white")

            table.add_row("Location", f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}")
            table.add_row("Network / AS", f"{data.get('isp')} ({data.get('as')})")
            
            # ISP/Org fingerprinting for Cloud
            org = (str(data.get("isp")) + " " + str(data.get("org"))).lower()
            cloud = "Unknown"
            if "amazon" in org or "aws" in org: cloud = "[orange1]Amazon AWS[/orange1]"
            elif "google" in org: cloud = "[blue]Google Cloud[/blue]"
            elif "microsoft" in org or "azure" in org: cloud = "[bright_blue]Microsoft Azure[/bright_blue]"
            elif "cloudflare" in org: cloud = "[orange3]Cloudflare CDN[/orange3]"
            elif "digitalocean" in org: cloud = "[blue]DigitalOcean[/blue]"
            table.add_row("Provider Type", cloud)

            # OpSec Flags
            flags = []
            if data.get("proxy"): flags.append("[bold red]PROXY/VPN ACTIVE[/bold red]")
            if data.get("hosting"): flags.append("[bold yellow]DATA CENTER / HOSTING[/bold yellow]")
            if data.get("mobile"): flags.append("[cyan]CELLULAR NETWORK[/cyan]")
            table.add_row("Security Flags", ", ".join(flags) if flags else "[green]CLEAN (Residential/Direct)[/green]")
            
            table.add_row("Reverse DNS", data.get("reverse") or "[dim]None[/dim]")
            
            lat, lon = data.get('lat'), data.get('lon')
            map_url = f"https://www.google.com/maps?q={lat},{lon}"
            table.add_row("Coordinates", f"{lat}, {lon} ([link={map_url}]Maps[/link])")

            console.print("\n", Panel(table, border_style="cyan", expand=False))
            
        except Exception as e:
            console.print(f"[bold red]CRITICAL:[/] Connection to OSINT database lost: {e}")

def domain_osint(domain):
    """[ID 25] Deep Domain Intelligence and Subdomain Hunting"""
    add_system_log(f"[bold cyan]OSINT:[/] Hunting subdomains for {domain}")
    console = Console()
    
    results_table = Table(title=f"🌐 Domain Intelligence: {domain}", border_style="cyan", expand=True)
    results_table.add_column("Category", style="cyan", width=20)
    results_table.add_column("Details / Findings", style="white")

    with create_cyber_progress(f"[cyan]Hunting Vectors for {domain}...[/]") as progress:
        task = progress.add_task("Hunting", total=2)

        # 1. Subdomain Lookup
        try:
            sub_resp = requests.get(f"https://api.hackertarget.com/hostsearch/?q={domain}", timeout=10)
            subdomains = [s for s in sub_resp.text.split("\n") if s.strip()]
            sub_count = len(subdomains)
            top_subs = ", ".join([s.split(",")[0] for s in subdomains[:8]]) + "..."
            results_table.add_row("Subdomains Found", f"[bold green]{sub_count}[/bold green]")
            results_table.add_row("Major Entry Points", top_subs)
        except:
            results_table.add_row("Subdomains", "[red]API Fetch Error[/red]")
        
        progress.advance(task)

        # 2. DNS Lookup
        try:
            dns_resp = requests.get(f"https://api.hackertarget.com/dnslookup/?q={domain}", timeout=10)
            dns_info = dns_resp.text
            dns_lines = [l for l in dns_info.split("\n") if l.strip()]
            results_table.add_row("DNS Snapshot", "\n".join(dns_lines[:8]) + ("\n..." if len(dns_lines) > 8 else ""))
        except:
            results_table.add_row("DNS Intel", "[red]API Fetch Error[/red]")
            
        progress.advance(task)

    console.print(Panel(results_table, border_style="cyan"))
    add_system_log(f"[green]OSINT:[/] Completed reconnaissance for {domain}")

def identity_cloak():
    """[ID 30] Identity Cloak: Operational Security Audit"""
    add_system_log("[bold cyan]CLOAK:[/] Running Privacy Audit...")
    console = Console()
    
    try:
        ip_data = requests.get("http://ip-api.com/json/", timeout=5).json()
        current_ip = ip_data.get('query', 'Unknown')
        isp = ip_data.get('isp', '-')
        country = ip_data.get('country', '-')
        proxy = ip_data.get('proxy', False)
    except:
        current_ip = "Unknown"; isp = "-"; country = "-"; proxy = False

    table = Table(title="👤 OpSec Audit Results", border_style="blue")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="white")
    
    table.add_row("Public IP", current_ip)
    table.add_row("ISP / ASN", isp)
    table.add_row("Physical Location", country)
    table.add_row("VPN/Proxy Active", "[green]PROTECTED[/green]" if proxy else "[bold red]EXPOSED[/bold red]")
    
    console.print("\n", Panel(table, border_style="blue", expand=False))
    if not proxy:
        console.print(f"\n[bold yellow]💡 Stealth Tip:[/bold yellow] Use a VPN or Tor to hide your [red]{current_ip}[/red]")
    add_system_log("[green]CLOAK:[/] OpSec audit completed")
