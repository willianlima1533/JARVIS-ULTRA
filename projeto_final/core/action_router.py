#!/usr/bin/env python3
# core/action_router.py
"""
Roteador de ações do J.A.R.V.I.S.
Processa comandos de voz e executa ações correspondentes.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import project_scan, env_manager, memory_manager
from core.voice_assistant import notify_tts

def scan_downloads_and_import(downloads_path: str = None) -> Dict[str, Any]:
    """
    Escaneia a pasta de downloads em busca de ZIPs e os importa.
    
    Args:
        downloads_path: Caminho da pasta de downloads
        
    Returns:
        Dicionário com resultados da operação
    """
    if downloads_path is None:
        downloads_path = os.path.expanduser("~/storage/downloads")
    
    memory_manager.log_activity(f"Escaneando downloads em: {downloads_path}")
    
    # Verificar se o diretório existe
    if not os.path.exists(downloads_path):
        message = f"Diretório de downloads não encontrado: {downloads_path}"
        memory_manager.log_activity(message, "ERROR")
        notify_tts(f"Erro: pasta de downloads não encontrada")
        return {"success": False, "error": message}
    
    # Procurar arquivos ZIP
    zip_files = []
    for file in os.listdir(downloads_path):
        if file.lower().endswith('.zip'):
            zip_files.append(os.path.join(downloads_path, file))
    
    if not zip_files:
        message = "Nenhum arquivo ZIP encontrado em downloads"
        memory_manager.log_activity(message)
        notify_tts("Nenhum arquivo ZIP encontrado")
        return {"success": True, "imported": 0, "message": message}
    
    # Importar cada ZIP
    imported = []
    failed = []
    
    for zip_path in zip_files:
        try:
            # Extrair para a pasta de projetos
            project_name = os.path.splitext(os.path.basename(zip_path))[0]
            extract_dir = os.path.expanduser(f"~/projects/{project_name}")
            
            memory_manager.log_activity(f"Extraindo: {os.path.basename(zip_path)}")
            
            if project_scan.extract_zip(zip_path, extract_dir):
                imported.append(project_name)
                
                # Detectar tipo de projeto
                project_type = project_scan.detect_project_type(extract_dir)
                
                # Registrar na memória
                memory_manager.record_project_action(
                    extract_dir,
                    "imported_from_zip",
                    {"source": zip_path, "type": project_type}
                )
                
                # Configurar ambiente se for um projeto reconhecido
                if project_type != "unknown":
                    memory_manager.log_activity(f"Configurando ambiente {project_type} para {project_name}")
                    success, msg = env_manager.setup_project({
                        "path": extract_dir,
                        "type": project_type
                    })
                    if not success:
                        memory_manager.log_activity(f"Falha ao configurar: {msg}", "WARNING")
            else:
                failed.append(os.path.basename(zip_path))
        
        except Exception as e:
            memory_manager.log_activity(f"Erro ao importar {os.path.basename(zip_path)}: {e}", "ERROR")
            failed.append(os.path.basename(zip_path))
    
    # Notificar resultado
    if imported:
        message = f"Importados {len(imported)} projetos: {', '.join(imported)}"
        memory_manager.log_activity(message)
        notify_tts(f"Importei {len(imported)} projetos com sucesso")
    
    if failed:
        message = f"Falha ao importar: {', '.join(failed)}"
        memory_manager.log_activity(message, "WARNING")
    
    return {
        "success": True,
        "imported": len(imported),
        "failed": len(failed),
        "projects": imported
    }

def scan_projects(scan_dirs: list = None) -> Dict[str, Any]:
    """
    Escaneia diretórios em busca de projetos.
    
    Args:
        scan_dirs: Lista de diretórios para escanear
        
    Returns:
        Dicionário com resultados
    """
    if scan_dirs is None:
        scan_dirs = [
            os.path.expanduser("~/storage/downloads"),
            os.path.expanduser("~/projects")
        ]
    
    memory_manager.log_activity("Escaneando projetos...")
    notify_tts("Escaneando projetos")
    
    projects = project_scan.scan_projects(scan_dirs)
    
    message = f"Encontrados {len(projects)} projetos"
    memory_manager.log_activity(message)
    notify_tts(message)
    
    return {"success": True, "count": len(projects), "projects": projects}

def setup_environments() -> Dict[str, Any]:
    """
    Configura ambientes para todos os projetos detectados.
    
    Returns:
        Dicionário com resultados
    """
    memory_manager.log_activity("Configurando ambientes...")
    notify_tts("Configurando ambientes de desenvolvimento")
    
    index_file = os.path.expanduser("~/projeto_final/data/index.json")
    
    if not os.path.exists(index_file):
        message = "Índice de projetos não encontrado. Execute scan primeiro."
        memory_manager.log_activity(message, "ERROR")
        return {"success": False, "error": message}
    
    import json
    with open(index_file, "r", encoding="utf-8") as f:
        projects = json.load(f)
    
    success_count = 0
    for project in projects:
        success, msg = env_manager.setup_project(project)
        if success:
            success_count += 1
    
    message = f"Configurados {success_count}/{len(projects)} ambientes"
    memory_manager.log_activity(message)
    notify_tts(message)
    
    return {"success": True, "configured": success_count, "total": len(projects)}

def analyze_project(project_path: str, auto_apply: bool = None) -> Dict[str, Any]:
    """
    Analisa um projeto e aplica melhorias.
    
    Args:
        project_path: Caminho do projeto
        auto_apply: Se deve aplicar automaticamente (None = usar preferência)
        
    Returns:
        Dicionário com resultados
    """
    from engineer import analyze_project as eng_analyze
    
    if auto_apply is None:
        aggressiveness = memory_manager.get_preference("aggressiveness", "medium")
        auto_apply = (aggressiveness == "high")
    
    memory_manager.log_activity(f"Analisando projeto: {project_path}")
    notify_tts(f"Analisando projeto {os.path.basename(project_path)}")
    
    result = eng_analyze(project_path)
    
    # Registrar na memória
    memory_manager.record_project_action(
        project_path,
        "analyzed",
        {"suggestions": len(result.get("suggestions", []))}
    )
    
    return result

def route(command: str, **kwargs) -> Any:
    """
    Roteia um comando para a ação apropriada.
    
    Args:
        command: Comando a executar
        **kwargs: Argumentos adicionais
        
    Returns:
        Resultado da ação
    """
    command = command.lower().strip()
    
    # Comandos de scan
    if "scan" in command and "download" in command:
        return scan_downloads_and_import(kwargs.get("downloads_path"))
    
    elif "scan" in command and "project" in command:
        return scan_projects(kwargs.get("scan_dirs"))
    
    # Comandos de configuração
    elif "setup" in command or "configurar" in command:
        return setup_environments()
    
    # Comandos de análise
    elif "analis" in command or "melhor" in command:
        project_path = kwargs.get("project_path")
        if not project_path:
            return {"success": False, "error": "project_path não especificado"}
        return analyze_project(project_path, kwargs.get("auto_apply"))
    
    # Comando desconhecido
    else:
        message = f"Comando não reconhecido: {command}"
        memory_manager.log_activity(message, "WARNING")
        return {"success": False, "error": message}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Action Router do J.A.R.V.I.S")
    parser.add_argument("command", help="Comando a executar")
    parser.add_argument("--project-path", help="Caminho do projeto")
    parser.add_argument("--downloads-path", help="Caminho da pasta de downloads")
    parser.add_argument("--auto-apply", action="store_true", help="Aplicar automaticamente")
    args = parser.parse_args()
    
    result = route(
        args.command,
        project_path=args.project_path,
        downloads_path=args.downloads_path,
        auto_apply=args.auto_apply
    )
    
    print("\nResultado:")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))

