import asyncio
import time
import threading
from rich.console import Console
from rich.table import Table
from rich.live import Live

console = Console()

# Global state dictionary for reliable traffic tracking
GLOBAL_STATS = {
    "request_count": 0,
    "total_bytes": 0,
    "start_time": time.time(),
    "last_check_time": time.time(),
    "last_check_count": 0,
    "rps": 0
}

async def handle_request(reader, writer):
    """Zero-overhead request handler for extreme RPS benchmarks"""
    global GLOBAL_STATS
    try:
        # Just count the packet arrival without heavy header parsing
        data = await reader.read(256) 
        GLOBAL_STATS["request_count"] += 1
        GLOBAL_STATS["total_bytes"] += len(data)
        
        # Immediate minimal HTTP response
        writer.write(b"HTTP/1.1 200 OK\r\nConnection: close\r\n\r\nOK")
        await writer.drain()
    except:
        pass
    finally:
        try:
            writer.close()
        except:
            pass

async def run_async_server(port):
    server = await asyncio.start_server(handle_request, "127.0.0.1", port)
    console.print(f"[bold green][+][/] Enterprise Async Sandbox Listening on port {port}")
    async with server:
        await server.serve_forever()

def rps_calculator():
    global GLOBAL_STATS
    while True:
        now = time.time()
        elapsed = now - GLOBAL_STATS["last_check_time"]
        if elapsed >= 1.0:
            current_count = GLOBAL_STATS["request_count"]
            GLOBAL_STATS["rps"] = int((current_count - GLOBAL_STATS["last_check_count"]) / elapsed)
            GLOBAL_STATS["last_check_count"] = current_count
            GLOBAL_STATS["last_check_time"] = now
        time.sleep(1)

def display_monitor():
    threading.Thread(target=rps_calculator, daemon=True).start()
    
    with Live(refresh_per_second=4) as live:
        while True:
            table = Table(title="[bold cyan]🛰️ ENTERPRISE-GRADE SANDBOX MONITOR[/]")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            uptime = int(time.time() - GLOBAL_STATS["start_time"])
            table.add_row("Status", "[bold green]ONLINE (ASYNC ENGINE)[/]")
            table.add_row("Uptime", f"{uptime}s")
            table.add_row("Counted Requests", f"{GLOBAL_STATS['request_count']:,}")
            table.add_row("Current RPS", f"[bold yellow]{GLOBAL_STATS['rps']}[/]")
            table.add_row("Data Received", f"{GLOBAL_STATS['total_bytes'] / 1024 / 1024:.2f} MB")
            
            live.update(table)
            time.sleep(0.25)

if __name__ == "__main__":
    PORT = 8082
    def start_loop():
        asyncio.run(run_async_server(PORT))
    
    threading.Thread(target=start_loop, daemon=True).start()
    try:
        display_monitor()
    except KeyboardInterrupt:
        console.print("\n[bold red][!] Sandbox Terminated.[/]")
