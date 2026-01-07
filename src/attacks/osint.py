import requests
import re
import time
from rich.live import Live
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from src.utils.logging import add_system_log
from src.utils.ui import create_cyber_progress

def ip_tracker(target_ip=None):
    """Deep OSINT IP Tracker - Get detailed geolocation and network intel"""
    console = Console()
    
    if not target_ip:
        try:
            target_ip = requests.get('https://api.ipify.org', timeout=5).text.strip()
        except:
            console.print("[bold red] Error: Could not determine your public IP.[/]")
            return

    private_patterns = [
        r'^10\.',                   # 10.0.0.0 – 10.255.255.255
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.', # 172.16.0.0 – 172.31.255.255
        r'^192\.168\.',             # 192.168.0.0 – 192.168.255.255
        r'^127\.',                  # 127.0.0.0 – 127.255.255.255
        r'^169\.254\.'              # APIPA
    ]
    
    is_private = any(re.match(pattern, target_ip) for pattern in private_patterns)
    if is_private:
        console.print(f"\n[bold yellow]  🛰️  INITIATING DEEP TRACKING: {target_ip}[/]")
        console.print(Panel(
            f"[bold yellow]⚠️  Local/Private IP Detected[/bold yellow]\n\n"
            f"ไอพี [white]{target_ip}[/white] เป็นไอพีภายในเครือข่าย (LAN)\n"
            f"ระบบ OSINT ไม่สามารถระบุที่อยู่ทางภูมิศาสตร์ของไอพีส่วนตัวได้",
            border_style="yellow", title="IP-Tracker Info"
        ))
        return

    console.print(f"\n[bold yellow]  🛰️  INITIATING DEEP TRACKING: {target_ip}[/]")
    with create_cyber_progress("[bold cyan]INTELLIGENCE GATHERING FROM OSINT DATABASE...[/bold cyan]") as progress:
        task = progress.add_task("OSINT Tracking")
        try:
            fields = "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query,reverse"
            response = requests.get(f"http://ip-api.com/json/{target_ip}?fields={fields}", timeout=10)
            data = response.json()
            progress.update(task, advance=100)
            
            if data.get('status') == 'fail':
                console.print(f"[bold red] Tracking Failed:[/] {data.get('message', 'Unknown error')}")
                return

            table = Table(title=f" DEEP INTEL REPORT: {target_ip}", border_style="bold blue", title_style="bold underline white")
            table.add_column("Category", style="cyan", no_wrap=True)
            table.add_column("Information", style="white")

            table.add_row(" Location", f"{data.get('city', 'N/A')}, {data.get('regionName', 'N/A')} ({data.get('region', 'N/A')}), {data.get('country', 'N/A')}")
            table.add_row(" Zip/Postal", data.get('zip', 'N/A'))
            table.add_row(" Timezone", data.get('timezone', 'N/A'))
            table.add_row(" ISP", data.get('isp', 'N/A'))
            table.add_row(" ASN", data.get('as', 'N/A'))
            
            lat, lon = data.get('lat'), data.get('lon')
            google_maps = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            table.add_row(" Physical Map", f"[link={google_maps}][underline blue]Open in Google Maps[/link]")

            console.print("\n")
            console.print(Panel(table, border_style="blue", expand=False))
            add_system_log(f"[cyan]OSINT:[/] Generated intel report for {target_ip}")
        except Exception as e:
            console.print(f"[bold red] Error connected to OSINT server:[/] {str(e)}")

from rich.live import Live
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from src.utils.logging import add_system_log
from src.utils.ui import create_cyber_progress

def domain_osint(domain):
    """Information gathering for domains (Subdomains, DNS) with Live Streaming"""
    add_system_log(f"[bold cyan]OSINT:[/] Hunting subdomains for {domain}")
    console = Console()
    
    results_table = Table(title=f"🌐 [bold white]Domain Intelligence Hunter:[/] [cyan]{domain}[/]", border_style="cyan", expand=True)
    results_table.add_column("Category", style="cyan", width=20)
    results_table.add_column("Details / Findings", style="white")

    progress = create_cyber_progress(f"[cyan]Hunting Vectors for {domain}...[/]", total=2)
    task = progress.add_task("Hunting", total=2)

    with Live(Group(progress, results_table), refresh_per_second=4):
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
        time.sleep(0.5)

        # 2. DNS Lookup
        try:
            dns_resp = requests.get(f"https://api.hackertarget.com/dnslookup/?q={domain}", timeout=10)
            dns_info = dns_resp.text
            dns_lines = [l for l in dns_info.split("\n") if l.strip()][:10]
            results_table.add_row("DNS Snapshot", "\n".join(dns_lines))
        except:
            results_table.add_row("DNS Intel", "[red]API Fetch Error[/red]")
            
        progress.advance(task)
        time.sleep(0.5)
        progress.stop()

    console.print(Panel(f"[bold green]OSINT Reconnaissance complete for {domain}. Found {sub_count if 'sub_count' in locals() else 0} subdomains.[/]", border_style="green"))
        
    console.print(Panel(dns_table, border_style="cyan", title="DNS Intel"))

def identity_cloak():
    """Identity Cloak: Privacy audit and MAC Spoofing logic"""
    add_system_log("[bold cyan]CLOAK:[/] Running Privacy Audit...")
    console = Console()
    console.print("\n[bold white]👤 Identity Cloak: Operational Security Audit[/bold white]")
    
    # 1. IP and VPN Check
    try:
        ip_data = requests.get("http://ip-api.com/json/", timeout=5).json()
        current_ip = ip_data.get('query', 'Unknown')
        isp = ip_data.get('isp', '-')
        country = ip_data.get('country', '-')
    except:
        current_ip = "Unknown"; isp = "-"; country = "-"

    table = Table(title="Security Audit Results", border_style="blue")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="white")
    
    table.add_row("Public IP", current_ip)
    table.add_row("ISP / Data Center", isp)
    table.add_row("Physical Location", country)
    
    console.print(Panel(table, border_style="blue", title="Audit Report"))
    console.print(f"\n[bold yellow]💡 Stealth Tip:[/bold yellow] Use a VPN or Tor to hide your [red]{current_ip}[/red]")
    add_system_log("[green]CLOAK:[/] OpSec audit completed")
