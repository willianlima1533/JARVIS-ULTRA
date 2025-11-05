
#!/usr/bin/env python3
# core/memory_manager.py
"""
Gerenciador de memória persistente do J.A.R.V.I.S.
Armazena preferências, histórico de ações, aprendizados e memória de longo prazo.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Arquivos de persistência
MEMORY_FILE = os.path.expanduser("~/.jarvis_memory.json")
ACTIVITY_LOG = os.path.expanduser("~/.jarvis_activity.log")

def ensure_memory():
    """Garante que os arquivos de memória existem e inicializa-os se não existirem."""
    if not os.path.exists(MEMORY_FILE):
        initial_memory = {
            "preferences": {
                "aggressiveness": "high",  # low, medium, high
                "voice_confirmation": True,
                "auto_backup": True,
                "language": "pt-BR",
                "default_city": "São Paulo",
                "last_known_latitude": -23.5505,
                "last_known_longitude": -46.6333,
            },
            "working_memory": [], # Para contexto de curto prazo da conversa/tarefa atual
            "episodic_memory": [], # Eventos e experiências passadas
            "semantic_memory": {}, # Conhecimento geral, fatos, relações
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
    """Registra um evento na memória episódica e de trabalho."""
    memory = load_memory()
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "data": data
    }
    memory["episodic_memory"].append(event)
    memory["working_memory"].append(event) # Adiciona também à memória de trabalho
    
    # Manter apenas os últimos 1000 eventos episódicos
    if len(memory["episodic_memory"]) > 1000:
        memory["episodic_memory"] = memory["episodic_memory"][-1000:]

    # Manter apenas os últimos 10 eventos na memória de trabalho para contexto imediato
    if len(memory["working_memory"]) > 10:
        memory["working_memory"] = memory["working_memory"][-10:]
    
    save_memory(memory)
    log_activity(f"Evento registrado: {event_type}")

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
    """Aprende um novo padrão ou atualiza um existente."""
    memory = load_memory()
    
    if pattern_name not in memory["learned_patterns"]:
        memory["learned_patterns"][pattern_name] = {
            "first_learned": datetime.now().isoformat(),
            "occurrences": 0,
            "data": pattern_data,
            "relevance_score": 1.0 # Score de relevância inicial
        }
    
    memory["learned_patterns"][pattern_name]["occurrences"] += 1
    memory["learned_patterns"][pattern_name]["last_seen"] = datetime.now().isoformat()
    # Lógica para ajustar relevance_score com base no uso ou sucesso
    
    save_memory(memory)
    log_activity(f"Padrão aprendido/atualizado: {pattern_name}")

def store_semantic_knowledge(concept: str, knowledge: Any):
    """
    Armazena conhecimento semântico (fatos, definições, relações).
    Pode ser um simples dicionário ou integrar com um banco de dados de grafo.
    """
    memory = load_memory()
    memory["semantic_memory"][concept] = {
        "data": knowledge,
        "last_updated": datetime.now().isoformat()
    }
    save_memory(memory)
    log_activity(f"Conhecimento semântico armazenado: {concept}")

def retrieve_semantic_knowledge(concept: str) -> Optional[Any]:
    """
    Recupera conhecimento semântico.
    """
    memory = load_memory()
    return memory.get("semantic_memory", {}).get(concept, None)

def get_working_memory() -> List[Dict]:
    """
    Retorna o conteúdo atual da memória de trabalho (eventos recentes).
    """
    memory = load_memory()
    return memory.get("working_memory", [])

def clear_working_memory():
    """
    Limpa a memória de trabalho.
    """
    memory = load_memory()
    memory["working_memory"] = []
    save_memory(memory)
    log_activity("Memória de trabalho limpa.")

if __name__ == "__main__":
    # Teste do memory manager
    print("Testando Memory Manager...")
    
    ensure_memory()
    
    # Testar preferências
    set_preference("test_pref", "test_value")
    print(f"Preferência test_pref: {get_preference('test_pref')}")
    set_preference("default_city", "Curitiba")
    print(f"Preferência default_city: {get_preference('default_city')}")

    # Testar log de atividade
    log_activity("Teste de atividade", "DEBUG")
    
    # Testar evento
    log_event("test_event", {"key": "value"})
    
    # Testar ação de projeto
    record_project_action("/test/project", "created", {"type": "python"})
    
    # Testar aprendizado de padrão
    learn_pattern("test_pattern", {"description": "Padrão de teste"})
    
    # Testar memória semântica
    store_semantic_knowledge("Python", "Linguagem de programação de alto nível.")
    print(f"Conhecimento sobre Python: {retrieve_semantic_knowledge('Python')}")

    print("\nMemória de trabalho (últimos eventos):")
    for event in get_working_memory():
        print(f"  {event['timestamp']}: {event['type']}")

    print("\nEventos episódicos recentes:")
    for event in get_recent_events(5):
        print(f"  {event['timestamp']}: {event['type']}")
    
    print("\nMemory Manager testado com sucesso!")
    clear_working_memory()
    print("Memória de trabalho limpa.")


