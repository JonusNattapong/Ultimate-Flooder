"""
Event System for IP-HUNTER v2.2.0
ระบบ Event กลางสำหรับการสื่อสารระหว่าง Modules
"""

import threading
import time
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty


class EventType(Enum):
    """ประเภทของ Event ในระบบ"""
    # Attack Events
    ATTACK_CREATED = "attack.created"
    ATTACK_STARTED = "attack.started"
    ATTACK_PROGRESS = "attack.progress"
    ATTACK_PAUSED = "attack.paused"
    ATTACK_RESUMED = "attack.resumed"
    ATTACK_COMPLETED = "attack.completed"
    ATTACK_FAILED = "attack.failed"
    
    # AI Events
    AI_ANALYZING = "ai.analyzing"
    AI_SUGGESTION = "ai.suggestion"
    AI_WARNING = "ai.warning"
    AI_ADAPTIVE_ADJUST = "ai.adaptive_adjust"
    
    # Target Events
    TARGET_ANALYZED = "target.analyzed"
    TARGET_WAF_DETECTED = "target.waf_detected"
    TARGET_RESPONDING = "target.responding"
    TARGET_DOWN = "target.down"
    
    # System Events
    SYSTEM_WARNING = "system.warning"
    SYSTEM_ERROR = "system.error"
    SYSTEM_RESOURCE_HIGH = "system.resource_high"
    
    # Session Events
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    SESSION_ENDED = "session.ended"


@dataclass
class Event:
    """Event object ที่ส่งผ่าน EventBus"""
    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    timestamp: float = field(default_factory=time.time)
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp,
            "session_id": self.session_id
        }


class EventBus:
    """
    Event Bus - ระบบ Publish/Subscribe สำหรับการสื่อสารระหว่าง Modules
    
    Features:
    - Subscribe to specific event types
    - Wildcard subscriptions (e.g., "attack.*")
    - Async event processing with queue
    - Event history for debugging
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
            
        self._subscribers: Dict[str, List[Callable]] = {}
        self._wildcard_subscribers: Dict[str, List[Callable]] = {}
        self._event_queue: Queue = Queue()
        self._history: List[Event] = []
        self._max_history = 100
        self._processing = False
        self._processor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        self._initialized = True
    
    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type
        
        Args:
            event_type: Event type string (e.g., "attack.started") or wildcard (e.g., "attack.*")
            handler: Callback function that receives Event object
        """
        with self._lock:
            if "*" in event_type:
                # Wildcard subscription
                prefix = event_type.replace("*", "")
                if prefix not in self._wildcard_subscribers:
                    self._wildcard_subscribers[prefix] = []
                self._wildcard_subscribers[prefix].append(handler)
            else:
                if event_type not in self._subscribers:
                    self._subscribers[event_type] = []
                self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        """
        Unsubscribe from an event type
        
        Returns:
            True if handler was found and removed
        """
        with self._lock:
            if "*" in event_type:
                prefix = event_type.replace("*", "")
                if prefix in self._wildcard_subscribers:
                    try:
                        self._wildcard_subscribers[prefix].remove(handler)
                        return True
                    except ValueError:
                        return False
            else:
                if event_type in self._subscribers:
                    try:
                        self._subscribers[event_type].remove(handler)
                        return True
                    except ValueError:
                        return False
        return False
    
    def emit(self, event: Event) -> None:
        """
        Emit an event (synchronous, immediate delivery)
        
        Args:
            event: Event object to emit
        """
        # Add to history
        with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history.pop(0)
        
        event_type_str = event.type.value
        
        # Notify exact subscribers
        handlers = self._subscribers.get(event_type_str, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                from src.utils.logging import add_system_log
                add_system_log(f"[red]EVENT-ERROR:[/] Handler failed for {event_type_str}: {e}")
        
        # Notify wildcard subscribers
        for prefix, wildcard_handlers in self._wildcard_subscribers.items():
            if event_type_str.startswith(prefix):
                for handler in wildcard_handlers:
                    try:
                        handler(event)
                    except Exception as e:
                        from src.utils.logging import add_system_log
                        add_system_log(f"[red]EVENT-ERROR:[/] Wildcard handler failed: {e}")
    
    def emit_async(self, event: Event) -> None:
        """
        Emit an event asynchronously (queued for processing)
        
        Args:
            event: Event object to emit
        """
        self._event_queue.put(event)
        
        # Start processor if not running
        if not self._processing:
            self._start_processor()
    
    def _start_processor(self) -> None:
        """Start the async event processor thread"""
        if self._processor_thread and self._processor_thread.is_alive():
            return
            
        self._processing = True
        self._processor_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._processor_thread.start()
    
    def _process_queue(self) -> None:
        """Process events from the queue"""
        while self._processing:
            try:
                event = self._event_queue.get(timeout=1.0)
                self.emit(event)
            except Empty:
                # Check if we should stop
                if self._event_queue.empty():
                    self._processing = False
                    break
    
    def stop_processor(self) -> None:
        """Stop the async event processor"""
        self._processing = False
        if self._processor_thread:
            self._processor_thread.join(timeout=2.0)
    
    def get_history(self, event_type: Optional[str] = None, 
                    limit: int = 50) -> List[Event]:
        """
        Get event history
        
        Args:
            event_type: Filter by event type (optional)
            limit: Maximum events to return
        
        Returns:
            List of Event objects
        """
        with self._lock:
            if event_type:
                filtered = [e for e in self._history if e.type.value == event_type]
                return filtered[-limit:]
            return self._history[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history"""
        with self._lock:
            self._history.clear()
    
    def get_subscriber_count(self, event_type: Optional[str] = None) -> int:
        """Get number of subscribers"""
        if event_type:
            return len(self._subscribers.get(event_type, []))
        return sum(len(handlers) for handlers in self._subscribers.values())


# Helper functions for easy event emission
def emit_attack_event(event_type: EventType, session_id: str, 
                      data: Dict[str, Any], source: str = "dispatcher") -> None:
    """Helper to emit attack-related events"""
    event = Event(
        type=event_type,
        data=data,
        source=source,
        session_id=session_id
    )
    event_bus.emit(event)


def emit_ai_event(event_type: EventType, data: Dict[str, Any],
                  session_id: Optional[str] = None) -> None:
    """Helper to emit AI-related events"""
    event = Event(
        type=event_type,
        data=data,
        source="ai_orchestrator",
        session_id=session_id
    )
    event_bus.emit(event)


def emit_system_event(event_type: EventType, data: Dict[str, Any]) -> None:
    """Helper to emit system-related events"""
    event = Event(
        type=event_type,
        data=data,
        source="system"
    )
    event_bus.emit(event)


# Global instance
event_bus = EventBus()
