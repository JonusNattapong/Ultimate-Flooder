import socket
import os
import json
import time
import random
from datetime import datetime
from scapy.all import ARP, Ether, srp, IP, TCP, sr1, conf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from src.utils.logging import add_system_log

console = Console()

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
    
    def syn_scan(p):
        """Half-open SYN scanning logic"""
        try:
            # Send SYN packet
            syn_pkt = IP(dst=target)/TCP(dport=p, flags="S")
            resp = sr1(syn_pkt, timeout=1, verbose=0)
            
            if resp and resp.haslayer(TCP):
                if resp.getlayer(TCP).flags == 0x12: # SA (SYN-ACK)
                    # Port is open! Send RST to close the half-open connection
                    rst_pkt = IP(dst=target)/TCP(dport=p, flags="R")
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

    import threading
    thread_list = []
    scan_func = syn_scan if stealth else connect_scan
    
    console.print(f"\n[bold yellow]🔍 Initiating {mode} Scan against {target}[/bold yellow]")
    
    for p in track(ports, description=f"[cyan]Hunting Ports...[/]"):
        t = threading.Thread(target=scan_func, args=(p,))
        t.start()
        thread_list.append(t)
        
        # Adaptive Delay for Stealth
        if stealth: time.sleep(random.uniform(0.01, 0.05))

        if len(thread_list) >= threads:
            for thread in thread_list: thread.join()
            thread_list = []
            
    for t in thread_list: t.join()

    table = Table(title=f"Advanced Port Audit: {target}", border_style="cyan")
    table.add_column("Port", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Service/Banner", style="white")

    common_services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 
        80: "HTTP", 110: "POP3", 443: "HTTPS", 3306: "MySQL", 
        3389: "RDP", 8080: "Proxy/Alt-HTTP"
    }

    if not open_ports:
        table.add_row("No open ports detected", "-", "-")
    else:
        for p in sorted(open_ports.keys()):
            banner = open_ports[p]
            service_name = common_services.get(p, "Unknown")
            display_info = f"{service_name} | {banner}" if banner != "No Banner" else service_name
            table.add_row(str(p), "OPEN (Active)", display_info)
            add_system_log(f"[green]PORT FOUND:[/] {target}:{p} ({service_name})")

    console.print(Panel(table, border_style="cyan", title=f"Audit Mode: {mode}"))

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
