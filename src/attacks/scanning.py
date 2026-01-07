import socket
import os
import json
import time
import random
import threading
import ipaddress
from datetime import datetime
from scapy.all import ARP, Ether, srp, IP, TCP, sr1, ICMP, sr, conf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Group
from src.utils.logging import add_system_log
from src.utils.ui import create_cyber_progress, CyberSpinnerColumn
from src.utils.network import COMMON_PORTS
import concurrent.futures

console = Console()
table_lock = threading.Lock() # Lock for thread-safe UI updates

def grab_banner(target, port):
    """Attempt to grab a service banner from an open port"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        s.connect((target, port))
        # Some services need a push to talk
        if port == 80: s.send(b"HEAD / HTTP/1.1\r\nHost: example.com\r\n\r\n")
        elif port == 21: pass # FTP usually sends welcome
        
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        s.close()
        return banner[:50]
    except:
        return "No Banner"

def port_scanner(target, ports, threads=10, stealth=True):
    """Professional Multi-Threaded Stealth (SYN) Port Scanner"""
    from src.utils.ui import create_cyber_progress
    mode = "STEALTH (SYN)" if stealth else "FULL (CONNECT)"
    add_system_log(f"[bold cyan]SCAN:[/] Running {mode} scan on {target}")
    
    if isinstance(ports, str):
        if "-" in ports:
            start, end = map(int, ports.split("-"))
            ports = list(range(start, end + 1))
        else:
            ports = [int(p) for p in ports.split(",")]
    elif isinstance(ports, int):
        ports = [ports]

    # Stealth: Randomize order to evade simple sequential detection
    random.shuffle(ports)
    
    open_ports = {}
    scapy_lock = threading.Lock()
    
    def syn_scan(p):
        """Half-open SYN scanning logic (Thread-safe for Windows)"""
        try:
            # Send SYN packet
            syn_pkt = IP(dst=target)/TCP(dport=p, flags="S")
            
            with scapy_lock:
                resp = sr1(syn_pkt, timeout=1, verbose=0)
            
            if resp and resp.haslayer(TCP):
                if resp.getlayer(TCP).flags == 0x12: # SA (SYN-ACK)
                    # Port is open! Send RST to close the half-open connection
                    rst_pkt = IP(dst=target)/TCP(dport=p, flags="R")
                    with scapy_lock:
                        sr1(rst_pkt, timeout=0.5, verbose=0)
                    
                    banner = grab_banner(target, p)
                    open_ports[p] = banner
        except:
            pass

    def connect_scan(p):
        """Standard full-connection scanning logic"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            if sock.connect_ex((target, p)) == 0:
                banner = grab_banner(target, p)
                open_ports[p] = banner
            sock.close()
        except: pass

    import concurrent.futures
    scan_func = syn_scan if stealth else connect_scan
    
    console.print(f"\n[bold yellow]🔍 Initiating {mode} Scan against {target}[/bold yellow]")
    
    # Live Results Table
    results_table = Table(title=f"Advanced Port Audit: {target}", border_style="cyan", expand=True)
    results_table.add_column("Port", style="yellow", width=10)
    results_table.add_column("Service & Common Usage", style="cyan", width=35)
    results_table.add_column("Status", style="green", width=15)
    results_table.add_column("Banner / Detail", style="white")

    progress = create_cyber_progress(f"[cyan]Hunting Ports on {target}...[/]", total=len(ports))
    task = progress.add_task("Scanning", total=len(ports))
    
    def worker(p):
        scan_func(p)
        if p in open_ports:
            banner = open_ports[p]
            service_desc = COMMON_PORTS.get(p, "Unknown Service")
            
            # --- PROFESSIONAL ENHANCEMENT: Risk Level Detection ---
            risk_level = "[green]LOW[/]"
            high_risk_ports = [21, 23, 135, 139, 445, 3389, 5900]
            if p in high_risk_ports:
                risk_level = "[bold red]HIGH RISK[/]"
            elif p in [80, 443, 8080]:
                risk_level = "[yellow]MEDIUM[/]"

            with table_lock:
                results_table.add_row(
                    str(p), 
                    f"{service_desc} ({risk_level})",
                    "OPEN (Active)", 
                    banner if banner != "No Banner" else "[dim]No Banner Data[/dim]"
                )
            add_system_log(f"[green]PORT FOUND:[/] {target}:{p} ({service_desc}) - Risk: {risk_level}")
        progress.advance(task)
        if stealth: time.sleep(random.uniform(0.01, 0.05))

    with Live(Group(progress, results_table), refresh_per_second=4):
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(worker, ports)

    if not open_ports:
        console.print(Panel("[bold red]No open ports detected.[/]", border_style="red"))
    else:
        console.print(Panel("[bold green]Scan Completed Successfully.[/]", border_style="green"))

