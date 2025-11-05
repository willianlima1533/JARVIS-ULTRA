#!/usr/bin/env python3
# engineer/metrics.py
"""
Sistema de coleta e armazenamento de métricas.
"""
import json
import os
import time
from typing import Dict, List
from datetime import datetime

METRICS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "metrics.json"))

def ensure_metrics():
    """Garante que o arquivo de métricas existe."""
    os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
    
    if not os.path.exists(METRICS_FILE):
        initial_data = {
            "runs": [],
            "patches": [],
            "projects": {},
            "system": {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "total_runs": 0,
                "total_patches": 0,
                "success_rate": 0.0
            }
        }
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)

def load_metrics() -> Dict:
    """
    Carrega as métricas do arquivo.
    
    Returns:
        Dicionário com as métricas
    """
    ensure_metrics()
    
    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_metrics(metrics: Dict):
    """
    Salva as métricas no arquivo.
    
    Args:
        metrics: Dicionário com as métricas
    """
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

def record_run(run_info: Dict):
    """
    Registra uma execução do auto-engineer.
    
    Args:
        run_info: Informações da execução
    """
    metrics = load_metrics()
    
    run_record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ts": time.time(),
        **run_info
    }
    
    metrics["runs"].append(run_record)
    metrics["system"]["total_runs"] += 1
    
    # Calcular taxa de sucesso
    successful_runs = sum(1 for r in metrics["runs"] if r.get("success", False))
    metrics["system"]["success_rate"] = successful_runs / len(metrics["runs"]) if metrics["runs"] else 0.0
    
    save_metrics(metrics)
    print(f"[METRICS] Execução registrada: {run_info.get('success', False)}")

def record_patch(patch_info: Dict):
    """
    Registra um patch aplicado.
    
    Args:
        patch_info: Informações do patch
    """
    metrics = load_metrics()
    
    patch_record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ts": time.time(),
        **patch_info
    }
    
    metrics["patches"].append(patch_record)
    metrics["system"]["total_patches"] += 1
    
    save_metrics(metrics)
    print(f"[METRICS] Patch registrado: {patch_info.get('file', 'unknown')}")

def record_project_metric(project_path: str, metric_name: str, value: any):
    """
    Registra uma métrica específica de um projeto.
    
    Args:
        project_path: Caminho do projeto
        metric_name: Nome da métrica
        value: Valor da métrica
    """
    metrics = load_metrics()
    
    if project_path not in metrics["projects"]:
        metrics["projects"][project_path] = {
            "created_at": datetime.utcnow().isoformat() + "Z",
            "metrics": {}
        }
    
    metrics["projects"][project_path]["metrics"][metric_name] = {
        "value": value,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    save_metrics(metrics)
    print(f"[METRICS] Métrica registrada para {project_path}: {metric_name}={value}")

def get_summary() -> Dict:
    """
    Retorna um resumo das métricas.
    
    Returns:
        Dicionário com o resumo
    """
    metrics = load_metrics()
    
    recent_runs = metrics["runs"][-10:] if metrics["runs"] else []
    recent_patches = metrics["patches"][-10:] if metrics["patches"] else []
    
    summary = {
        "system": metrics["system"],
        "recent_runs": len(recent_runs),
        "recent_patches": len(recent_patches),
        "total_projects": len(metrics["projects"]),
        "last_run": recent_runs[-1] if recent_runs else None,
        "last_patch": recent_patches[-1] if recent_patches else None
    }
    
    return summary

if __name__ == "__main__":
    # Teste do sistema de métricas
    print("Testando sistema de métricas...")
    
    # Registrar uma execução
    record_run({
        "success": True,
        "details": {"test": "value"},
        "duration": 1.5
    })
    
    # Registrar um patch
    record_patch({
        "file": "test.py",
        "method": "mock",
        "confidence": 0.8,
        "applied": True
    })
    
    # Registrar métrica de projeto
    record_project_metric("/home/test/project", "lines_of_code", 1000)
    
    # Obter resumo
    summary = get_summary()
    print("\nResumo das métricas:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

