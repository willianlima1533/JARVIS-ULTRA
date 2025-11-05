#!/usr/bin/env python3
# core/env_manager.py
"""
Módulo de gerenciamento de ambientes de desenvolvimento.
Cria e configura ambientes virtuais para projetos Python e Node.js.
"""
import os
import subprocess
import sys
from typing import Tuple

def run_command(cmd: list, cwd: str = None, timeout: int = 300) -> Tuple[bool, str]:
    """
    Executa um comando e retorna o resultado.
    
    Args:
        cmd: Lista com o comando e argumentos
        cwd: Diretório de trabalho
        timeout: Timeout em segundos
        
    Returns:
        Tupla (sucesso, output)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout + (f"\nERROR:\n{result.stderr}" if result.stderr else "")
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"Comando expirou após {timeout}s"
    except Exception as e:
        return False, str(e)

def setup_python(project_path: str) -> Tuple[bool, str]:
    """
    Configura ambiente Python para um projeto.
    
    Args:
        project_path: Caminho do projeto
        
    Returns:
        Tupla (sucesso, mensagem)
    """
    print(f"[ENV] Configurando ambiente Python em: {project_path}")
    
    venv_path = os.path.join(project_path, "venv")
    
    # Criar venv se não existir
    if not os.path.exists(venv_path):
        print(f"[ENV] Criando ambiente virtual...")
        success, output = run_command([sys.executable, "-m", "venv", venv_path])
        if not success:
            return False, f"Falha ao criar venv: {output}"
    else:
        print(f"[ENV] Ambiente virtual já existe")
    
    # Determinar o caminho do pip no venv
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_path, "Scripts", "pip")
        python_path = os.path.join(venv_path, "Scripts", "python")
    else:  # Unix/Linux/Termux
        pip_path = os.path.join(venv_path, "bin", "pip")
        python_path = os.path.join(venv_path, "bin", "python")
    
    # Atualizar pip, setuptools, wheel
    print(f"[ENV] Atualizando pip, setuptools, wheel...")
    success, output = run_command([pip_path, "install", "--upgrade", "pip", "setuptools", "wheel"])
    if not success:
        print(f"[ENV] Aviso: Falha ao atualizar pip: {output}")
    
    # Instalar dependências se requirements.txt existir
    req_file = os.path.join(project_path, "requirements.txt")
    if os.path.exists(req_file):
        print(f"[ENV] Instalando dependências de requirements.txt...")
        success, output = run_command([pip_path, "install", "-r", req_file], cwd=project_path)
        if not success:
            return False, f"Falha ao instalar dependências: {output}"
        print(f"[ENV] Dependências instaladas com sucesso")
    else:
        print(f"[ENV] Nenhum requirements.txt encontrado")
    
    return True, f"Ambiente Python configurado em {venv_path}"

def setup_node(project_path: str) -> Tuple[bool, str]:
    """
    Configura ambiente Node.js para um projeto.
    
    Args:
        project_path: Caminho do projeto
        
    Returns:
        Tupla (sucesso, mensagem)
    """
    print(f"[ENV] Configurando ambiente Node.js em: {project_path}")
    
    package_json = os.path.join(project_path, "package.json")
    if not os.path.exists(package_json):
        return False, "package.json não encontrado"
    
    # Verificar se npm está disponível
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "npm não está instalado ou não está no PATH"
    
    # Executar npm install
    print(f"[ENV] Executando npm install...")
    success, output = run_command(["npm", "install"], cwd=project_path, timeout=600)
    
    if not success:
        return False, f"Falha ao executar npm install: {output}"
    
    print(f"[ENV] Dependências Node.js instaladas com sucesso")
    return True, "Ambiente Node.js configurado"

def setup_project(project_info: dict) -> Tuple[bool, str]:
    """
    Configura o ambiente para um projeto baseado em seu tipo.
    
    Args:
        project_info: Dicionário com informações do projeto (path, type)
        
    Returns:
        Tupla (sucesso, mensagem)
    """
    project_path = project_info.get("path")
    project_type = project_info.get("type")
    
    if not project_path or not os.path.exists(project_path):
        return False, f"Caminho do projeto inválido: {project_path}"
    
    if project_type == "python":
        return setup_python(project_path)
    elif project_type == "node":
        return setup_node(project_path)
    else:
        return False, f"Tipo de projeto desconhecido: {project_type}"

if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Configurar ambientes de projetos")
    parser.add_argument("--index", default=os.path.join(os.path.expanduser("~"), "projeto_final/data/index.json"),
                        help="Arquivo de índice de projetos")
    parser.add_argument("--project-path", help="Caminho específico de um projeto para configurar")
    parser.add_argument("--project-type", choices=["python", "node"], help="Tipo do projeto")
    args = parser.parse_args()
    
    if args.project_path and args.project_type:
        # Configurar um projeto específico
        success, msg = setup_project({"path": args.project_path, "type": args.project_type})
        print(msg)
        sys.exit(0 if success else 1)
    elif os.path.exists(args.index):
        # Configurar todos os projetos do índice
        with open(args.index, "r", encoding="utf-8") as f:
            projects = json.load(f)
        
        print(f"[ENV] Configurando {len(projects)} projetos...")
        for project in projects:
            print(f"\n[ENV] Processando: {project['path']}")
            success, msg = setup_project(project)
            print(f"[ENV] Resultado: {msg}")
    else:
        print(f"[ENV] Índice não encontrado: {args.index}")
        print(f"[ENV] Execute project_scan.py primeiro para gerar o índice")
        sys.exit(1)

