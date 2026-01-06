import os
from src.utils import add_system_log

def load_risk_patterns():
    """Load AI vulnerability patterns from txt/risk_patterns.txt"""
    patterns = {}
    path = "txt/risk_patterns.txt"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line:
                        parts = line.strip().split("|")
                        if len(parts) >= 3:
                            patterns[parts[0]] = (parts[1], parts[2])
        except Exception as e:
            add_system_log(f"[bold red]ERROR:[/] Failed to load risk patterns: {e}")
    
    if not patterns:
        patterns = {
            r"AI_KEY|OPENAI_API_KEY": ("CRITICAL", "OpenAI API Token"),
            r"AKIA[0-9A-Z]{16}": ("CRITICAL", "AWS Access Key"),
            r"PRIVATE KEY|BEGIN RSA": ("FATAL", "Private Key")
        }
    return patterns
