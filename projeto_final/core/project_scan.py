#!/usr/bin/env python3
# core/project_scan.py
"""
Módulo de escaneamento de projetos.
Detecta projetos Python/Node.js e arquivos ZIP em diretórios configuráveis.
Descompacta ZIPs automaticamente e identifica o tipo de projeto.
"""
import os
import json
import zipfile
import shutil
from typing import List, Dict

def extract_zip(file_path: str, dest_dir: str) -> bool:
    """
    Extrai um arquivo ZIP para um diretório de destino.
    
    Args:
        file_path: Caminho para o arquivo ZIP
        dest_dir: Diretório de destino para extração
        
    Returns:
        True se a extração foi bem-sucedida, False caso contrário
    """
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
        print(f"[SCAN] ZIP extraído com sucesso: {file_path} -> {dest_dir}")
        return True
    except Exception as e:
        print(f"[SCAN] Falha ao extrair {file_path}: {e}")
        return False

def detect_project_type(path: str) -> str:
    """
    Detecta o tipo de projeto baseado em arquivos marcadores.
    
    Args:
        path: Caminho do diretório do projeto
        
    Returns:
        'python', 'node', ou 'unknown'
    """
    files = os.listdir(path) if os.path.isdir(path) else []
    
    if "requirements.txt" in files or "setup.py" in files or "pyproject.toml" in files:
        return "python"
    elif "package.json" in files:
        return "node"
    else:
        return "unknown"

def scan_projects(base_dirs: List[str], data_dir: str = None) -> List[Dict]:
    """
    Escaneia diretórios em busca de projetos e ZIPs.
    
    Args:
        base_dirs: Lista de diretórios base para escanear
        data_dir: Diretório onde salvar o índice de projetos
        
    Returns:
        Lista de dicionários com informações dos projetos detectados
    """
    if data_dir is None:
        data_dir = os.path.join(os.path.expanduser("~"), "projeto_final/data")
    
    os.makedirs(data_dir, exist_ok=True)
    projects = []
    processed_zips = set()
    
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            print(f"[SCAN] Diretório não existe: {base_dir}")
            continue
            
        print(f"[SCAN] Escaneando: {base_dir}")
        
        for root, dirs, files in os.walk(base_dir):
            # Ignorar diretórios de ambiente virtual e node_modules
            dirs[:] = [d for d in dirs if d not in ['venv', 'node_modules', '.git', '__pycache__']]
            
            # Processar ZIPs encontrados
            for f in files:
                if f.lower().endswith(".zip"):
                    zip_path = os.path.join(root, f)
                    
                    if zip_path in processed_zips:
                        continue
                    
                    extract_dir = os.path.join(base_dir, "extracted", os.path.splitext(f)[0])
                    
                    if not os.path.exists(extract_dir):
                        print(f"[SCAN] Extraindo {zip_path} para {extract_dir}")
                        if extract_zip(zip_path, extract_dir):
                            processed_zips.add(zip_path)
                            # Verificar se o ZIP extraído contém um projeto
                            project_type = detect_project_type(extract_dir)
                            if project_type != "unknown":
                                projects.append({
                                    "path": extract_dir,
                                    "type": project_type,
                                    "source": "zip",
                                    "original_zip": zip_path
                                })
            
            # Detectar projetos existentes
            project_type = detect_project_type(root)
            if project_type != "unknown":
                # Evitar duplicatas
                if not any(p["path"] == root for p in projects):
                    projects.append({
                        "path": root,
                        "type": project_type,
                        "source": "directory"
                    })
    
    # Salvar índice global
    index_file = os.path.join(data_dir, "index.json")
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
    
    print(f"[SCAN] Total de projetos detectados: {len(projects)}")
    print(f"[SCAN] Índice salvo em: {index_file}")
    
    return projects

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Escanear projetos em diretórios")
    parser.add_argument("--dirs", nargs="+", default=[os.path.expanduser("~/storage/downloads"), os.path.expanduser("~/projects")],
                        help="Diretórios para escanear")
    parser.add_argument("--data-dir", default=None, help="Diretório para salvar o índice")
    args = parser.parse_args()
    
    projects = scan_projects(args.dirs, args.data_dir)
    print(f"\nProjetos encontrados: {len(projects)}")
    for p in projects:
        print(f"  - {p['path']} ({p['type']}) [fonte: {p['source']}]")

