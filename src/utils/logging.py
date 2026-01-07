import time

# System logs global state
SYSTEM_LOGS = []

def add_system_log(msg):
    """Add a timestamped log entry to global dashboard"""
    from rich.console import Console
    console = Console()
    
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[bold dim][{timestamp}][/] {msg}"
    SYSTEM_LOGS.append(formatted_msg)
    
    # Also print to console for real-time feedback during tests
    console.print(formatted_msg)
    
    if len(SYSTEM_LOGS) > 50:
        SYSTEM_LOGS.pop(0)
