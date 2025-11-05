
#!/usr/bin/env python3
# core/auto_updater.py
"""
Módulo de autoatualização para o J.A.R.V.I.S.
Verifica, baixa e aplica atualizações de uma fonte configurável.
"""
import os
import subprocess
import sys
import shutil
import requests
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import memory_manager
from core.utils import notify_tts
from core.jarvis_installer import JarvisInstaller # Importar o novo instalador

PROJECT_ROOT = os.path.expanduser("~/projects/projeto_final")
BACKUP_DIR = os.path.expanduser("~/.jarvis_backups/updates")
VERSION_FILE = os.path.join(PROJECT_ROOT, "VERSION") # Arquivo para armazenar a versão atual

# URL para verificar a última versão e baixar o pacote de atualização
UPDATE_CHECK_URL = "https://example.com/jarvis_latest_version.json" # Substituir por uma URL real
UPDATE_PACKAGE_URL = "https://example.com/jarvis_update.zip" # Substituir por uma URL real

def get_current_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    return "0.0.0" # Versão inicial se o arquivo não existir

def set_current_version(version):
    with open(VERSION_FILE, "w") as f:
        f.write(version)

def check_for_updates() -> dict:
    """
    Verifica se há atualizações disponíveis em uma URL remota.
    
    Returns:
        Dicionário com informações da atualização (latest_version, download_url, checksum) ou None.
    """
    memory_manager.log_activity("Verificando atualizações...")
    notify_tts("Verificando atualizações para o J.A.R.V.I.S.")
    
    try:
        response = requests.get(UPDATE_CHECK_URL, timeout=10)
        response.raise_for_status()
        update_info = response.json()
        
        latest_version = update_info.get("version")
        download_url = update_info.get("download_url")
        checksum = update_info.get("checksum") # Ex: SHA256
        
        if not all([latest_version, download_url, checksum]):
            memory_manager.log_activity("Informações de atualização incompletas na URL remota.", "ERROR")
            return None
            
        current_version = get_current_version()
        
        # Comparação de versão simples (pode ser melhorado para semver)
        if tuple(map(int, latest_version.split("."))) > tuple(map(int, current_version.split("."))):
            memory_manager.log_activity(f"Atualizações disponíveis! Versão atual: {current_version}, Mais recente: {latest_version}")
            notify_tts(f"Atualizações disponíveis para o J.A.R.V.I.S. Versão {latest_version}.")
            return update_info
        else:
            memory_manager.log_activity("J.A.R.V.I.S já está atualizado.")
            notify_tts("J.A.R.V.I.S já está atualizado.")
            return None
            
    except requests.exceptions.RequestException as e:
        memory_manager.log_activity(f"Erro ao verificar atualizações: {e}", "ERROR")
        notify_tts("Erro ao verificar atualizações do J.A.R.V.I.S.")
        return None
    except json.JSONDecodeError:
        memory_manager.log_activity("Erro ao decodificar JSON da URL de atualização.", "ERROR")
        return None
    except Exception as e:
        memory_manager.log_activity(f"Erro inesperado ao verificar atualizações: {e}", "ERROR")
        notify_tts("Erro inesperado na autoatualização.")
        return None

