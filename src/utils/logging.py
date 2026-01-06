import time

# System logs global state
SYSTEM_LOGS = []

def add_system_log(msg):
    """Add a timestamped log entry to global dashboard"""
    # Force localized timestamp
    timestamp = time.strftime("%H:%M:%S")
    SYSTEM_LOGS.append(f"[bold dim][{timestamp}][/] {msg}")
    # Keep last 50 logs for display cycle
    if len(SYSTEM_LOGS) > 50:
        SYSTEM_LOGS.pop(0)
