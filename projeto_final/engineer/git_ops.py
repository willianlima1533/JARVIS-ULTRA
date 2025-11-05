#!/usr/bin/env python3
# engineer/git_ops.py
"""
Operações Git para controle de versão e aplicação de patches.
"""
import os
import subprocess
from typing import Tuple
from engineer.logger import get_logger

logger = get_logger("git_ops")

def run_git_command(cmd: str, cwd: str = None) -> Tuple[bool, str]:
    """
    Executa um comando Git.
    
    Args:
        cmd: Comando Git
        cwd: Diretório de trabalho
        
    Returns:
        Tupla (sucesso, output)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True
        )
        output = result.stdout + ("\nERROR:\n" + result.stderr if result.stderr else "")
        return result.returncode == 0, output
    except Exception as e:
        logger.error(f"Erro ao executar comando Git: {e}")
        return False, str(e)

def init_repo(path: str) -> bool:
    """
    Inicializa um repositório Git se não existir.
    
    Args:
        path: Caminho do repositório
        
    Returns:
        True se bem-sucedido
    """
    if not os.path.exists(os.path.join(path, ".git")):
        logger.info(f"Inicializando repositório Git em: {path}")
        success, output = run_git_command("git init", cwd=path)
        
        if success:
            logger.info("Repositório Git inicializado")
            # Configurar nome e email padrão se não configurado
            run_git_command('git config user.name "Projeto Final"', cwd=path)
            run_git_command('git config user.email "projeto@final.local"', cwd=path)
        else:
            logger.error(f"Falha ao inicializar repositório: {output}")
        
        return success
    else:
        logger.info("Repositório Git já existe")
        return True

def commit_all(path: str, message: str = "auto commit") -> Tuple[bool, str]:
    """
    Adiciona e commita todas as mudanças.
    
    Args:
        path: Caminho do repositório
        message: Mensagem do commit
        
    Returns:
        Tupla (sucesso, output)
    """
    # Adicionar todos os arquivos
    run_git_command("git add -A", cwd=path)
    
    # Commitar
    success, output = run_git_command(f'git commit -m "{message}"', cwd=path)
    
    if not success:
        if "nothing to commit" in output.lower():
            logger.info("Nada para commitar")
            return True, "Nothing to commit"
        else:
            logger.warning(f"Commit falhou: {output}")
    else:
        logger.info(f"Commit realizado: {message}")
    
    return success, output

def create_branch(path: str, branch_name: str) -> Tuple[bool, str]:
    """
    Cria e muda para uma nova branch.
    
    Args:
        path: Caminho do repositório
        branch_name: Nome da branch
        
    Returns:
        Tupla (sucesso, output)
    """
    logger.info(f"Criando branch: {branch_name}")
    success, output = run_git_command(f"git checkout -b {branch_name}", cwd=path)
    
    if success:
        logger.info(f"Branch {branch_name} criada")
    else:
        logger.error(f"Falha ao criar branch: {output}")
    
    return success, output

def checkout_branch(path: str, branch_name: str) -> Tuple[bool, str]:
    """
    Muda para uma branch existente.
    
    Args:
        path: Caminho do repositório
        branch_name: Nome da branch
        
    Returns:
        Tupla (sucesso, output)
    """
    logger.info(f"Mudando para branch: {branch_name}")
    success, output = run_git_command(f"git checkout {branch_name}", cwd=path)
    
    if success:
        logger.info(f"Mudou para branch {branch_name}")
    else:
        logger.error(f"Falha ao mudar para branch: {output}")
    
    return success, output

def rollback_to_commit(path: str, commit_hash: str) -> Tuple[bool, str]:
    """
    Reverte para um commit específico.
    
    Args:
        path: Caminho do repositório
        commit_hash: Hash do commit
        
    Returns:
        Tupla (sucesso, output)
    """
    logger.warning(f"Revertendo para commit: {commit_hash}")
    success, output = run_git_command(f"git reset --hard {commit_hash}", cwd=path)
    
    if success:
        logger.info(f"Revertido para {commit_hash}")
    else:
        logger.error(f"Falha ao reverter: {output}")
    
    return success, output

def get_current_commit(path: str) -> str:
    """
    Obtém o hash do commit atual.
    
    Args:
        path: Caminho do repositório
        
    Returns:
        Hash do commit ou None se falhar
    """
    success, output = run_git_command("git rev-parse HEAD", cwd=path)
    
    if success:
        return output.strip()
    else:
        return None

def get_diff(path: str, file_path: str = None) -> str:
    """
    Obtém o diff das mudanças.
    
    Args:
        path: Caminho do repositório
        file_path: Arquivo específico (opcional)
        
    Returns:
        Diff das mudanças
    """
    cmd = "git diff"
    if file_path:
        cmd += f" {file_path}"
    
    success, output = run_git_command(cmd, cwd=path)
    
    if success:
        return output
    else:
        return ""

def get_log(path: str, n: int = 10) -> str:
    """
    Obtém o log dos últimos commits.
    
    Args:
        path: Caminho do repositório
        n: Número de commits
        
    Returns:
        Log dos commits
    """
    success, output = run_git_command(f"git log --oneline -n {n}", cwd=path)
    
    if success:
        return output
    else:
        return "Nenhum commit encontrado"

if __name__ == "__main__":
    import argparse
    import tempfile
    
    parser = argparse.ArgumentParser(description="Operações Git")
    parser.add_argument("--test", action="store_true", help="Executar testes")
    args = parser.parse_args()
    
    if args.test:
        # Criar um repositório temporário para teste
        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"Testando operações Git em: {tmpdir}")
            
            # Inicializar repo
            init_repo(tmpdir)
            
            # Criar um arquivo
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("Teste\n")
            
            # Commitar
            commit_all(tmpdir, "Commit inicial")
            
            # Obter commit atual
            current = get_current_commit(tmpdir)
            print(f"Commit atual: {current}")
            
            # Modificar arquivo
            with open(test_file, "a") as f:
                f.write("Modificação\n")
            
            # Ver diff
            diff = get_diff(tmpdir)
            print(f"Diff:\n{diff}")
            
            # Commitar novamente
            commit_all(tmpdir, "Segunda modificação")
            
            # Ver log
            log = get_log(tmpdir)
            print(f"Log:\n{log}")
            
            print("\nTestes concluídos!")

