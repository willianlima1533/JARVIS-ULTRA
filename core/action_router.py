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
import json

# Adicionar o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import project_scan, env_manager, memory_manager
from core.realtime_info_manager import RealtimeInfoManager
from core.camera_perception import CameraPerception

# Instanciar os gerenciadores
info_manager = RealtimeInfoManager()
camera_perception = CameraPerception()

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
        return {"success": False, "error": message}
    
    # Procurar arquivos ZIP
    zip_files = []
    for file in os.listdir(downloads_path):
        if file.lower().endswith(".zip"):
            zip_files.append(os.path.join(downloads_path, file))
    
    if not zip_files:
        message = "Nenhum arquivo ZIP encontrado em downloads"
        memory_manager.log_activity(message)
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
        message = f"Importados {len(imported)} projetos: {''.join(imported)}"
        memory_manager.log_activity(message)
    
    if failed:
        message = f"Falha ao importar: {''.join(failed)}"
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
    
    projects = project_scan.scan_projects(scan_dirs)
    
    message = f"Encontrados {len(projects)} projetos"
    memory_manager.log_activity(message)
    
    return {"success": True, "count": len(projects), "projects": projects}

def setup_environments() -> Dict[str, Any]:
    """
    Configura ambientes para todos os projetos detectados.
    
    Returns:
        Dicionário com resultados
    """
    memory_manager.log_activity("Configurando ambientes...")
    
    index_file = os.path.expanduser("~/projeto_final/data/index.json")
    
    if not os.path.exists(index_file):
        message = "Índice de projetos não encontrado. Execute scan primeiro."
        memory_manager.log_activity(message, "ERROR")
        return {"success": False, "error": message}
    
    with open(index_file, "r", encoding="utf-8") as f:
        projects = json.load(f)
    
    success_count = 0
    for project in projects:
        success, msg = env_manager.setup_project(project)
        if success:
            success_count += 1
    
    message = f"Configurados {success_count}/{len(projects)} ambientes"
    memory_manager.log_activity(message)
    
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
    from engineer import auto_engineer # Importar diretamente auto_engineer
    
    if auto_apply is None:
        aggressiveness = memory_manager.get_preference("aggressiveness", "medium")
        auto_apply = (aggressiveness == "high")
    
    memory_manager.log_activity(f"Analisando projeto: {project_path}")
    
    result = auto_engineer.analyze_project(project_path, auto_apply) # Passar auto_apply
    
    # Registrar na memória
    memory_manager.record_project_action(
        project_path,
        "analyzed",
        {"suggestions": len(result.get("suggestions", []))}
    )
    
    return result

def get_weather_info(city: str, country_code: str = "BR") -> Dict[str, Any]:
    """
    Obtém informações meteorológicas.
    """
    memory_manager.log_activity(f"Obtendo clima para {city}, {country_code}")
    result = info_manager.get_weather(city, country_code)
    # A notificação TTS será tratada pelo action_router ou cognitive_processor
    return {"success": True, "result": result}

def get_news(query: str = "geral") -> Dict[str, Any]:
    """
    Obtém manchetes de notícias.
    """
    memory_manager.log_activity(f"Obtendo notícias sobre {query}")
    result = info_manager.get_news_headlines(query)
    return {"success": True, "result": result}

def get_nearby(latitude: float, longitude: float, query: str = "pontos de interesse") -> Dict[str, Any]:
    """
    Obtém informações sobre locais próximos.
    """
    memory_manager.log_activity(f"Buscando {query} próximos a {latitude}, {longitude}")
    result = info_manager.get_nearby_places(latitude, longitude, query=query)
    return {"success": True, "result": result}

def perceive_mood() -> Dict[str, Any]:
    """
    Ativa a percepção da câmera para analisar o humor do usuário.
    """
    memory_manager.log_activity("Ativando percepção de humor via câmera.")
    result = camera_perception.perceive_user_mood()
    return {"success": True, "result": result}

