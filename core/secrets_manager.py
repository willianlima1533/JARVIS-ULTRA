import os
import json
from cryptography.fernet import Fernet
from typing import Optional, Dict, Any

# Caminhos de arquivo
KEY_FILE = "secure.key"
SECRETS_FILE = "secrets.json.enc"

def _load_key() -> Optional[bytes]:
    """Carrega a chave de criptografia do arquivo secure.key."""
    try:
        with open(KEY_FILE, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo de chave '{KEY_FILE}' não encontrado. Execute o script de instalação.")
        return None

def _get_fernet() -> Optional[Fernet]:
    """Retorna uma instância de Fernet se a chave estiver disponível."""
    key = _load_key()
    if key:
        return Fernet(key)
    return None

def encrypt_secrets(secrets: Dict[str, Any]) -> bool:
    """Criptografa o dicionário de segredos e salva no arquivo SECRETS_FILE."""
    fernet = _get_fernet()
    if not fernet:
        return False

    try:
        secrets_json = json.dumps(secrets).encode()
        encrypted_data = fernet.encrypt(secrets_json)
        with open(SECRETS_FILE, "wb") as f:
            f.write(encrypted_data)
        print(f"✅ Segredos criptografados e salvos em '{SECRETS_FILE}'.")
        return True
    except Exception as e:
        print(f"ERRO ao criptografar segredos: {e}")
        return False

def decrypt_secrets() -> Optional[Dict[str, Any]]:
    """Descriptografa e carrega os segredos do arquivo SECRETS_FILE."""
    fernet = _get_fernet()
    if not fernet:
        return None

    try:
        with open(SECRETS_FILE, "rb") as f:
            encrypted_data = f.read()
        
        decrypted_data = fernet.decrypt(encrypted_data)
        secrets = json.loads(decrypted_data.decode())
        return secrets
    except FileNotFoundError:
        print(f"AVISO: Arquivo de segredos '{SECRETS_FILE}' não encontrado. Credenciais MT5 não carregadas.")
        return None
    except Exception as e:
        print(f"ERRO ao descriptografar segredos. Chave incorreta ou arquivo corrompido: {e}")
        return None

# Função de inicialização para o usuário
def setup_mt5_credentials(login: str, password: str, server: str, path: str = None):
    """
    Criptografa e salva as credenciais MT5.
    path: Caminho opcional para o MetaTrader5.exe (apenas Windows).
    """
    mt5_secrets = {
        "MT5_LOGIN": login,
        "MT5_PASSWORD": password,
        "MT5_SERVER": server,
        "MT5_PATH": path
    }
    print("Iniciando criptografia das credenciais MT5...")
    encrypt_secrets({"mt5": mt5_secrets})

def get_mt5_credentials() -> Optional[Dict[str, str]]:
    """Carrega e retorna as credenciais MT5 descriptografadas."""
    secrets = decrypt_secrets()
    if secrets and "mt5" in secrets:
        return secrets["mt5"]
    return None

if __name__ == '__main__':
    # Exemplo de uso (será removido após a integração)
    # Apenas para teste local
    print("Módulo de gerenciamento de segredos carregado.")
    # Para testar, crie um arquivo 'secure.key' e chame setup_mt5_credentials()
    # setup_mt5_credentials("41996359", "85,20dY!", "FBS-Real")
    # creds = get_mt5_credentials()
    # print(f"Credenciais carregadas: {creds}")