def create_backup() -> str:
    """
    Cria um backup do diretório atual do projeto antes de uma atualização.
    
    Returns:
        Caminho para o diretório de backup.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"jarvis_backup_{timestamp}")
    
    memory_manager.log_activity(f"Criando backup do projeto em: {backup_path}")
    notify_tts("Criando backup do J.A.R.V.I.S antes da atualização.")
    
    try:
        shutil.copytree(PROJECT_ROOT, backup_path, ignore=shutil.ignore_patterns(".git", "__pycache__", "venv", "node_modules"))
        memory_manager.log_activity("Backup criado com sucesso.")
        return backup_path
    except Exception as e:
        memory_manager.log_activity(f"Erro ao criar backup: {e}", "ERROR")
        notify_tts("Erro ao criar backup do J.A.R.V.I.S.")
        return ""

def apply_updates(update_info: dict) -> bool:
    """
    Baixa e aplica as atualizações.
    
    Args:
        update_info: Dicionário com informações da atualização (latest_version, download_url, checksum).
        
    Returns:
        True se as atualizações foram aplicadas com sucesso, False caso contrário.
    """
    if not update_info:
        return False

    latest_version = update_info["version"]
    download_url = update_info["download_url"]
    checksum = update_info["checksum"]

    memory_manager.log_activity(f"Aplicando atualizações para a versão {latest_version}...")
    notify_tts(f"Aplicando atualizações para o J.A.R.V.I.S versão {latest_version}.")
    
    backup_path = create_backup()
    if not backup_path:
        memory_manager.log_activity("Não foi possível criar backup, abortando atualização.", "ERROR")
        notify_tts("Atualização abortada devido a falha no backup.")
        return False
    
    temp_zip_path = os.path.join(os.path.expanduser("~/.jarvis_temp"), f"jarvis_update_{latest_version}.zip")
    os.makedirs(os.path.dirname(temp_zip_path), exist_ok=True)

    try:
        # 1. Baixar o arquivo de atualização
        memory_manager.log_activity(f"Baixando atualização de {download_url}...")
        response = requests.get(download_url, stream=True, timeout=300)
        response.raise_for_status()
        with open(temp_zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        memory_manager.log_activity("Download concluído.")

        # 2. Verificar o checksum (implementação simplificada, pode usar hashlib)
        # if not verify_checksum(temp_zip_path, checksum):
        #     raise Exception("Falha na verificação do checksum do arquivo de atualização.")

        # 3. Extrair e substituir arquivos
        memory_manager.log_activity("Extraindo e substituindo arquivos...")
        # Cuidado: esta operação sobrescreve arquivos. Idealmente, usar um patch ou merge inteligente.
        # Para simplificar, vamos extrair para um temp dir e depois copiar.
        temp_extract_dir = os.path.join(os.path.expanduser("~/.jarvis_temp"), f"jarvis_update_extracted_{latest_version}")
        shutil.unpack_archive(temp_zip_path, temp_extract_dir)

        # Copiar novos arquivos para o PROJECT_ROOT, sobrescrevendo os antigos
        for src_dir, dirs, files in os.walk(temp_extract_dir):
            dst_dir = src_dir.replace(temp_extract_dir, PROJECT_ROOT, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                shutil.copy2(src_file, dst_file) # copy2 mantém metadados
        
        # 4. Reinstalar dependências com o novo instalador
        memory_manager.log_activity("Reinstalando e verificando dependências com JarvisInstaller...")
        installer = JarvisInstaller(PROJECT_ROOT)
        installer.install_python_dependencies() # Apenas Python, sistema já deve estar ok

        set_current_version(latest_version)
        memory_manager.log_activity("Atualizações aplicadas com sucesso.")
        notify_tts("J.A.R.V.I.S atualizado com sucesso. Reinicie para aplicar as mudanças.")
        return True

    except Exception as e:
        memory_manager.log_activity(f"Erro ao aplicar atualizações: {e}", "ERROR")
        notify_tts("Erro ao aplicar atualizações do J.A.R.V.I.S. Tentando reverter.")
        # Tentar reverter usando o backup
        try:
            if backup_path and os.path.exists(backup_path):
                memory_manager.log_activity(f"Revertendo para o backup: {backup_path}", "INFO")
                # Limpar o diretório atual e restaurar do backup
                for item in os.listdir(PROJECT_ROOT):
                    if item not in [".git", ".jarvis_backups", ".jarvis_temp"]:
                        item_path = os.path.join(PROJECT_ROOT, item)
                        if os.path.isfile(item_path): os.remove(item_path)
                        elif os.path.isdir(item_path): shutil.rmtree(item_path)
                shutil.copytree(backup_path, PROJECT_ROOT, dirs_exist_ok=True)
                memory_manager.log_activity("Reversão para a versão anterior bem-sucedida.", "INFO")
                notify_tts("J.A.R.V.I.S revertido para a versão anterior.")
            else:
                memory_manager.log_activity("Backup não encontrado para reversão.", "CRITICAL")
                notify_tts("Erro crítico! Falha na atualização e na reversão. Verifique manualmente.")
        except Exception as rollback_e:
            memory_manager.log_activity(f"Erro ao reverter: {rollback_e}", "CRITICAL")
            notify_tts("Erro crítico! Falha na atualização e na reversão. Verifique manualmente.")
        return False
    finally:
        # Limpar arquivos temporários
        if os.path.exists(temp_zip_path): os.remove(temp_zip_path)
        # if os.path.exists(temp_extract_dir): shutil.rmtree(temp_extract_dir)

def auto_update_cycle():
    """
    Executa um ciclo completo de verificação e aplicação de atualizações.
    """
    update_info = check_for_updates()
    if update_info:
        apply_updates(update_info)
    else:
        memory_manager.log_activity("Nenhuma atualização para aplicar.")

if __name__ == "__main__":
    import argparse
    
    # Criar o arquivo VERSION se não existir e definir a versão inicial
    if not os.path.exists(VERSION_FILE):
        set_current_version("0.0.0")

    parser = argparse.ArgumentParser(description="Módulo de Autoatualização do J.A.R.V.I.S")
    parser.add_argument("--check", action="store_true", help="Apenas verificar por atualizações")
    parser.add_argument("--apply", action="store_true", help="Aplicar atualizações")
    args = parser.parse_args()
    
    if args.check:
        check_for_updates()
    elif args.apply:
        update_info = check_for_updates()
        if update_info:
            apply_updates(update_info)
        else:
            print("Nenhuma atualização disponível para aplicar.")
    else:
        auto_update_cycle()