def network_scanner(threads=250, subnet=None):
    """Modern Network Discovery with ARP for local subnets & Ping Sweep for remote subnets"""
    from src.utils.ui import create_cyber_progress
    add_system_log("[bold cyan]SCAN:[/] Initiating network-wide discovery...")

    # Determine local subnet
    local_subnet = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        local_subnet = ".".join(local_ip.split('.')[:-1]) + ".0/24"
    except:
        local_subnet = "192.168.1.0/24"

    if not subnet:
        subnet = local_subnet

    console.print(Panel(f"[bold cyan]📡 Network Discovery Path:[/] [yellow]{subnet}[/]", border_style="cyan"))

    # --- PHASE 1: DISCOVERY (ARP or PING) ---
    results = []
    from rich.progress import Progress, TextColumn

    if subnet == local_subnet:
        # Local subnet: Use ARP
        with Progress(
            CyberSpinnerColumn(),
            TextColumn("[bold green][SAT] Broadcasting ARP Requests...[/]"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task("", total=None)
            try:
                ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=subnet), timeout=5, retry=2, verbose=False)
                for snd, rcv in ans:
                    results.append({'ip': rcv.psrc, 'mac': rcv.hwsrc})
            except Exception as e:
                console.print(f"[red]Error during ARP scan: {e}[/]")
                return
    else:
        # Remote subnet: Use Ping Sweep
        with Progress(
            CyberSpinnerColumn(),
            TextColumn("[bold green]📡 Broadcasting ICMP Ping Requests...[/]"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task("", total=None)
            try:
                network = ipaddress.ip_network(subnet)
                ips = [str(ip) for ip in network.hosts()]
                pkts = [IP(dst=ip)/ICMP() for ip in ips]
                ans, unans = sr(pkts, timeout=2, retry=1, verbose=False)
                for snd, rcv in ans:
                    results.append({'ip': rcv.src, 'mac': 'N/A'})
            except Exception as e:
                console.print(f"[red]Error during ping sweep: {e}[/]")
                return

    if not results:
        console.print(Panel("[bold red]❌ No devices found on the network.[/bold red]", border_style="red"))
        return

    # --- PHASE 2: HOST EXPLORATION WITH LIVE OUTPUT ---
    final_results = []
    
    # 3. Final Table for Live Display
    table = Table(
        title=f"🌐 [bold white]Network Discovery Snapshot:[/] [cyan]{subnet}[/]", 
        border_style="bright_blue",
        header_style="bold magenta",
        show_lines=True,
        expand=True
    )
    table.add_column("IP Address", style="bold cyan")
    table.add_column("MAC Address", style="magenta")
    table.add_column("Hostname / Device Name", style="white")
    table.add_column("Open Ports", style="yellow")

    progress = create_cyber_progress("[bold white]🔍 Exploring Found Hosts...[/]", total=len(results))
    task_id = progress.add_task("Exploring", total=len(results))

    def scan_host(ip, mac):
        hostname = "Unknown"
        try: hostname = socket.gethostbyaddr(ip)[0]
        except: pass
        
        open_ports = []
        # Check most common ports only for speed in local discovery
        for p in [80, 443, 21, 22, 3389, 445, 135, 139]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            if s.connect_ex((ip, p)) == 0:
                service = COMMON_PORTS.get(p, str(p))
                open_ports.append(f"{p}({service})")
            s.close()
        
        res = {'ip': ip, 'mac': mac, 'hostname': hostname, 'ports': open_ports}
        final_results.append(res)
        
        # Update live table with lock
        ports_str = ", ".join(open_ports) if open_ports else "[dim]None Detected[/dim]"
        with table_lock:
            table.add_row(ip, mac, hostname, ports_str)
        add_system_log(f"[cyan]HOST DISCOVERED:[/] {ip} ({hostname})")
        progress.advance(task_id)

    with Live(Group(progress, table), refresh_per_second=4):
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(lambda r: scan_host(r['ip'], r['mac']), results)

    # --- PHASE 3: FINAL STATUS ---
    console.print(Panel(f"[bold green]Network discovery complete for {subnet}. Found {len(final_results)} active devices.[/]", border_style="green"))
    add_system_log(f"[bold green]SCAN COMPLETE:[/] Found {len(final_results)} active hosts in {subnet}")

    # OPTIONAL: Ask to add to library
    if final_results:
        from src.modern_cli import ModernCLI
        ans = console.input("\n[bold white]Add found targets to locked library? (y/n): [/]").strip().lower()
        if ans == 'y':
            for r in final_results:
                if r['ip'] not in ModernCLI.locked_targets:
                    ModernCLI.locked_targets.append(r['ip'])
            console.print("[bold green]✅ Targets imported to Library (ID 0).[/bold green]")
            time.sleep(1.5)
