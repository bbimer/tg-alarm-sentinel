import json
import os
import time
from typing import Dict, Any, List
import config

DEFAULT_STATE: Dict[str, Any] = {
    "is_sleeping": True,          # True = Sleeping (Alerts ON), False = Awake (Alerts OFF)
    "auto_wake_until": 0,         # Timestamp until which user is temporarily awake
    "last_trigger_time": "Never",
    "total_alerts_count": 0,
    "targets": ["@example_signal_bot"] # Generic placeholder for public portfolio
}

def load_state() -> Dict[str, Any]:
    if not os.path.exists(config.STATE_FILE_PATH):
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE.copy()
    try:
        with open(config.STATE_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "targets" not in data or not isinstance(data["targets"], list):
                data["targets"] = ["@example_signal_bot"]
            auto_wake = data.get("auto_wake_until", 0)
            if auto_wake > 0 and time.time() > auto_wake:
                data["auto_wake_until"] = 0
                data["is_sleeping"] = True # Automatically re-enable sleep mode
                save_state(data)
            return data
    except Exception as e:
        print(f"[!] Error loading state.json: {e}")
        return DEFAULT_STATE.copy()

def save_state(state_data: Dict[str, Any]) -> None:
    try:
        with open(config.STATE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error saving state.json: {e}")

def set_sleeping(sleeping: bool, wake_hours: float = 0) -> Dict[str, Any]:
    state = load_state()
    state["is_sleeping"] = sleeping
    if not sleeping and wake_hours > 0:
        state["auto_wake_until"] = time.time() + (wake_hours * 3600)
    else:
        state["auto_wake_until"] = 0
    save_state(state)
    return state

def record_alert() -> Dict[str, Any]:
    state = load_state()
    state["total_alerts_count"] = state.get("total_alerts_count", 0) + 1
    state["last_trigger_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)
    return state

def get_targets() -> List[str]:
    state = load_state()
    return state.get("targets", [])

def add_target(target: str) -> bool:
    clean = target.strip()
    if not clean:
        return False
    state = load_state()
    targets = state.get("targets", [])
    if clean.lower() not in [t.lower() for t in targets]:
        targets.append(clean)
        state["targets"] = targets
        save_state(state)
        return True
    return False

def remove_target(target: str) -> bool:
    state = load_state()
    targets = state.get("targets", [])
    new_targets = [t for t in targets if t.lower() != target.strip().lower()]
    if len(new_targets) != len(targets):
        state["targets"] = new_targets
        save_state(state)
        return True
    return False
