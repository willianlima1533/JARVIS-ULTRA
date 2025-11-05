#!/usr/bin/env python3
# core/shortcuts_manager.py
"""
Módulo de gerenciamento de atalhos para Termux.
Cria atalhos em ~/.shortcuts para execução rápida de projetos.
"""
import os
import json
import stat
from typing import List, Dict

SHORTCUTS_DIR = os.path.join(os.path.expanduser("~"), ".shortcuts")

def ensure_shortcuts_dir():
    """Garante que o diretório de atalhos existe."""
    os.makedirs(SHORTCUTS_DIR, exist_ok=True)
    print(f"[SHORTCUTS] Diretório de atalhos: {SHORTCUTS_DIR}")

def create_python_shortcut(project_info: Dict) -> str:
    """
    Cria um atalho para executar um projeto Python.
    
    Args:
        project_info: Dicionário com informações do projeto
        
    Returns:
        Caminho do atalho criado
    """
    project_path = project_info["path"]
    project_name = os.path.basename(project_path)
    shortcut_name = f"run_{project_name}.sh"
    shortcut_path = os.path.join(SHORTCUTS_DIR, shortcut_name)
    
    # Determinar o arquivo principal
    main_files = ["main.py", "app.py", "run.py", "__main__.py"]
    main_file = None
    for mf in main_files:
        if os.path.exists(os.path.join(project_path, mf)):
            main_file = mf
            break
    
    if not main_file:
        main_file = "main.py"  # fallback
    
    venv_python = os.path.join(project_path, "venv", "bin", "python")
    
    script_content = f"""#!/data/data/com.termux/files/usr/bin/bash
# Atalho para: {project_name}
# Tipo: Python
# Caminho: {project_path}

cd "{project_path}" || exit 1

if [ -f "{venv_python}" ]; then
    echo "[RUN] Executando com venv: {main_file}"
    "{venv_python}" "{main_file}"
else
    echo "[RUN] Executando com Python global: {main_file}"
    python "{main_file}"
fi
"""
    
    with open(shortcut_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # Tornar executável
    os.chmod(shortcut_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    print(f"[SHORTCUTS] Atalho Python criado: {shortcut_path}")
    return shortcut_path

def create_node_shortcut(project_info: Dict) -> str:
    """
    Cria um atalho para executar um projeto Node.js.
    
    Args:
        project_info: Dicionário com informações do projeto
        
    Returns:
        Caminho do atalho criado
    """
    project_path = project_info["path"]
    project_name = os.path.basename(project_path)
    shortcut_name = f"run_{project_name}.sh"
    shortcut_path = os.path.join(SHORTCUTS_DIR, shortcut_name)
    
    # Ler package.json para determinar o script de start
    package_json = os.path.join(project_path, "package.json")
    start_cmd = "npm start"
    
    if os.path.exists(package_json):
        try:
            with open(package_json, "r", encoding="utf-8") as f:
                package_data = json.load(f)
            
            if "scripts" in package_data:
                if "start" in package_data["scripts"]:
                    start_cmd = "npm start"
                elif "dev" in package_data["scripts"]:
                    start_cmd = "npm run dev"
        except Exception as e:
            print(f"[SHORTCUTS] Aviso: Falha ao ler package.json: {e}")
    
    script_content = f"""#!/data/data/com.termux/files/usr/bin/bash
# Atalho para: {project_name}
# Tipo: Node.js
# Caminho: {project_path}

cd "{project_path}" || exit 1

echo "[RUN] Executando: {start_cmd}"
{start_cmd}
"""
    
    with open(shortcut_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # Tornar executável
    os.chmod(shortcut_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    print(f"[SHORTCUTS] Atalho Node.js criado: {shortcut_path}")
    return shortcut_path

def create_dashboard_shortcut(dashboard_path: str = None) -> str:
    """
    Cria um atalho para abrir o dashboard Streamlit.
    
    Args:
        dashboard_path: Caminho do arquivo dashboard (opcional)
        
    Returns:
        Caminho do atalho criado
    """
    if dashboard_path is None:
        dashboard_path = os.path.join(os.path.expanduser("~"), "projeto_final/interface/streamlit_dashboard.py")
    
    shortcut_path = os.path.join(SHORTCUTS_DIR, "open_dashboard.sh")
    
    script_content = f"""#!/data/data/com.termux/files/usr/bin/bash
# Atalho para: Dashboard do Projeto Final

echo "[DASHBOARD] Iniciando dashboard Streamlit..."
streamlit run "{dashboard_path}"
"""
    
    with open(shortcut_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    os.chmod(shortcut_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    print(f"[SHORTCUTS] Atalho do dashboard criado: {shortcut_path}")
    return shortcut_path

def create_shortcuts_from_index(index_file: str) -> List[str]:
    """
    Cria atalhos para todos os projetos no índice.
    
    Args:
        index_file: Caminho do arquivo de índice
        
    Returns:
        Lista de caminhos dos atalhos criados
    """
    ensure_shortcuts_dir()
    
    if not os.path.exists(index_file):
        print(f"[SHORTCUTS] Índice não encontrado: {index_file}")
        return []
    
    with open(index_file, "r", encoding="utf-8") as f:
        projects = json.load(f)
    
    shortcuts = []
    
    for project in projects:
        project_type = project.get("type")
        
        try:
            if project_type == "python":
                shortcut = create_python_shortcut(project)
                shortcuts.append(shortcut)
            elif project_type == "node":
                shortcut = create_node_shortcut(project)
                shortcuts.append(shortcut)
            else:
                print(f"[SHORTCUTS] Tipo desconhecido: {project_type} para {project['path']}")
        except Exception as e:
            print(f"[SHORTCUTS] Erro ao criar atalho para {project['path']}: {e}")
    
    # Criar atalho do dashboard
    try:
        dashboard_shortcut = create_dashboard_shortcut()
        shortcuts.append(dashboard_shortcut)
    except Exception as e:
        print(f"[SHORTCUTS] Erro ao criar atalho do dashboard: {e}")
    
    print(f"[SHORTCUTS] Total de atalhos criados: {len(shortcuts)}")
    return shortcuts

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerenciar atalhos do Termux")
    parser.add_argument("--index", default=os.path.join(os.path.expanduser("~"), "projeto_final/data/index.json"),
                        help="Arquivo de índice de projetos")
    parser.add_argument("--dashboard", help="Criar apenas atalho do dashboard")
    args = parser.parse_args()
    
    if args.dashboard:
        create_dashboard_shortcut()
    else:
        shortcuts = create_shortcuts_from_index(args.index)
        print(f"\nAtalhos criados em: {SHORTCUTS_DIR}")
        for shortcut in shortcuts:
            print(f"  - {os.path.basename(shortcut)}")

