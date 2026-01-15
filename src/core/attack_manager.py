"""
Attack Manager for IP-HUNTER v2.2.0
ระบบจัดการ Attack Sessions แบบ Unified
"""

import uuid
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Type
from enum import Enum

from src.utils.logging import add_system_log
from src.attacks.base import AttackBase, AttackMetrics
from src.core.events import event_bus, Event, EventType, emit_attack_event


class SessionState(Enum):
    """สถานะของ Attack Session"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AttackSession:
    """
    Attack Session - เก็บข้อมูลและสถานะของ Attack แต่ละตัว
    """
    id: str
    attack_id: str  # Menu ID (e.g., "1", "2", "3")
    attack_name: str
    target: str
    attack: Optional[AttackBase] = None
    state: SessionState = SessionState.PENDING
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Optional[AttackMetrics] = None
    ai_suggestions: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    ended_at: Optional[float] = None
    error_message: str = ""
    
    def get_duration(self) -> float:
        """คำนวณระยะเวลาที่ Attack รันแล้ว"""
        if not self.started_at:
            return 0.0
        end = self.ended_at or time.time()
        return end - self.started_at
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """ดึง Metrics summary"""
        if self.metrics:
            return self.metrics.get_summary()
        elif self.attack:
            return self.attack.get_metrics()
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "attack_id": self.attack_id,
            "attack_name": self.attack_name,
            "target": self.target,
            "state": self.state.value,
            "config": self.config,
            "metrics": self.get_metrics_summary(),
            "duration": self.get_duration(),
            "ai_suggestions": self.ai_suggestions,
            "created_at": self.created_at,
            "error": self.error_message
        }


class AttackManager:
    """
    Attack Manager - จัดการ Attack Sessions แบบ Unified
    
    Features:
    - Session-based attack management
    - Multi-vector attack coordination
    - Centralized pause/resume/stop control
    - Real-time metrics aggregation
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.sessions: Dict[str, AttackSession] = {}
        self._active_sessions: List[str] = []
        self._session_lock = threading.Lock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitoring = False
        
        # Subscribe to attack events
        event_bus.subscribe("attack.*", self._handle_attack_event)
        
        self._initialized = True
    
    def create_session(self, attack_id: str, attack_name: str, 
                       target: str, config: Dict[str, Any],
                       ai_suggestions: List[str] = None) -> AttackSession:
        """
        สร้าง Attack Session ใหม่
        
        Args:
            attack_id: Menu ID (e.g., "1" for HTTP Flood)
            attack_name: ชื่อของ Attack
            target: เป้าหมาย (URL หรือ IP)
            config: Configuration parameters
            ai_suggestions: AI suggestions (optional)
        
        Returns:
            AttackSession object
        """
        session_id = str(uuid.uuid4())[:8]
        
        session = AttackSession(
            id=session_id,
            attack_id=attack_id,
            attack_name=attack_name,
            target=target,
            config=config,
            ai_suggestions=ai_suggestions or []
        )
        
        with self._session_lock:
            self.sessions[session_id] = session
        
        # Emit event
        emit_attack_event(
            EventType.ATTACK_CREATED,
            session_id,
            {"attack_name": attack_name, "target": target}
        )
        
        add_system_log(f"[green]MANAGER:[/] Session {session_id} created for {attack_name}")
        return session
    
    def start_session(self, session_id: str, attack: AttackBase) -> bool:
        """
        เริ่มรัน Attack Session
        
        Args:
            session_id: Session ID
            attack: AttackBase instance ที่พร้อมรัน
        
        Returns:
            True if started successfully
        """
        session = self.sessions.get(session_id)
        if not session:
            add_system_log(f"[red]MANAGER-ERROR:[/] Session {session_id} not found")
            return False
        
        if session.state != SessionState.PENDING:
            add_system_log(f"[yellow]MANAGER-WARN:[/] Session {session_id} is not pending")
            return False
        
        session.attack = attack
        session.metrics = attack.metrics
        session.started_at = time.time()
        session.state = SessionState.RUNNING
        
        # Setup callbacks
        original_on_progress = attack.on_progress
        original_on_complete = attack.on_complete
        original_on_error = attack.on_error
        
        def on_progress(state, metrics):
            if original_on_progress:
                original_on_progress(state, metrics)
            emit_attack_event(
                EventType.ATTACK_PROGRESS,
                session_id,
                {"state": state, "metrics": metrics}
            )
        
        def on_complete(metrics):
            session.state = SessionState.COMPLETED
            session.ended_at = time.time()
            with self._session_lock:
                if session_id in self._active_sessions:
                    self._active_sessions.remove(session_id)
            if original_on_complete:
                original_on_complete(metrics)
            emit_attack_event(
                EventType.ATTACK_COMPLETED,
                session_id,
                {"metrics": metrics}
            )
        
        def on_error(error):
            session.state = SessionState.FAILED
            session.error_message = str(error)
            session.ended_at = time.time()
            with self._session_lock:
                if session_id in self._active_sessions:
                    self._active_sessions.remove(session_id)
            if original_on_error:
                original_on_error(error)
            emit_attack_event(
                EventType.ATTACK_FAILED,
                session_id,
                {"error": str(error)}
            )
        
        attack.on_progress = on_progress
        attack.on_complete = on_complete
        attack.on_error = on_error
        
        # Start attack
        success = attack.start()
        
        if success:
            with self._session_lock:
                self._active_sessions.append(session_id)
            emit_attack_event(
                EventType.ATTACK_STARTED,
                session_id,
                {"attack_name": session.attack_name, "target": session.target}
            )
            add_system_log(f"[green]MANAGER:[/] Session {session_id} started")
        else:
            session.state = SessionState.FAILED
            session.error_message = "Failed to start attack"
            add_system_log(f"[red]MANAGER-ERROR:[/] Session {session_id} failed to start")
        
        return success
    
    def pause_session(self, session_id: str) -> bool:
        """Pause an active session"""
        session = self.sessions.get(session_id)
        if not session or not session.attack:
            return False
        
        if session.state == SessionState.RUNNING:
            session.attack.pause()
            session.state = SessionState.PAUSED
            emit_attack_event(EventType.ATTACK_PAUSED, session_id, {})
            add_system_log(f"[yellow]MANAGER:[/] Session {session_id} paused")
            return True
        return False
    
    def resume_session(self, session_id: str) -> bool:
        """Resume a paused session"""
        session = self.sessions.get(session_id)
        if not session or not session.attack:
            return False
        
        if session.state == SessionState.PAUSED:
            session.attack.pause()  # Toggle pause
            session.state = SessionState.RUNNING
            emit_attack_event(EventType.ATTACK_RESUMED, session_id, {})
            add_system_log(f"[green]MANAGER:[/] Session {session_id} resumed")
            return True
        return False
    
    def stop_session(self, session_id: str) -> bool:
        """Stop a session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        if session.attack and session.state in [SessionState.RUNNING, SessionState.PAUSED]:
            session.attack.stop()
            session.state = SessionState.CANCELLED
            session.ended_at = time.time()
            
            with self._session_lock:
                if session_id in self._active_sessions:
                    self._active_sessions.remove(session_id)
            
            add_system_log(f"[yellow]MANAGER:[/] Session {session_id} stopped")
            return True
        return False
    
    def stop_all_sessions(self) -> int:
        """Stop all active sessions"""
        stopped = 0
        for session_id in list(self._active_sessions):
            if self.stop_session(session_id):
                stopped += 1
        add_system_log(f"[yellow]MANAGER:[/] Stopped {stopped} sessions")
        return stopped
    
    def get_session(self, session_id: str) -> Optional[AttackSession]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
    
    def get_active_sessions(self) -> List[AttackSession]:
        """Get all active (running/paused) sessions"""
        return [
            self.sessions[sid] for sid in self._active_sessions
            if sid in self.sessions
        ]
    
    def get_all_sessions(self) -> List[AttackSession]:
        """Get all sessions"""
        return list(self.sessions.values())
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated metrics from all active sessions
        
        Returns:
            Combined metrics dictionary
        """
        total_packets = 0
        total_bytes = 0
        total_failed = 0
        active_count = 0
        
        for session in self.get_active_sessions():
            metrics = session.get_metrics_summary()
            total_packets += metrics.get("packets_sent", 0)
            total_bytes += metrics.get("bytes_sent", 0)
            total_failed += metrics.get("packets_failed", 0)
            active_count += 1
        
        return {
            "active_sessions": active_count,
            "total_packets_sent": total_packets,
            "total_bytes_sent": total_bytes,
            "total_failed": total_failed,
            "total_success_rate": (total_packets / max(1, total_packets + total_failed)) * 100
        }
    
    def run_multi_vector(self, configs: List[Dict[str, Any]], 
                         attack_factory: callable) -> List[AttackSession]:
        """
        รัน Multi-Vector Attack (หลาย attack พร้อมกัน)
        
        Args:
            configs: List of attack configurations
            attack_factory: Function that creates AttackBase from config
        
        Returns:
            List of created AttackSession objects
        """
        sessions = []
        
        for config in configs:
            attack_id = config.get("attack_id", "1")
            attack_name = config.get("attack_name", "Unknown")
            target = config.get("target", "")
            
            # Create session
            session = self.create_session(
                attack_id=attack_id,
                attack_name=attack_name,
                target=target,
                config=config
            )
            
            # Create and start attack
            try:
                attack = attack_factory(config)
                if attack:
                    self.start_session(session.id, attack)
                    sessions.append(session)
            except Exception as e:
                session.state = SessionState.FAILED
                session.error_message = str(e)
                add_system_log(f"[red]MANAGER-ERROR:[/] Multi-vector failed for {attack_name}: {e}")
        
        add_system_log(f"[green]MANAGER:[/] Started {len(sessions)} multi-vector attacks")
        return sessions
    
    def cleanup_sessions(self, max_age: float = 3600) -> int:
        """
        Clean up old completed/failed sessions
        
        Args:
            max_age: Maximum age in seconds (default 1 hour)
        
        Returns:
            Number of sessions cleaned up
        """
        now = time.time()
        to_remove = []
        
        with self._session_lock:
            for session_id, session in self.sessions.items():
                if session.state in [SessionState.COMPLETED, SessionState.FAILED, SessionState.CANCELLED]:
                    if (now - (session.ended_at or session.created_at)) > max_age:
                        to_remove.append(session_id)
            
            for session_id in to_remove:
                del self.sessions[session_id]
        
        if to_remove:
            add_system_log(f"[dim]MANAGER:[/] Cleaned up {len(to_remove)} old sessions")
        
        return len(to_remove)
    
    def _handle_attack_event(self, event: Event) -> None:
        """Handle attack events for internal tracking"""
        # This can be extended for logging, analytics, etc.
        pass


# Global instance
attack_manager = AttackManager()
