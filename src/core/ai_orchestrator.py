"""
AI Orchestrator for IP-HUNTER v2.2.0
ศูนย์กลางการทำงานของ AI สำหรับ Auto-Reconnaissance, Smart Strategy และ Adaptive Control
"""

import asyncio
import socket
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

from src.utils.logging import add_system_log
from src.utils.ai import OffensiveAI, LangChainFree
from src.utils.threat_intelligence import ThreatIntelligence, threat_intel


class ServiceType(Enum):
    """ประเภทของ Service ที่ตรวจพบ"""
    WEB_SERVER = "web_server"
    DATABASE = "database"
    FTP = "ftp"
    SSH = "ssh"
    MAIL = "mail"
    DNS = "dns"
    GAME = "game"
    UNKNOWN = "unknown"


@dataclass
class PortInfo:
    """ข้อมูล Port ที่เปิดอยู่"""
    port: int
    service: str
    banner: str = ""
    is_secure: bool = False


@dataclass
class TargetProfile:
    """โปรไฟล์ของเป้าหมายที่วิเคราะห์แล้ว"""
    target: str
    ip_address: str = ""
    hostname: str = ""
    open_ports: List[PortInfo] = field(default_factory=list)
    services: List[ServiceType] = field(default_factory=list)
    has_waf: bool = False
    waf_type: str = ""
    has_cdn: bool = False
    cdn_type: str = ""
    ssl_enabled: bool = False
    http_server: str = ""
    os_guess: str = ""
    risk_score: int = 0
    scan_time: float = 0.0
    
    def get_primary_service(self) -> ServiceType:
        """ดึง Service หลักของ Target"""
        if ServiceType.WEB_SERVER in self.services:
            return ServiceType.WEB_SERVER
        elif self.services:
            return self.services[0]
        return ServiceType.UNKNOWN
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "ip": self.ip_address,
            "hostname": self.hostname,
            "open_ports": [{"port": p.port, "service": p.service} for p in self.open_ports],
            "services": [s.value for s in self.services],
            "has_waf": self.has_waf,
            "waf_type": self.waf_type,
            "has_cdn": self.has_cdn,
            "ssl_enabled": self.ssl_enabled,
            "http_server": self.http_server,
            "risk_score": self.risk_score
        }


@dataclass
class AttackSuggestion:
    """คำแนะนำการโจมตีจาก AI"""
    attack_id: str
    attack_name: str
    confidence: float  # 0.0 - 1.0
    reason: str
    recommended_threads: int = 100
    recommended_duration: int = 60
    use_tor: bool = False
    use_stealth: bool = True
    priority: int = 1  # 1 = highest priority


