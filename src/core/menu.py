from src.config import CONFIG
from src.utils import load_file_lines
from src.security import validate_target

class Menu:
    ATTACKS = {
        "1": {"name": "Layer 7 HTTP Flood (Basic)", "func": "http_flood", "needs_root": False},
        "2": {"name": "Layer 7 Async HTTP Flood (Advanced + Proxies)", "func": "async_http_flood", "needs_root": False},
        "3": {"name": "Layer 4 SYN Flood", "func": "syn_flood", "needs_root": True},
        "4": {"name": "Layer 4 UDP Flood", "func": "udp_flood", "needs_root": True},
        "5": {"name": "Layer 7 Slowloris Attack", "func": "slowloris_attack", "needs_root": False},
        "6": {"name": "NTP Amplification Attack", "func": "ntp_amplification", "needs_root": True},
        "7": {"name": "Botnet C2 Server", "func": "botnet_c2", "needs_root": False},
        "8": {"name": "Cloudflare Bypass Flood", "func": "cloudflare_bypass_flood", "needs_root": False},
        "9": {"name": "Memcached Amplification Attack", "func": "memcached_amplification", "needs_root": True},
        "10": {"name": "SSDP Amplification Attack", "func": "ssdp_amplification", "needs_root": True},
        "11": {"name": "DNS Amplification Attack", "func": "dns_amplification", "needs_root": True},
        "12": {"name": "RUDY (R U Dead Yet?) Attack", "func": "rudy_attack", "needs_root": False},
        "13": {"name": "HOIC (High Orbit Ion Cannon) Attack", "func": "hoic_attack", "needs_root": False},
        "14": {"name": "HTTP/2 Rapid Reset (CVE-2023-44487)", "func": "http2_rapid_reset", "needs_root": False},
        "15": {"name": "Apache Range Header DoS", "func": "apache_killer", "needs_root": False},
        "16": {"name": "Nginx Range Header DoS", "func": "nginx_range_dos", "needs_root": False},
        "17": {"name": "Port Scanner", "func": "port_scanner", "needs_root": False},
        "18": {"name": "Launch Local Bot Client", "func": "launch_bot", "needs_root": False},
        "19": {"name": "ICMP / Ping of Death Flood", "func": "icmp_flood", "needs_root": True},
        "20": {"name": "Network Recon / Scanner", "func": "network_scanner", "needs_root": True},
        "21": {"name": "Deep IP Tracker (OSINT)", "func": "ip_tracker", "needs_root": False},
        "22": {"name": "AI-Adaptive Smart Flood", "func": "adaptive_flood", "needs_root": False},
        "23": {"name": "Vulnerability Scout", "func": "vulnerability_scout", "needs_root": False},
        "24": {"name": "Brute-Force Suite", "func": "brute_force_suite", "needs_root": False},
        "25": {"name": "Domain OSINT Multi-Hunter", "func": "domain_osint", "needs_root": False},
        "26": {"name": "Proxy Autopilot", "func": "proxy_autopilot", "needs_root": False},
        "27": {"name": "WiFi Ghost Recon", "func": "wifi_ghost", "needs_root": False},
        "28": {"name": "Packet Insight (Sniffer)", "func": "packet_insight", "needs_root": True},
        "29": {"name": "Payload Lab", "func": "payload_lab", "needs_root": False},
        "30": {"name": "Identity Cloak (OpSec)", "func": "identity_cloak", "needs_root": False},
        "31": {"name": "CVE Explorer", "func": "cve_explorer", "needs_root": False},
        "32": {"name": "Web Exposure Sniper", "func": "web_exposure_sniper", "needs_root": False}
    }

    @staticmethod
    def display():
        print("\nSelect Attack Type:")
        for key, attack in Menu.ATTACKS.items():
            print(f"{key}. {attack['name']}")
        return input("Enter choice: ").strip()

    @staticmethod
    def get_attack_params(choice):
        """Get attack parameters based on choice"""
        if choice == "7":
            try:
                c2_port_input = input("C2 Port (default 6667): ").strip()
                c2_port = int(c2_port_input) if c2_port_input else CONFIG['C2_DEFAULT_PORT']
                if not (1 <= c2_port <= 65535):
                    raise ValueError("Port must be between 1 and 65535")
            except ValueError as e:
                print(f"Invalid port: {e}")
                return None
            return {"c2_port": c2_port}

        target = input("Target (IP or URL): ").strip()
        if not target:
            print("Target cannot be empty!")
            return None

        if not validate_target(target):
            print("Invalid target format! Please enter a valid IP or URL.")
            return None

        try:
            port_input = input(f"Port (default {CONFIG['DEFAULT_PORT']}, range e.g. 1-1024): ").strip()
            if not port_input:
                port = CONFIG['DEFAULT_PORT']
            elif "-" in port_input or "," in port_input:
                port = port_input # Keep as string for scanner
            else:
                port = int(port_input)
                if not (1 <= port <= 65535):
                    raise ValueError("Port must be between 1 and 65535")

            threads_input = input(f"Threads (default {CONFIG['DEFAULT_THREADS']}, max 1000): ").strip()
            threads = int(threads_input) if threads_input else CONFIG['DEFAULT_THREADS']
            if not (1 <= threads <= 1000):
                raise ValueError("Threads must be between 1 and 1000")

            duration_input = input(f"Duration (seconds, default {CONFIG['DEFAULT_DURATION']}, max 3600): ").strip()
            duration = int(duration_input) if duration_input else CONFIG['DEFAULT_DURATION']
            if not (1 <= duration <= 3600):
                raise ValueError("Duration must be between 1 and 3600 seconds")

        except ValueError as e:
            print(f"Invalid input: {e}")
            return None

        proxy_file = input(f"Proxy file ({CONFIG['PROXY_FILE']}) or leave empty: ").strip()
        proxies = []
        if proxy_file:
            import os
            if not os.path.isfile(proxy_file):
                print(f"Proxy file not found: {proxy_file}")
            else:
                proxies = load_file_lines(proxy_file)

        return {
            "target": target,
            "port": port,
            "threads": threads,
            "duration": duration,
            "proxies": proxies
        }
