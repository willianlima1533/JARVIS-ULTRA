#!/usr/bin/env python3
# core/sandbox.py
"""
Módulo de sandbox para testes seguros.
Cria um ambiente isolado para testar modificações antes de aplicá-las.
"""
import os
import shutil
import subprocess
import tempfile
from typing import Tuple, List

def run_in_sandbox(project_root: str, cmd: List[str], timeout: int = 30) -> Tuple[bool, str]:
    """
    Executa um comando em um ambiente sandbox isolado.
    
    Args:
        project_root: Caminho raiz do projeto
        cmd: Lista com comando e argumentos
        timeout: Timeout em segundos
        
    Returns:
        Tupla (sucesso, output)
    """
    print(f"[SANDBOX] Criando ambiente isolado para: {project_root}")
    
    # Criar diretório temporário
    tmp_dir = tempfile.mkdtemp(prefix="sandbox_")
    sandbox_path = os.path.join(tmp_dir, "project")
    
    try:
        # Copiar projeto para sandbox
        print(f"[SANDBOX] Copiando projeto para sandbox...")
        shutil.copytree(project_root, sandbox_path, dirs_exist_ok=True)
        
        # Executar comando
        print(f"[SANDBOX] Executando comando: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=sandbox_path,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout + (f"\nSTDERR:\n{result.stderr}" if result.stderr else "")
        success = result.returncode == 0
        
        print(f"[SANDBOX] Comando {'bem-sucedido' if success else 'falhou'}")
        
        return success, output
        
    except subprocess.TimeoutExpired:
        print(f"[SANDBOX] Comando expirou após {timeout}s")
        return False, f"Timeout após {timeout}s"
        
    except Exception as e:
        print(f"[SANDBOX] Erro: {e}")
        return False, str(e)
        
    finally:
        # Limpar sandbox
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            print(f"[SANDBOX] Sandbox limpo")
        except Exception as e:
            print(f"[SANDBOX] Aviso: Falha ao limpar sandbox: {e}")

def test_python_project(project_path: str, test_file: str = None) -> Tuple[bool, str]:
    """
    Testa um projeto Python no sandbox.
    
    Args:
        project_path: Caminho do projeto
        test_file: Arquivo de teste específico (opcional)
        
    Returns:
        Tupla (sucesso, output)
    """
    # Determinar o comando de teste
    if test_file:
        cmd = ["python", test_file]
    elif os.path.exists(os.path.join(project_path, "test.py")):
        cmd = ["python", "test.py"]
    elif os.path.exists(os.path.join(project_path, "tests")):
        cmd = ["python", "-m", "pytest", "tests"]
    else:
        # Tentar importar o módulo principal
        main_files = ["main.py", "app.py", "__init__.py"]
        for main_file in main_files:
            if os.path.exists(os.path.join(project_path, main_file)):
                cmd = ["python", "-c", f"import {os.path.splitext(main_file)[0]}"]
                break
        else:
            return False, "Nenhum arquivo de teste ou main.py encontrado"
    
    return run_in_sandbox(project_path, cmd, timeout=60)

def test_node_project(project_path: str) -> Tuple[bool, str]:
    """
    Testa um projeto Node.js no sandbox.
    
    Args:
        project_path: Caminho do projeto
        
    Returns:
        Tupla (sucesso, output)
    """
    # Verificar se há script de teste no package.json
    package_json = os.path.join(project_path, "package.json")
    if os.path.exists(package_json):
        import json
        with open(package_json, "r", encoding="utf-8") as f:
            package_data = json.load(f)
        
        if "scripts" in package_data and "test" in package_data["scripts"]:
            cmd = ["npm", "test"]
        else:
            # Tentar executar o arquivo principal
            main_file = package_data.get("main", "index.js")
            cmd = ["node", main_file]
    else:
        cmd = ["node", "index.js"]
    
    return run_in_sandbox(project_path, cmd, timeout=60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Testar projetos em sandbox")
    parser.add_argument("project_path", help="Caminho do projeto")
    parser.add_argument("--type", choices=["python", "node"], required=True, help="Tipo do projeto")
    parser.add_argument("--test-file", help="Arquivo de teste específico (Python)")
    args = parser.parse_args()
    
    if args.type == "python":
        success, output = test_python_project(args.project_path, args.test_file)
    else:
        success, output = test_node_project(args.project_path)
    
    print("\n" + "="*60)
    print("RESULTADO DO TESTE NO SANDBOX")
    print("="*60)
    print(output)
    print("="*60)
    print(f"Status: {'SUCESSO' if success else 'FALHA'}")
    print("="*60)
    
    exit(0 if success else 1)