def route(command: str, **kwargs) -> Any:
    """
    Roteia um comando para a ação apropriada.
    
    Args:
        command: Comando a executar
        **kwargs: Argumentos adicionais
        
    Returns:
        Resultado da ação
    """
    command_lower = command.lower().strip()

    # A notificação TTS de "Processando" deve ser tratada no VoiceAssistant ou no CognitiveProcessor,
    # ou o teste deve ser ajustado para não esperar essa chamada aqui.
    # Removendo a chamada para evitar duplicação ou chamadas inesperadas.
    
    # Comandos de scan
    if "scan" in command_lower and "download" in command_lower:
        return scan_downloads_and_import(kwargs.get("downloads_path"))
    
    elif "scan" in command_lower and "project" in command_lower:
        return scan_projects(kwargs.get("scan_dirs"))
    
    # Comandos de configuração
    elif "setup" in command_lower or "configurar" in command_lower:
        return setup_environments()
    
    # Comandos de análise
    elif "analis" in command_lower or "melhor" in command_lower:
        project_path = kwargs.get("project_path")
        if not project_path:
            return {"success": False, "error": "project_path não especificado"}
        return analyze_project(project_path, kwargs.get("auto_apply"))
    
    # Comandos de informações em tempo real
    elif "clima" in command_lower or "tempo" in command_lower:
        city = kwargs.get("city")
        if not city:
            # Tentar extrair a cidade do comando, ou usar uma padrão
            # Ex: "qual o clima em São Paulo" -> "São Paulo"
            parts = command_lower.split("em ")
            if len(parts) > 1:
                city = parts[1].split(" ")[0].strip()
            else:
                city = memory_manager.get_preference("default_city", "São Paulo") # Usar uma cidade padrão
        return get_weather_info(city, kwargs.get("country_code", "BR"))

    elif "noticias" in command_lower:
        query = kwargs.get("query")
        if not query:
            parts = command_lower.split("sobre ")
            if len(parts) > 1:
                query = parts[1].strip()
            else:
                query = "geral"
        return get_news(query)

    elif "perto de mim" in command_lower or "proximo" in command_lower:
        latitude = kwargs.get("latitude")
        longitude = kwargs.get("longitude")
        query_place = kwargs.get("query_place")

        if not latitude or not longitude:
            # Tentar obter localização do sistema ou da memória
            # Por enquanto, usar valores fixos para demonstração
            latitude = memory_manager.get_preference("last_known_latitude", -23.5505) # São Paulo
            longitude = memory_manager.get_preference("last_known_longitude", -46.6333) # São Paulo

        if not query_place:
            parts = command_lower.split("encontre ")
            if len(parts) > 1:
                query_place = parts[1].split(" perto")[0].strip()
            else:
                query_place = "pontos de interesse"
        return get_nearby(latitude, longitude, query=query_place)

    elif "ver meu humor" in command_lower or "como estou" in command_lower or "minha cara" in command_lower:
        return perceive_mood()

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
    parser.add_argument("--city", help="Cidade para consulta de clima")
    parser.add_argument("--query-news", help="Tópico para consulta de notícias")
    parser.add_argument("--latitude", type=float, help="Latitude para locais próximos")
    parser.add_argument("--longitude", type=float, help="Longitude para locais próximos")
    parser.add_argument("--query-place", help="Tipo de lugar para consulta de locais próximos")
    parser.add_argument("--perceive-mood", action="store_true", help="Ativar percepção de humor pela câmera")

    args = parser.parse_args()
    
    # Construir kwargs dinamicamente para passar apenas os argumentos relevantes
    route_kwargs = {
        "project_path": args.project_path,
        "downloads_path": args.downloads_path,
        "auto_apply": args.auto_apply,
        "city": args.city,
        "query_news": args.query_news,
        "latitude": args.latitude,
        "longitude": args.longitude,
        "query_place": args.query_place
    }
    
    result = route(
        args.command,
        **{k: v for k, v in route_kwargs.items() if v is not None} # Passar apenas args não nulos
    )
    
    print("\nResultado:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

