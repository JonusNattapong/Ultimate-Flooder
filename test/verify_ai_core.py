import sys
import os
import time
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.ai_orchestrator import AIOrchestrator
from src.core.attack_manager import AttackManager
from src.core.events import EventBus

def test_ai_orchestration():
    print("\n--- Testing AI Orchestrator ---")
    ai = AIOrchestrator()
    
    # Mock analysis
    print("[+] Analyzing target: example.com")
    profile = ai.analyze_target("example.com")
    print(f"[✓] Profile Created: IP={profile.ip_address}, Services={profile.services}")
    
    # Get suggestions
    print("[+] Getting attack suggestions...")
    suggestions = ai.suggest_attack_strategy(profile)
    for s in suggestions:
        print(f"[!] Suggestion: {s.attack_name} (Conf: {s.confidence*100:.1f}%) - {s.reason}")
    
    return suggestions[0] if suggestions else None

def test_attack_manager_lifecycle(suggestion):
    print("\n--- Testing Attack Manager Lifecycle ---")
    manager = AttackManager()
    bus = EventBus()
    
    # Mock event listener
    def on_event(event):
        print(f"[Event] {event.type}: {event.data}")
    
    bus.subscribe("attack.*", on_event)
    
    if not suggestion:
        print("[!] No suggestion to test")
        return

    print(f"[+] Creating session for: {suggestion.attack_name}")
    session = manager.create_session(
        attack_id=suggestion.attack_id,
        attack_name=suggestion.attack_name,
        target="127.0.0.1",
        config={"threads": 10, "duration": 30}
    )
    
    print(f"[✓] Session ID: {session.id}")
    
    # Since we don't want to actually flood, we'll verify the manager handles the session object
    from src.attacks.l4 import UdpFloodAttack
    attack = UdpFloodAttack("127.0.0.1", port=80, threads=1, duration=5)
    
    print("[+] Starting session...")
    manager.start_session(session.id, attack)
    time.sleep(1)
    
    print("[+] Pausing session...")
    manager.pause_session(session.id)
    time.sleep(1)
    
    print("[+] Resuming session...")
    manager.resume_session(session.id)
    time.sleep(1)
    
    print("[+] Stopping session...")
    manager.stop_session(session.id)
    
    metrics = manager.get_aggregated_metrics()
    print(f"[✓] Final Metrics: {metrics}")

if __name__ == "__main__":
    best_suggestion = test_ai_orchestration()
    test_attack_manager_lifecycle(best_suggestion)
    print("\n[COMPLETE] AI and Manager verification finished.")