class AIOrchestrator:
    """
    AI Orchestrator - ศูนย์กลางการทำงานของ AI
    
    Features:
    - Auto-Reconnaissance: วิเคราะห์ Target อัตโนมัติก่อนโจมตี
    - Smart Strategy: แนะนำ Attack Vector ที่เหมาะสมที่สุด
    - Adaptive Control: ปรับ Attack Parameters แบบ Real-time
    """
    
    # Service mapping by port
    PORT_SERVICES = {
        21: ("FTP", ServiceType.FTP),
        22: ("SSH", ServiceType.SSH),
        23: ("Telnet", ServiceType.UNKNOWN),
        25: ("SMTP", ServiceType.MAIL),
        53: ("DNS", ServiceType.DNS),
        80: ("HTTP", ServiceType.WEB_SERVER),
        110: ("POP3", ServiceType.MAIL),
        143: ("IMAP", ServiceType.MAIL),
        443: ("HTTPS", ServiceType.WEB_SERVER),
        445: ("SMB", ServiceType.UNKNOWN),
        993: ("IMAPS", ServiceType.MAIL),
        995: ("POP3S", ServiceType.MAIL),
        1433: ("MSSQL", ServiceType.DATABASE),
        1521: ("Oracle", ServiceType.DATABASE),
        3306: ("MySQL", ServiceType.DATABASE),
        3389: ("RDP", ServiceType.UNKNOWN),
        5432: ("PostgreSQL", ServiceType.DATABASE),
        5900: ("VNC", ServiceType.UNKNOWN),
        6379: ("Redis", ServiceType.DATABASE),
        8080: ("HTTP-Alt", ServiceType.WEB_SERVER),
        8443: ("HTTPS-Alt", ServiceType.WEB_SERVER),
        27017: ("MongoDB", ServiceType.DATABASE),
    }
    
    # WAF signatures
    WAF_SIGNATURES = {
        "cloudflare": ["cloudflare", "cf-ray", "__cfduid"],
        "akamai": ["akamai", "ak_bmsc"],
        "aws_waf": ["awswaf", "x-amzn-requestid"],
        "sucuri": ["sucuri", "x-sucuri-id"],
        "incapsula": ["incapsula", "visid_incap"],
        "f5_bigip": ["bigip", "f5"],
    }
    
    # Attack recommendations by service type
    ATTACK_RECOMMENDATIONS = {
        ServiceType.WEB_SERVER: [
            ("1", "HTTP Flood (Stealth)", 0.9),
            ("2", "Async HTTP Flood", 0.85),
            ("8", "Cloudflare Bypass", 0.8),
            ("22", "AI-Adaptive Flood", 0.95),
            ("33", "Mixed Vector Flood", 0.75),
        ],
        ServiceType.DATABASE: [
            ("4", "UDP Flood", 0.7),
            ("3", "SYN Flood", 0.8),
        ],
        ServiceType.FTP: [
            ("3", "SYN Flood", 0.85),
            ("4", "UDP Flood", 0.7),
        ],
        ServiceType.SSH: [
            ("3", "SYN Flood", 0.9),
            ("5", "Slowloris", 0.6),
        ],
        ServiceType.DNS: [
            ("11", "DNS Amplification", 0.9),
            ("4", "UDP Flood", 0.8),
        ],
        ServiceType.UNKNOWN: [
            ("3", "SYN Flood", 0.7),
            ("4", "UDP Flood", 0.7),
            ("19", "Hybrid ICMP", 0.6),
        ],
    }
    
    def __init__(self):
        self.offensive_ai = OffensiveAI()
        self.threat_intel = threat_intel
        self.langchain = LangChainFree()
        self._scan_cache: Dict[str, TargetProfile] = {}
        self._last_suggestions: List[AttackSuggestion] = []
        
        # Callbacks for events
        self.on_scan_progress: Optional[Callable] = None
        self.on_analysis_complete: Optional[Callable] = None
    
    def analyze_target(self, target: str, quick_scan: bool = True) -> TargetProfile:
        """
        วิเคราะห์ Target แบบ Synchronous
        
        Args:
            target: URL หรือ IP address
            quick_scan: True = สแกนเฉพาะ port ทั่วไป, False = สแกนทั้งหมด
        
        Returns:
            TargetProfile พร้อมข้อมูลที่วิเคราะห์แล้ว
        """
        start_time = time.time()
        profile = TargetProfile(target=target)
        
        # Extract hostname/IP
        try:
            from urllib.parse import urlparse
            parsed = urlparse(target if "://" in target else f"http://{target}")
            hostname = parsed.hostname or target
            profile.hostname = hostname
            
            # Resolve IP
            try:
                profile.ip_address = socket.gethostbyname(hostname)
            except socket.gaierror:
                profile.ip_address = hostname  # Assume it's already an IP
                
        except Exception as e:
            add_system_log(f"[yellow]AI-WARN:[/] Failed to parse target: {e}")
            profile.ip_address = target
            profile.hostname = target
        
        # Check cache
        cache_key = profile.ip_address
        if cache_key in self._scan_cache:
            cached = self._scan_cache[cache_key]
            if time.time() - cached.scan_time < 300:  # 5 min cache
                add_system_log("[green]AI:[/] Using cached target profile")
                return cached
        
        # Port scanning
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 
                       993, 995, 1433, 3306, 3389, 5432, 8080, 8443]
        
        if self.on_scan_progress:
            self.on_scan_progress("Scanning ports...", 0)
        
        for i, port in enumerate(common_ports):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5 if quick_scan else 2.0)
                result = sock.connect_ex((profile.ip_address, port))
                sock.close()
                
                if result == 0:
                    service_info = self.PORT_SERVICES.get(port, ("Unknown", ServiceType.UNKNOWN))
                    port_info = PortInfo(
                        port=port,
                        service=service_info[0],
                        is_secure=(port in [443, 993, 995, 8443])
                    )
                    profile.open_ports.append(port_info)
                    
                    if service_info[1] not in profile.services:
                        profile.services.append(service_info[1])
                        
            except Exception:
                pass
            
            if self.on_scan_progress:
                progress = int((i + 1) / len(common_ports) * 50)
                self.on_scan_progress(f"Scanning port {port}...", progress)
        
        # Check for WAF/CDN (for web servers)
        if ServiceType.WEB_SERVER in profile.services:
            profile = self._detect_waf_cdn(profile)
            profile.ssl_enabled = any(p.port in [443, 8443] for p in profile.open_ports)
        
        # Calculate risk score
        profile.risk_score = self._calculate_risk_score(profile)
        profile.scan_time = time.time()
        
        # Cache result
        self._scan_cache[cache_key] = profile
        
        elapsed = time.time() - start_time
        add_system_log(f"[green]AI:[/] Target analysis complete in {elapsed:.2f}s")
        
        if self.on_analysis_complete:
            self.on_analysis_complete(profile)
        
        return profile
    
    def _detect_waf_cdn(self, profile: TargetProfile) -> TargetProfile:
        """ตรวจจับ WAF และ CDN"""
        try:
            import requests
            url = f"https://{profile.hostname}" if profile.ssl_enabled else f"http://{profile.hostname}"
            
            response = requests.head(url, timeout=5, allow_redirects=True)
            headers = {k.lower(): v.lower() for k, v in response.headers.items()}
            headers_str = str(headers)
            
            # Extract server header
            profile.http_server = response.headers.get("Server", "Unknown")
            
            # Detect WAF
            for waf_name, signatures in self.WAF_SIGNATURES.items():
                if any(sig in headers_str for sig in signatures):
                    profile.has_waf = True
                    profile.waf_type = waf_name
                    break
            
            # Detect CDN
            if "cloudflare" in headers_str:
                profile.has_cdn = True
                profile.cdn_type = "Cloudflare"
            elif "akamai" in headers_str:
                profile.has_cdn = True
                profile.cdn_type = "Akamai"
            elif "fastly" in headers_str:
                profile.has_cdn = True
                profile.cdn_type = "Fastly"
                
        except Exception as e:
            add_system_log(f"[yellow]AI-WARN:[/] WAF detection failed: {e}")
        
        return profile
    
    def _calculate_risk_score(self, profile: TargetProfile) -> int:
        """คำนวณ Risk Score (0-100)"""
        score = 50  # Base score
        
        # More open ports = higher risk
        score += len(profile.open_ports) * 3
        
        # WAF reduces attack success chance
        if profile.has_waf:
            score -= 15
        if profile.has_cdn:
            score -= 10
        
        # SSL reduces some attack vectors
        if profile.ssl_enabled:
            score -= 5
        
        # Specific services affect score
        if ServiceType.DATABASE in profile.services:
            score += 10  # Database exposure is risky
        if ServiceType.SSH in profile.services:
            score += 5
        
        return max(0, min(100, score))
    
    def suggest_attack_strategy(self, profile: TargetProfile, max_suggestions: int = 5) -> List[AttackSuggestion]:
        """
        แนะนำ Attack Strategy ตาม Target Profile
        
        Args:
            profile: TargetProfile จาก analyze_target()
            max_suggestions: จำนวน suggestions สูงสุด
        
        Returns:
            List ของ AttackSuggestion เรียงตาม confidence
        """
        suggestions = []
        primary_service = profile.get_primary_service()
        
        # Get base recommendations
        base_recs = self.ATTACK_RECOMMENDATIONS.get(primary_service, 
                                                     self.ATTACK_RECOMMENDATIONS[ServiceType.UNKNOWN])
        
        for attack_id, attack_name, base_confidence in base_recs:
            confidence = base_confidence
            reason_parts = [f"Effective against {primary_service.value}"]
            
            # Adjust for WAF
            if profile.has_waf:
                if attack_id in ["8", "22"]:  # Bypass attacks
                    confidence += 0.1
                    reason_parts.append(f"includes {profile.waf_type} bypass")
                else:
                    confidence -= 0.2
                    reason_parts.append(f"may be blocked by {profile.waf_type}")
            
            # Adjust for CDN
            if profile.has_cdn:
                if attack_id in ["8", "22", "33"]:
                    confidence += 0.05
                else:
                    confidence -= 0.1
            
            # Recommend stealth for protected targets
            use_stealth = profile.has_waf or profile.has_cdn
            use_tor = profile.has_waf and profile.waf_type == "cloudflare"
            
            # Calculate recommended parameters
            if profile.has_waf:
                rec_threads = 50  # Lower for stealth
                rec_duration = 120  # Longer for effectiveness
            else:
                rec_threads = 100
                rec_duration = 60
            
            suggestion = AttackSuggestion(
                attack_id=attack_id,
                attack_name=attack_name,
                confidence=max(0.1, min(1.0, confidence)),
                reason="; ".join(reason_parts),
                recommended_threads=rec_threads,
                recommended_duration=rec_duration,
                use_tor=use_tor,
                use_stealth=use_stealth,
                priority=len(suggestions) + 1
            )
            suggestions.append(suggestion)
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        self._last_suggestions = suggestions[:max_suggestions]
        
        # Generate AI-enhanced strategy if available
        try:
            target_summary = f"""
            Target: {profile.target}
            IP: {profile.ip_address}
            Open Ports: {', '.join([f"{p.port}/{p.service}" for p in profile.open_ports])}
            WAF: {profile.waf_type if profile.has_waf else 'None'}
            CDN: {profile.cdn_type if profile.has_cdn else 'None'}
            Server: {profile.http_server}
            """
            ai_strategy = self.offensive_ai.generate_attack_strategy(target_summary)
            add_system_log(f"[cyan]AI Strategy:[/] {ai_strategy[:100]}...")
        except Exception as e:
            add_system_log(f"[yellow]AI-WARN:[/] AI strategy generation failed: {e}")
        
        return self._last_suggestions
    
    def get_adaptive_params(self, attack_id: str, current_success_rate: float, 
                           current_response_time: float) -> Dict[str, Any]:
        """
        ปรับ Parameters แบบ Adaptive ตาม Real-time metrics
        
        Args:
            attack_id: ID ของ attack ที่กำลังรัน
            current_success_rate: อัตราความสำเร็จปัจจุบัน (0.0-1.0)
            current_response_time: Response time เฉลี่ย (seconds)
        
        Returns:
            Dict ของ parameters ที่แนะนำให้ปรับ
        """
        adjustments = {}
        
        if current_success_rate < 0.3:
            # Low success rate - might be blocked
            adjustments["reduce_threads"] = True
            adjustments["enable_stealth"] = True
            adjustments["rotate_user_agent"] = True
            adjustments["message"] = "Low success rate detected. Enabling stealth mode."
        elif current_success_rate > 0.9 and current_response_time < 0.5:
            # Very high success, fast response - target is handling well
            adjustments["increase_threads"] = True
            adjustments["message"] = "Target handling load well. Increasing intensity."
        elif current_response_time > 5.0:
            # Slow response - target might be struggling
            adjustments["maintain_pressure"] = True
            adjustments["message"] = "Target showing stress. Maintaining pressure."
        
        return adjustments
    
    def get_last_suggestions(self) -> List[AttackSuggestion]:
        """ดึง suggestions ล่าสุด"""
        return self._last_suggestions
    
    def clear_cache(self):
        """ล้าง scan cache"""
        self._scan_cache.clear()
        add_system_log("[green]AI:[/] Target cache cleared")


# Global instance
ai_orchestrator = AIOrchestrator()
