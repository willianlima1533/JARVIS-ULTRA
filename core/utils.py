
#!/usr/bin/env python3
# core/utils.py
"""
Funções utilitárias diversas para o J.A.R.V.I.S.
"""
import subprocess
import os
import sys
import json
from typing import Tuple, Any

# --- Funções de Notificação TTS ---
def notify_tts(text: str):
    """
    Usa termux-tts-speak para falar o texto fornecido no Termux.
    Em outros sistemas, pode ser substituído por uma implementação diferente.
    """
    if "TERMUX_VERSION" in os.environ:
        try:
            subprocess.run(["termux-tts-speak", text], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            print("Erro: 'termux-tts-speak' não encontrado. Certifique-se de que o Termux:API está instalado e configurado.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar termux-tts-speak: {e.stderr.decode().strip()}")
    else:
        # Implementação para outros sistemas operacionais (ex: macOS, Linux com espeak, Windows com SAPI)
        # Por simplicidade, vamos apenas imprimir para o console por enquanto.
        print(f"[TTS] {text}")

# --- Funções de Execução de Comando ---
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

# --- Funções de Configuração (Exemplo, pode ser movido para env_manager se for específico) ---
def get_config(key: str, default: Any = None) -> Any:
    """
    Obtém uma configuração do arquivo de configuração global do Jarvis.
    """
    config_path = os.path.expanduser("~/.jarvis_config.json")
    if not os.path.exists(config_path):
        return default
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config.get(key, default)

def set_config(key: str, value: Any):
    """
    Define uma configuração no arquivo de configuração global do Jarvis.
    """
    config_path = os.path.expanduser("~/.jarvis_config.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    
    config[key] = value
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

if __name__ == "__main__":
    print("Testando notify_tts...")
    notify_tts("Olá, eu sou o Jarvis. Teste de fala.")

    print("\nTestando run_command...")
    success, output = run_command(["echo", "Hello from run_command!"])
    print(f"Sucesso: {success}, Output: {output.strip()}")

    print("\nTestando get_config e set_config...")
    set_config("test_key", "test_value")
    print(f"Valor de test_key: {get_config('test_key')}")
    print(f"Valor de non_existent_key (default None): {get_config('non_existent_key')}")
    print(f"Valor de non_existent_key (default 123): {get_config('non_existent_key', 123)}")
    
    # Limpar arquivo de configuração de teste
    config_path = os.path.expanduser("~/.jarvis_config.json")
    if os.path.exists(config_path):
        os.remove(config_path)
        print("Arquivo de configuração de teste limpo.")

