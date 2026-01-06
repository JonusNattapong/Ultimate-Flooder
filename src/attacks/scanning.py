import socket
import os
import json
import time
from datetime import datetime
from scapy.all import ARP, Ether, srp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from src.utils.logging import add_system_log

console = Console()

def port_scanner(target, ports, threads=10):
    """Modern Multi-Threaded Port Scanner"""
    add_system_log(f"[bold cyan]SCAN:[/] Scanning ports on {target}")
    
    if isinstance(ports, str):
        if "-" in ports:
            start, end = map(int, ports.split("-"))
            ports = range(start, end + 1)
        else:
            ports = [int(p) for p in ports.split(",")]
    elif isinstance(ports, int):
        ports = [ports]

    open_ports = []
    
    def check_port(p):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, p))
            if result == 0:
                open_ports.append(p)
            sock.close()
        except:
            pass

    import threading
    thread_list = []
    for p in track(ports, description=f"[cyan]Scanning {target}...[/]"):
        t = threading.Thread(target=check_port, args=(p,))
        t.start()
        thread_list.append(t)
        if len(thread_list) >= threads:
            for thread in thread_list: thread.join()
            thread_list = []
            
    for t in thread_list: t.join()

    table = Table(title=f"Port Scan Report: {target}", border_style="cyan")
    table.add_column("Port", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Service", style="white")

    common_services = {21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3", 443: "HTTPS", 3306: "MySQL", 3389: "RDP"}

    if not open_ports:
        table.add_row("No open ports found", "-", "-")
    else:
        for p in sorted(open_ports):
            table.add_row(str(p), "OPEN", common_services.get(p, "Unknown"))
            add_system_log(f"[green]PORT FOUND:[/] {target}:{p} is open")

    console.print(Panel(table, border_style="cyan"))

def network_scanner(threads=250, subnet=None):
    """Modern Network Discovery with ARP & History Tracking"""
    add_system_log("[bold cyan]SCAN:[/] Initiating network-wide discovery...")
    
    if not subnet:
        # Try to auto-detect local network
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            subnet = ".".join(local_ip.split('.')[:-1]) + ".0/24"
        except:
            subnet = "192.168.1.0/24"

    console.print(f"\n[bold cyan]📡 Network Discovery Path: {subnet}[/bold cyan]")
    
    # ARP Scan
    try:
        ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=subnet), timeout=3, verbose=False)
        results = []
        for snd, rcv in ans:
            results.append({'ip': rcv.psrc, 'mac': rcv.hwsrc})
    except Exception as e:
        console.print(f"[red]Error during ARP scan: {e}[/]")
        return

    # Basic Port Scan for found hosts
    final_results = []
    def scan_host(ip, mac):
        hostname = "Unknown"
        try: hostname = socket.gethostbyaddr(ip)[0]
        except: pass
        
        open_ports = []
        for p in [80, 443, 21, 22, 3389]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((ip, p)) == 0: open_ports.append(str(p))
            s.close()
        
        final_results.append({
            'ip': ip, 
            'mac': mac, 
            'hostname': hostname, 
            'ports': open_ports
        })

    import threading
    threads_list = []
    for r in results:
        t = threading.Thread(target=scan_host, args=(r['ip'], r['mac']))
        t.start()
        threads_list.append(t)
    
    for t in threads_list: t.join()

    # Display results
    table = Table(title=f"Network Discovery: {subnet}", border_style="blue")
    table.add_column("IP Address", style="cyan")
    table.add_column("MAC Address", style="magenta")
    table.add_column("Hostname", style="white")
    table.add_column("Open Ports", style="yellow")

    for r in sorted(final_results, key=lambda x: x['ip']):
        table.add_row(r['ip'], r['mac'], r['hostname'], ", ".join(r['ports']) or "None")

    console.print(Panel(table, border_style="blue"))
