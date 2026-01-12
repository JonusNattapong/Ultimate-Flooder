"""
API Integration for Ultimate Flooder
Shodan and Censys API clients for finding vulnerable servers
"""

import os
import time
import random
import requests
from typing import List, Dict, Optional
from src.utils.logging import add_system_log

class FreeAmplificationAPI:
    """Free alternative using public sources and community lists"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_ntp_servers(self, limit: int = 50) -> List[str]:
        """Get NTP servers from free sources"""
        servers = []

        # Try to get from public NTP pool lists
        try:
            # NTP Pool project
            response = self.session.get("https://www.ntppool.org/zone", timeout=10)
            if response.status_code == 200:
                # Parse some NTP servers (simplified)
                ntp_ips = [
                    "time.nist.gov:123",
                    "pool.ntp.org:123",
                    "asia.pool.ntp.org:123",
                    "europe.pool.ntp.org:123",
                    "north-america.pool.ntp.org:123"
                ]
                servers.extend(ntp_ips[:limit//2])
        except:
            pass

        # Add some known public NTP servers
        public_ntp = [
            "129.6.15.28:123",    # NIST
            "129.6.15.29:123",    # NIST
            "129.6.15.30:123",    # NIST
            "132.163.97.1:123",   # NIST
            "132.163.97.2:123",   # NIST
        ]
        servers.extend(public_ntp)

        servers = list(set(servers))[:limit]
        add_system_log(f"[green]Found {len(servers)} NTP servers (free sources)[/green]")
        return servers

    def get_memcached_servers(self, limit: int = 50) -> List[str]:
        """Get Memcached servers from free sources"""
        servers = []

        # Known vulnerable Memcached servers (from public reports)
        # Note: These may not be current - use with caution
        public_memcached = [
            "45.155.205.41:11211",
            "185.125.204.16:11211",
            "194.180.49.229:11211",
        ]

        servers.extend(public_memcached[:limit])
        add_system_log(f"[green]Found {len(servers)} Memcached servers (free sources)[/green]")
        return servers

    def get_ssdp_servers(self, limit: int = 50) -> List[str]:
        """Get SSDP servers from free sources"""
        servers = []

        # SSDP multicast address (the main amplification target)
        ssdp_servers = [
            "239.255.255.250:1900",  # SSDP multicast
        ]

        # Add some known UPnP devices
        public_ssdp = [
            "192.168.1.1:1900",     # Common router
            "192.168.0.1:1900",     # Common router
        ]

        servers.extend(ssdp_servers + public_ssdp)
        servers = list(set(servers))[:limit]
        add_system_log(f"[green]Found {len(servers)} SSDP servers (free sources)[/green]")
        return servers

    def get_dns_servers(self, limit: int = 50) -> List[str]:
        """Get DNS servers from free sources"""
        servers = []

        # Public DNS servers
        public_dns = [
            "8.8.8.8:53",          # Google DNS
            "8.8.4.4:53",          # Google DNS
            "1.1.1.1:53",          # Cloudflare DNS
            "1.0.0.1:53",          # Cloudflare DNS
            "208.67.222.222:53",   # OpenDNS
            "208.67.220.220:53",   # OpenDNS
            "9.9.9.9:53",          # Quad9
            "149.112.112.112:53",  # Quad9
        ]

        servers.extend(public_dns[:limit])
        add_system_log(f"[green]Found {len(servers)} DNS servers (free sources)[/green]")
        return servers


# Legacy Shodan/Censys classes (kept for compatibility but not used)
class ShodanAPI(FreeAmplificationAPI):
    """Legacy Shodan API - now uses free sources"""
    pass

class CensysAPI(FreeAmplificationAPI):
    """Legacy Censys API - now uses free sources"""
    pass


class AmplificationHunter:
    """Unified interface for finding amplification servers using FREE sources"""

    def __init__(self):
        self.free_api = FreeAmplificationAPI()
        # Keep legacy APIs for potential future use
        self.shodan = ShodanAPI()
        self.censys = CensysAPI()
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour

    def _get_cached(self, key: str) -> Optional[List[str]]:
        """Get cached results if still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_timeout:
                return data
            else:
                del self.cache[key]
        return None

    def _set_cached(self, key: str, data: List[str]):
        """Cache results"""
        self.cache[key] = (data, time.time())

    def get_ntp_servers(self, limit: int = 50, use_cache: bool = True) -> List[str]:
        """Get NTP servers from multiple sources (FREE sources first)"""
        cache_key = f"ntp_{limit}"

        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                add_system_log(f"[blue]Using cached NTP servers ({len(cached)})[/blue]")
                return cached

        servers = []

        # Use FREE API first
        free_servers = self.free_api.get_ntp_servers(limit)
        servers.extend(free_servers)

        # Fallback to paid APIs if free sources insufficient (but they won't be used)
        if len(servers) < limit:
            shodan_servers = self.shodan.get_ntp_servers(limit - len(servers))
            servers.extend(shodan_servers)

        if len(servers) < limit:
            censys_servers = self.censys.get_ntp_servers(limit - len(servers))
            servers.extend(censys_servers)

        # Remove duplicates and shuffle
        servers = list(set(servers))
        random.shuffle(servers)

        self._set_cached(cache_key, servers)
        add_system_log(f"[green]Total NTP servers found: {len(servers)}[/green]")
        return servers

    def get_memcached_servers(self, limit: int = 50, use_cache: bool = True) -> List[str]:
        """Get Memcached servers from multiple sources (FREE sources first)"""
        cache_key = f"memcached_{limit}"

        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                add_system_log(f"[blue]Using cached Memcached servers ({len(cached)})[/blue]")
                return cached

        servers = []

        # Use FREE API first
        free_servers = self.free_api.get_memcached_servers(limit)
        servers.extend(free_servers)

        # Fallback to paid APIs if free sources insufficient
        if len(servers) < limit:
            shodan_servers = self.shodan.get_memcached_servers(limit - len(servers))
            servers.extend(shodan_servers)

        if len(servers) < limit:
            censys_servers = self.censys.get_memcached_servers(limit - len(servers))
            servers.extend(censys_servers)

        servers = list(set(servers))
        random.shuffle(servers)

        self._set_cached(cache_key, servers)
        add_system_log(f"[green]Total Memcached servers found: {len(servers)}[/green]")
        return servers

    def get_ssdp_servers(self, limit: int = 50, use_cache: bool = True) -> List[str]:
        """Get SSDP servers from multiple sources (FREE sources first)"""
        cache_key = f"ssdp_{limit}"

        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                add_system_log(f"[blue]Using cached SSDP servers ({len(cached)})[/blue]")
                return cached

        servers = []

        # Use FREE API first
        free_servers = self.free_api.get_ssdp_servers(limit)
        servers.extend(free_servers)

        # Fallback to paid APIs if free sources insufficient
        if len(servers) < limit:
            shodan_servers = self.shodan.get_ssdp_servers(limit - len(servers))
            servers.extend(shodan_servers)

        if len(servers) < limit:
            censys_servers = self.censys.get_ssdp_servers(limit - len(servers))
            servers.extend(censys_servers)

        servers = list(set(servers))
        random.shuffle(servers)

        self._set_cached(cache_key, servers)
        add_system_log(f"[green]Total SSDP servers found: {len(servers)}[/green]")
        return servers

    def get_dns_servers(self, limit: int = 50, use_cache: bool = True) -> List[str]:
        """Get DNS servers from multiple sources (FREE sources first)"""
        cache_key = f"dns_{limit}"

        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                add_system_log(f"[blue]Using cached DNS servers ({len(cached)})[/blue]")
                return cached

        servers = []

        # Use FREE API first
        free_servers = self.free_api.get_dns_servers(limit)
        servers.extend(free_servers)

        # Fallback to paid APIs if free sources insufficient
        if len(servers) < limit:
            shodan_servers = self.shodan.get_dns_servers(limit - len(servers))
            servers.extend(shodan_servers)

        if len(servers) < limit:
            censys_servers = self.censys.get_dns_servers(limit - len(servers))
            servers.extend(censys_servers)

        servers = list(set(servers))
        random.shuffle(servers)

        self._set_cached(cache_key, servers)
        add_system_log(f"[green]Total DNS servers found: {len(servers)}[/green]")
        return servers


# Global instance
amplification_hunter = AmplificationHunter()