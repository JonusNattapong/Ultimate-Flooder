import os
import random
import socket
import platform
import subprocess
import time
import requests
from src.config import USER_AGENTS, REFERERS, CONFIG

def get_random_headers():
    """Generate random headers for requests"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": random.choice(REFERERS)
    }

def generate_stealth_headers():
    """Generate advanced stealth headers to avoid fingerprinting"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Referer": random.choice(REFERERS) if random.random() > 0.3 else "",
    }
    
    optional_headers = {
        "X-Requested-With": "XMLHttpRequest",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "X-Real-IP": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "CF-RAY": f"{random.randint(1000000000000000,9999999999999999)}-{random.choice(['CDG', 'FRA', 'LHR', 'AMS'])}",
        "X-Forwarded-Proto": "https",
        "X-Forwarded-Host": random.choice(["example.com", "google.com", "cloudflare.com"]),
    }
    
    for header in random.sample(list(optional_headers.keys()), random.randint(1, 3)):
        headers[header] = optional_headers[header]
    
    return headers

COMMON_PORTS = {
    20: "FTP-Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 88: "Kerberos", 110: "POP3", 115: "SFTP",
    135: "Microsoft RPC", 139: "NetBIOS", 143: "IMAP", 161: "SNMP",
    389: "LDAP", 443: "HTTPS", 445: "Microsoft-DS (SMB)", 465: "SMTPS",
    587: "SMTP Submission", 636: "LDAPS", 993: "IMAPS", 995: "POP3S",
    1433: "SQL Server", 1521: "Oracle DB", 3306: "MySQL", 3389: "RDP",
    5000: "Flask/Docker", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    8000: "HTTP-Alt", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB",
    25565: "Minecraft", 30120: "FiveM/GTA", 7777: "SA-MP"
}

def check_tor_running(port=9050):
    """Check if Tor is running on specified port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def find_tor_executable():
    """Find Tor executable path on the system"""
    system = platform.system().lower()
    
    if system == "windows":
        possible_paths = [
            r"C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
            r"C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
            os.path.expanduser(r"~\Desktop\Tor Browser\Browser\TorBrowser\Tor\tor.exe"),
            os.path.expanduser(r"~\Downloads\Tor Browser\Browser\TorBrowser\Tor\tor.exe"),
            os.path.expanduser(r"~\AppData\Local\Tor Browser\Browser\TorBrowser\Tor\tor.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        try:
            result = subprocess.run(['where', 'tor'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
    
    elif system == "linux":
        possible_paths = ["/usr/bin/tor", "/usr/local/bin/tor", "/opt/tor-browser/Browser/TorBrowser/Tor/tor"]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        try:
            result = subprocess.run(['which', 'tor'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
    
    elif system == "darwin":
        possible_paths = [
            "/Applications/Tor Browser.app/Contents/MacOS/Tor/tor",
            os.path.expanduser("~/Applications/Tor Browser.app/Contents/MacOS/Tor/tor"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    
    return None

def start_tor(tor_path=None, port=9050, bridges=None):
    """Start Tor process"""
    if tor_path is None:
        tor_path = find_tor_executable()
    
    if tor_path is None:
        return False, "Tor executable not found"
    
    try:
        if bridges:
            torrc_content = create_torrc_with_bridges(bridges)
        else:
            torrc_content = f"SocksPort {port}\nExitPolicy reject *:*\n"
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.torrc', delete=False) as f:
            f.write(torrc_content)
            torrc_path = f.name
        
        process = subprocess.Popen(
            [tor_path, '-f', torrc_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        wait_time = 60 if bridges else 30
        for i in range(wait_time):
            if check_tor_running(port):
                return True, f"Tor started successfully on port {port}"
            time.sleep(1)
        
        process.terminate()
        process.wait()
        try:
            os.unlink(torrc_path)
        except:
            pass
        return False, f"Tor failed to start within {wait_time} seconds"
    except Exception as e:
        return False, f"Error starting Tor: {str(e)}"

def create_torrc_with_bridges(bridges_list):
    """Create Tor configuration with bridges for censorship resistance"""
    if not bridges_list:
        return ""
    bridges_config = "\n".join([f"Bridge {bridge}" for bridge in bridges_list])
    return f"UseBridges 1\n{bridges_config}\nExitPolicy reject *:*\n"

def auto_start_tor_if_needed(port=9050):
    """Automatically start Tor if not running"""
    if check_tor_running(port):
        return True, "Tor is already running"
    return start_tor(port=port)

def check_vpn_running():
    """Check if VPN is running by checking network interfaces"""
    system = platform.system().lower()
    try:
        if system == "windows":
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
            output = result.stdout.lower()
            vpn_indicators = ['vpn', 'tap', 'tun', 'ppp', 'nordvpn', 'expressvpn', 'protonvpn']
            for indicator in vpn_indicators:
                if indicator in output:
                    return True, f"VPN detected ({indicator})"
        elif system in ["linux", "darwin"]:
            result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
            output = result.stdout.lower()
            vpn_indicators = ['tun', 'tap', 'ppp', 'vpn']
            for indicator in vpn_indicators:
                if indicator in output:
                    return True, f"VPN detected ({indicator})"
        return False, "No VPN detected"
    except Exception as e:
        return False, f"Error checking VPN: {str(e)}"

def generate_noise_traffic(num_requests=5):
    """Generate noise traffic to obscure real attacks"""
    noise_urls = ["https://httpbin.org/get", "https://api.ipify.org", "https://checkip.amazonaws.com", "https://icanhazip.com", "https://ipinfo.io/ip"]
    from src.utils.system import randomize_timing
    for i in range(num_requests):
        try:
            noise_url = random.choice(noise_urls)
            headers = generate_stealth_headers()
            requests.get(noise_url, headers=headers, timeout=5)
            randomize_timing(0.5, 2.0)
        except:
            pass

def create_proxy_chain(proxy_list, max_length=3):
    """Create a randomized proxy chain for maximum anonymity"""
    if not proxy_list or len(proxy_list) < 2:
        return proxy_list
    chain_length = min(max_length, len(proxy_list))
    selected_proxies = random.sample(proxy_list, chain_length)
    random.shuffle(selected_proxies)
    return selected_proxies

def validate_proxy_chain(chain):
    """Validate that all proxies in chain are working"""
    valid_proxies = []
    for proxy in chain:
        try:
            proxy_dict = {'http': proxy, 'https': proxy}
            response = requests.get('http://httpbin.org/ip', proxies=proxy_dict, timeout=10)
            if response.status_code == 200:
                valid_proxies.append(proxy)
        except:
            continue
    return valid_proxies

def setup_proxy_chain(proxy_list):
    """Setup a chain of proxies for maximum anonymity"""
    if not CONFIG['PROXY_CHAIN_ENABLED']:
        return proxy_list[0] if proxy_list else None
    chain = create_proxy_chain(proxy_list, CONFIG['PROXY_CHAIN_MAX_LENGTH'])
    return chain[0] if chain else None

def get_vpn_ip():
    """Get current public IP (useful for VPN verification)"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    return None
