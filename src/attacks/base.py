"""
Attack Base Classes for IP-HUNTER
Unified interface for all attack vectors with consistent lifecycle management.
"""

import abc
import threading
import time
from typing import Dict, Any, Optional, Callable
from src.utils.logging import add_system_log
from src.security import increment_thread_counter, decrement_thread_counter, increment_socket_counter, decrement_socket_counter

class AttackMetrics:
    """Standardized metrics tracking for all attacks"""

    def __init__(self):
        self.packets_sent = 0
        self.bytes_sent = 0
        self.packets_failed = 0
        self.active_connections = 0
        self.start_time = time.time()
        self.end_time = None
        self.peak_pps = 0
        self.peak_bps = 0
        self._lock = threading.Lock()

    def update(self, packets=0, bytes_sent=0, failed=0, connections=0):
        """Thread-safe metrics update"""
        with self._lock:
            self.packets_sent += packets
            self.bytes_sent += bytes_sent
            self.packets_failed += failed
            if connections > 0:
                self.active_connections = connections

            # Update peaks
            elapsed = max(1, time.time() - self.start_time)
            current_pps = self.packets_sent / elapsed
            current_bps = self.bytes_sent / elapsed / 1024 / 1024  # MB/s

            self.peak_pps = max(self.peak_pps, current_pps)
            self.peak_bps = max(self.peak_bps, current_bps)

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        elapsed = time.time() - self.start_time
        total_packets = self.packets_sent + self.packets_failed
        success_rate = (self.packets_sent / max(1, total_packets)) * 100

        return {
            "packets_sent": self.packets_sent,
            "bytes_sent": self.bytes_sent,
            "packets_failed": self.packets_failed,
            "active_connections": self.active_connections,
            "duration": elapsed,
            "pps": self.packets_sent / max(1, elapsed),
            "bps_mb": self.bytes_sent / max(1, elapsed) / 1024 / 1024,
            "success_rate": success_rate,
            "peak_pps": self.peak_pps,
            "peak_bps": self.peak_bps
        }

class AttackBase(abc.ABC):
    """
    Abstract base class for all attack vectors.
    Provides unified interface and lifecycle management.
    """

    def __init__(self, target: str, port: int = 80, threads: int = 10, duration: int = 60):
        self.target = target
        self.port = port
        self.threads = threads
        self.duration = duration

        # Attack state
        self.is_running = False
        self.is_paused = False
        self.should_stop = False

        # Threading
        self.worker_threads = []
        self.control_thread = None

        # Metrics
        self.metrics = AttackMetrics()

        # Callbacks
        self.on_progress: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

        # Attack-specific attributes (to be set by subclasses)
        self.attack_name = "Unknown Attack"
        self.category = "Unknown"

    @abc.abstractmethod
    def _setup_attack(self) -> bool:
        """Setup attack-specific parameters and validation"""
        pass

    @abc.abstractmethod
    def _create_worker(self) -> Callable:
        """Create worker function for individual attack threads"""
        pass

    def start(self) -> bool:
        """Start the attack with unified lifecycle"""
        if self.is_running:
            add_system_log(f"[yellow]Attack {self.attack_name} is already running[/yellow]")
            return False

        add_system_log(f"[green]Starting {self.attack_name} against {self.target}:{self.port}[/green]")

        # Setup attack
        if not self._setup_attack():
            add_system_log(f"[red]Failed to setup {self.attack_name}[/red]")
            return False

        # Reset state
        self.is_running = True
        self.is_paused = False
        self.should_stop = False
        self.metrics = AttackMetrics()

        # Start control thread
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()

        # Start worker threads
        for i in range(self.threads):
            worker = threading.Thread(target=self._worker_wrapper, daemon=True)
            worker.start()
            self.worker_threads.append(worker)
            increment_thread_counter()

        if self.on_progress:
            self.on_progress("started", self.metrics.get_summary())

        return True

    def stop(self) -> bool:
        """Stop the attack gracefully"""
        if not self.is_running:
            return False

        add_system_log(f"[yellow]Stopping {self.attack_name}...[/yellow]")
        self.should_stop = True

        # Wait for threads to finish
        for thread in self.worker_threads:
            thread.join(timeout=2.0)

        # Cleanup
        self._cleanup()
        self.is_running = False
        self.metrics.end_time = time.time()

        # Update global counters
        for _ in self.worker_threads:
            decrement_thread_counter()
        for _ in range(self.metrics.active_connections):
            decrement_socket_counter()

        add_system_log(f"[green]{self.attack_name} stopped. Sent {self.metrics.packets_sent:,} packets[/green]")

        if self.on_complete:
            self.on_complete(self.metrics.get_summary())

        return True

    def pause(self) -> bool:
        """Pause/resume the attack"""
        if not self.is_running:
            return False

        self.is_paused = not self.is_paused
        state = "paused" if self.is_paused else "resumed"
        add_system_log(f"[yellow]{self.attack_name} {state}[/yellow]")

        if self.on_progress:
            self.on_progress(state, self.metrics.get_summary())

        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get current attack metrics"""
        return self.metrics.get_summary()

    def _control_loop(self):
        """Main control loop managing attack lifecycle"""
        start_time = time.time()

        while not self.should_stop and (time.time() - start_time) < self.duration:
            if not self.is_paused:
                # Update progress
                if self.on_progress and int(time.time()) % 2 == 0:  # Update every 2 seconds
                    self.on_progress("running", self.metrics.get_summary())

            time.sleep(1)

        # Auto-stop when duration reached
        if not self.should_stop:
            self.stop()

    def _worker_wrapper(self):
        """Wrapper for worker threads with error handling"""
        try:
            worker_func = self._create_worker()
            worker_func()
        except Exception as e:
            add_system_log(f"[red]Worker error in {self.attack_name}: {e}[/red]")
            if self.on_error:
                self.on_error(str(e))

    def _cleanup(self):
        """Cleanup attack-specific resources"""
        # Override in subclasses for specific cleanup
        pass

    def __str__(self):
        return f"{self.attack_name}(target={self.target}, threads={self.threads}, duration={self.duration}s)"