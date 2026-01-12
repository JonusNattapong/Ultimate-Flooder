import json
import os
import time
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class ThreatIntelligence:
    """Advanced Threat Intelligence Platform for Ultimate Flooder"""

    def __init__(self, max_entries=50):
        self.threat_db = {}
        self.risk_scores = {}
        self.correlations = []
        self.max_entries = max_entries  # Limit memory usage

    def collect_intelligence(self, target, scan_results=None, vuln_results=None, osint_data=None):
        """Collect and correlate intelligence from multiple sources"""
        intel_id = f"{target}_{int(time.time())}"

        intel_data = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "sources": {},
            "risk_score": 0,
            "threat_level": "LOW",
            "recommendations": []
        }

        # 1. OSINT Intelligence
        if osint_data:
            intel_data["sources"]["osint"] = osint_data
            intel_data["risk_score"] += self._calculate_osint_risk(osint_data)

        # 2. Scanning Intelligence
        if scan_results:
            intel_data["sources"]["scanning"] = scan_results
            intel_data["risk_score"] += self._calculate_scan_risk(scan_results)

        # 3. Vulnerability Intelligence
        if vuln_results:
            intel_data["sources"]["vulnerabilities"] = vuln_results
            intel_data["risk_score"] += self._calculate_vuln_risk(vuln_results)

        # 4. Determine Threat Level
        intel_data["threat_level"] = self._determine_threat_level(intel_data["risk_score"])

        # 5. Generate AI Recommendations
        intel_data["recommendations"] = self._generate_recommendations(intel_data)

        # 6. Generate AI Attack Strategies (if model available)
        try:
            from src.utils.ai import OffensiveAI
            ai_assistant = OffensiveAI()
            target_summary = self._summarize_target(intel_data)
            attack_strategies = ai_assistant.generate_attack_strategy(target_summary)
            intel_data["ai_attack_strategies"] = attack_strategies
        except Exception as e:
            intel_data["ai_attack_strategies"] = f"AI unavailable: {str(e)}"

        # 6. Store Intelligence
        self.threat_db[intel_id] = intel_data

        # 7. Memory Management: Clean old entries
        if len(self.threat_db) > self.max_entries:
            # Remove oldest entries
            sorted_ids = sorted(self.threat_db.keys(), key=lambda x: self.threat_db[x]['timestamp'])
            for old_id in sorted_ids[:len(self.threat_db) - self.max_entries]:
                del self.threat_db[old_id]

        console.print(f"[bold cyan]THREAT-INTEL:[/] Collected intelligence for {target} (Risk: {intel_data['risk_score']})")
        return intel_id, intel_data

    def _calculate_osint_risk(self, osint_data):
        """Calculate risk score from OSINT data"""
        risk = 0

        # Location-based risk
        if "country" in osint_data:
            high_risk_countries = ["CN", "RU", "IR", "KP", "VN"]
            if osint_data.get("countryCode") in high_risk_countries:
                risk += 30

        # ISP/Org risk
        if "isp" in osint_data:
            isp = osint_data["isp"].lower()
            if any(term in isp for term in ["anonymous", "proxy", "vpn", "tor"]):
                risk += 25

        # Hosting risk
        if osint_data.get("hosting") == True:
            risk += 15

        return risk

    def _calculate_scan_risk(self, scan_results):
        """Calculate risk score from scanning results"""
        risk = 0

        if "open_ports" in scan_results:
            ports = scan_results["open_ports"]
            high_risk_ports = [21, 22, 23, 25, 53, 80, 443, 3306, 5432]  # FTP, SSH, Telnet, SMTP, DNS, HTTP, MySQL, PostgreSQL
            for port in ports:
                if port in high_risk_ports:
                    risk += 10

        if "services" in scan_results:
            services = scan_results["services"]
            if any(svc in str(services).lower() for svc in ["apache", "nginx", "iis", "tomcat"]):
                risk += 5  # Web servers are common targets

        return risk

    def _calculate_vuln_risk(self, vuln_results):
        """Calculate risk score from vulnerability findings"""
        risk = 0

        if "vulnerabilities" in vuln_results:
            vulns = vuln_results["vulnerabilities"]
            for vuln in vulns:
                vuln_type = vuln[0].lower()
                if "sql" in vuln_type:
                    risk += 40
                elif "xss" in vuln_type:
                    risk += 25
                elif "lfi" in vuln_type or "rce" in vuln_type:
                    risk += 50
                else:
                    risk += 10

        if "exposures" in vuln_results:
            exposures = vuln_results["exposures"]
            risk += len(exposures) * 15  # Each exposure adds risk

        return risk

    def _determine_threat_level(self, risk_score):
        """Determine threat level based on risk score"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"

    def _generate_recommendations(self, intel_data):
        """Generate recommendations based on threat level"""
        threat_level = intel_data.get('threat_level', 'LOW')
        risk_score = intel_data.get('risk_score', 0)

        base_recommendations = {
            "CRITICAL": [
                "Immediate isolation of affected systems required",
                "Engage incident response team immediately",
                "Conduct forensic analysis of compromised systems",
                "Review and update incident response procedures",
                "Notify relevant stakeholders and authorities if necessary"
            ],
            "HIGH": [
                "Prioritize patching of critical vulnerabilities",
                "Implement additional monitoring and logging",
                "Conduct security awareness training for staff",
                "Review access controls and permissions",
                "Perform comprehensive security assessment"
            ],
            "MEDIUM": [
                "Schedule regular security updates and patches",
                "Implement multi-factor authentication",
                "Regular security audits and penetration testing",
                "Monitor for unusual network activity",
                "Update security policies and procedures"
            ],
            "LOW": [
                "Maintain regular security updates",
                "Conduct periodic security assessments",
                "Employee security training programs",
                "Regular backup and disaster recovery testing",
                "Monitor security news and threat intelligence"
            ],
            "MINIMAL": [
                "Continue standard security practices",
                "Regular system monitoring",
                "Keep security software updated",
                "Conduct annual security reviews",
                "Stay informed about emerging threats"
            ]
        }

        recommendations = base_recommendations.get(threat_level, base_recommendations["LOW"])

        # Add specific recommendations based on sources
        sources = intel_data.get('sources', {})
        if 'vulnerabilities' in sources and risk_score > 30:
            recommendations.append("Address identified vulnerabilities immediately")
        if 'scanning' in sources:
            recommendations.append("Review network configuration and firewall rules")

        return recommendations[:5]

    def _summarize_target(self, intel_data):
        """Create a concise summary of target for AI analysis"""
        target = intel_data.get('target', 'Unknown')
        threat_level = intel_data.get('threat_level', 'Unknown')
        risk_score = intel_data.get('risk_score', 0)

        summary_parts = [f"Target: {target}, Threat Level: {threat_level}, Risk Score: {risk_score}"]

        sources = intel_data.get('sources', {})

        # Add OSINT info
        if 'osint' in sources:
            osint = sources['osint']
            if 'country' in osint:
                summary_parts.append(f"Location: {osint.get('country', 'Unknown')}")
            if 'isp' in osint:
                summary_parts.append(f"ISP: {osint['isp']}")

        # Add scanning info
        if 'scanning' in sources:
            scanning = sources['scanning']
            if 'open_ports' in scanning:
                ports = scanning['open_ports'][:5]  # Limit to first 5 ports
                summary_parts.append(f"Open ports: {', '.join(map(str, ports))}")
            if 'services' in scanning:
                services = scanning['services'][:3]  # Limit to first 3 services
                summary_parts.append(f"Services: {', '.join(services)}")

        # Add vulnerability info
        if 'vulnerabilities' in sources:
            vulns = sources['vulnerabilities']
            if 'vulnerabilities' in vulns:
                vuln_types = [v[0] for v in vulns['vulnerabilities'][:3]]  # First 3 vuln types
                summary_parts.append(f"Vulnerabilities: {', '.join(vuln_types)}")

        return ". ".join(summary_parts)

    def correlate_threats(self, target):
        """Find correlations between different intelligence sources"""
        correlations = []

        # Find related intelligence for the target
        related_intel = [intel for intel in self.threat_db.values() if intel["target"] == target]

        if len(related_intel) > 1:
            # Analyze trends
            risk_trend = [intel["risk_score"] for intel in related_intel[-5:]]  # Last 5 assessments
            if len(risk_trend) > 1:
                if risk_trend[-1] > risk_trend[0]:
                    correlations.append("Risk score increasing - immediate attention required")
                elif risk_trend[-1] < risk_trend[0]:
                    correlations.append("Risk score decreasing - security improvements effective")

        return correlations

    def generate_threat_report(self, intel_id):
        """Generate comprehensive threat intelligence report"""
        if intel_id not in self.threat_db:
            return None

        intel = self.threat_db[intel_id]

        # Create report table
        table = Table(title=f"🛡️ THREAT INTELLIGENCE REPORT: {intel['target']}", border_style="red")
        table.add_column("Category", style="cyan")
        table.add_column("Details", style="white")

        table.add_row("Assessment Date", intel['timestamp'])
        table.add_row("Risk Score", f"{intel['risk_score']}/100")
        table.add_row("Threat Level", intel['threat_level'])
        table.add_row("Intelligence Sources", ", ".join(intel['sources'].keys()))

        # Add recommendations
        if intel['recommendations']:
            table.add_row("AI Recommendations", "\n".join(f"• {rec}" for rec in intel['recommendations'][:3]))

        # Add AI attack strategies
        if 'ai_attack_strategies' in intel and intel['ai_attack_strategies']:
            strategies = intel['ai_attack_strategies']
            if len(strategies) > 200:
                strategies = strategies[:200] + "..."
            table.add_row("AI Attack Strategies", strategies)

        # Add correlations
        correlations = self.correlate_threats(intel['target'])
        if correlations:
            table.add_row("Threat Correlations", "\n".join(correlations))

        return table

    def export_intelligence(self, filepath=None):
        """Export all collected intelligence to JSON"""
        if not filepath:
            filepath = f"threat_intel_{int(time.time())}.json"

        with open(filepath, 'w') as f:
            json.dump(self.threat_db, f, indent=2, default=str)

        console.print(f"[green]THREAT-INTEL:[/] Exported intelligence to {filepath}")
        return filepath

# Global instance
threat_intel = ThreatIntelligence()