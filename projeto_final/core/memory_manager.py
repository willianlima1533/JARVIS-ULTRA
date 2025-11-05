#!/usr/bin/env python3
# core/memory_manager.py
"""
Gerenciador de memória persistente do J.A.R.V.I.S.
Armazena preferências, histórico de ações e aprendizados.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any

# Arquivos de persistência
MEMORY_FILE = os.path.expanduser("~/.jarvis_memory.json")
ACTIVITY_LOG = os.path.expanduser("~/.jarvis_activity.log")

def ensure_memory():
    """Garante que os arquivos de memória existem."""
    if not os.path.exists(MEMORY_FILE):
        initial_memory = {
            "preferences": {
                "aggressiveness": "high",  # low, medium, high
                "voice_confirmation": True,
                "auto_backup": True,
                "language": "pt-BR"
            },
            "events": [],
            "learned_patterns": {},
            "project_history": {}
        }
        save_memory(initial_memory)
    
    if not os.path.exists(ACTIVITY_LOG):
        with open(ACTIVITY_LOG, "w", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] J.A.R.V.I.S Activity Log iniciado\n")

def load_memory() -> Dict:
    """Carrega a memória do J.A.R.V.I.S."""
    ensure_memory()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory: Dict):
    """Salva a memória do J.A.R.V.I.S."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def get_preference(key: str, default: Any = None) -> Any:
    """Obtém uma preferência."""
    memory = load_memory()
    return memory.get("preferences", {}).get(key, default)

def set_preference(key: str, value: Any):
    """Define uma preferência."""
    memory = load_memory()
    memory["preferences"][key] = value
    save_memory(memory)
    log_activity(f"Preferência alterada: {key} = {value}")

def log_event(event_type: str, data: Dict):
    """Registra um evento na memória."""
    memory = load_memory()
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "data": data
    }
    memory["events"].append(event)
    
    # Manter apenas os últimos 1000 eventos
    if len(memory["events"]) > 1000:
        memory["events"] = memory["events"][-1000:]
    
    save_memory(memory)

def log_activity(message: str, level: str = "INFO"):
    """Registra uma atividade no log humanamente legível."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}\n"
    
    with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
        f.write(log_line)
    
    print(log_line.strip())

def record_project_action(project_path: str, action: str, details: Dict):
    """Registra uma ação realizada em um projeto."""
    memory = load_memory()
    
    if project_path not in memory["project_history"]:
        memory["project_history"][project_path] = {
            "first_seen": datetime.now().isoformat(),
            "actions": []
        }
    
    memory["project_history"][project_path]["actions"].append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })
    
    save_memory(memory)
    log_activity(f"Projeto {os.path.basename(project_path)}: {action}")

def learn_pattern(pattern_name: str, pattern_data: Dict):
    """Aprende um novo padrão."""
    memory = load_memory()
    
    if pattern_name not in memory["learned_patterns"]:
        memory["learned_patterns"][pattern_name] = {
            "first_learned": datetime.now().isoformat(),
            "occurrences": 0,
            "data": pattern_data
        }
    
    memory["learned_patterns"][pattern_name]["occurrences"] += 1
    memory["learned_patterns"][pattern_name]["last_seen"] = datetime.now().isoformat()
    
    save_memory(memory)
    log_activity(f"Padrão aprendido: {pattern_name}")

def get_recent_events(count: int = 10, event_type: str = None) -> List[Dict]:
    """Obtém eventos recentes."""
    memory = load_memory()
    events = memory.get("events", [])
    
    if event_type:
        events = [e for e in events if e.get("type") == event_type]
    
    return events[-count:]

def get_project_history(project_path: str) -> Dict:
    """Obtém o histórico de um projeto."""
    memory = load_memory()
    return memory.get("project_history", {}).get(project_path, {})

if __name__ == "__main__":
    # Teste do memory manager
    print("Testando Memory Manager...")
    
    ensure_memory()
    
    # Testar preferências
    set_preference("test_pref", "test_value")
    print(f"Preferência test_pref: {get_preference('test_pref')}")
    
    # Testar log de atividade
    log_activity("Teste de atividade", "DEBUG")
    
    # Testar evento
    log_event("test_event", {"key": "value"})
    
    # Testar ação de projeto
    record_project_action("/test/project", "created", {"type": "python"})
    
    # Testar aprendizado de padrão
    learn_pattern("test_pattern", {"description": "Padrão de teste"})
    
    print("\nEventos recentes:")
    for event in get_recent_events(5):
        print(f"  {event['timestamp']}: {event['type']}")
    
    print("\nMemory Manager testado com sucesso!")

