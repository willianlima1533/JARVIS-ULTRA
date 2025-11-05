
#!/usr/bin/env python3
# core/voice_assistant.py
"""
Assistente de voz do J.A.R.V.I.S.
Reconhecimento de fala (VOSK) e síntese de voz (TTS).
"""
import os
import subprocess
import sys
import shutil
import tempfile
import json
import time
from pathlib import Path
from typing import Optional, Tuple, Callable

# Caminho para o modelo VOSK (deve ser baixado pelo install_jarvis.sh)
VOSK_MODEL_DIR = os.path.expanduser("~/vosk-model-small-pt-0.3")

# Adicionar o diretório pai ao path para importações relativas
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar memory_manager e action_router para integração
from core import memory_manager
from core.action_router import route as action_router_route # Renomear para evitar conflito
from core.cognitive_processor import CognitiveProcessor




def check_vosk() -> bool:
    """
    Verifica se VOSK está disponível e o modelo foi baixado.
    """
    try:
        import vosk
        return os.path.exists(VOSK_MODEL_DIR) and os.path.isdir(VOSK_MODEL_DIR)
    except ImportError:
        return False

def listen_termux_mic_continuous(callback: Callable[[str], None], tts_notifier: Callable[[str], None], sample_rate: int = 16000):
    """
    Captura áudio continuamente usando termux-microphone-record e tenta transcrever com VOSK.
    Chama um callback com cada frase reconhecida.
    """
    if not check_vosk():
        print("[VOICE] VOSK não está disponível ou modelo não foi baixado.")
        tts_notifier("Vosk não está configurado para reconhecimento de voz.")
        return

    try:
        import vosk
        model = vosk.Model(VOSK_MODEL_DIR)
        rec = vosk.KaldiRecognizer(model, sample_rate)

        print("[VOICE] Iniciando escuta contínua via termux-microphone-record...")
        tts_notifier("Estou ouvindo. Diga Jarvis para me ativar.")

        # Use sox para gravar áudio em tempo real e encaminhar para VOSK
        # sox -d -r 16000 -c 1 -b 16 -e signed-integer -t raw -
        # -d: dispositivo de áudio padrão
        # -r 16000: taxa de amostragem de 16kHz
        # -c 1: mono
        # -b 16: 16-bit
        # -e signed-integer: formato de inteiro assinado
        # -t raw -: saída raw para stdout

        sox_command = ["rec", "-r", str(sample_rate), "-c", "1", "-b", "16", "-e", "signed-integer", "-t", "raw", "-"]

        # Tentar usar termux-microphone-record se sox não estiver disponível ou for Termux
        # Usar sox para sistemas não-Termux (padrão para o ambiente de sandbox)
        if check_command("rec"):
            process = subprocess.Popen(sox_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("[VOICE] Usando sox para escuta contínua.")
            try:
                while True:
                    data = process.stdout.read(4000) # Ler chunks do stdout do sox
                    if len(data) == 0: break
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result()).get("text", "")
                        if result: callback(result)
                final_result = json.loads(rec.FinalResult()).get("text", "")
                if final_result: callback(final_result)
            except KeyboardInterrupt:
                print("[VOICE] Escuta contínua interrompida.")
            finally:
                process.terminate()
                process.wait()
        
        elif os.environ.get("TERMUX_VERSION"): # Lógica Termux (se necessário)
            print("[VOICE] Usando termux-microphone-record como fallback em Termux.")
            # ... (manter a lógica Termux se for o caso, mas remover do código para simplificar)
            print("[VOICE] Escuta contínua no Termux não implementada neste ambiente.")
            
        else:
            print("[VOICE] Comando 'rec' (SoX) não encontrado. O reconhecimento de voz não funcionará.")
            tts_notifier("Ferramenta de gravação de microfone não encontrada. O reconhecimento de voz não funcionará.")

    except FileNotFoundError:
        print("[VOICE] Comando 'rec' (SoX) ou 'termux-microphone-record' não encontrado. Instale SoX ou Termux:API.")
        tts_notifier("Ferramenta de gravação de microfone não encontrada. Por favor, instale SoX ou Termux API.")
        return
    except Exception as e:
        print(f"[VOICE] Erro no reconhecimento de voz contínuo (VOSK): {e}")
        return

def check_command(cmd: str) -> bool:
    """
    Verifica se um comando existe no PATH.
    """
    return shutil.which(cmd) is not None

class VoiceAssistant:
    def __init__(self, tts_notifier: Callable[[str], None]):
        self.is_listening = False
        self.cognitive_processor = CognitiveProcessor()
        self.notify_tts = tts_notifier

    def process_command(self, text: str):
        """
        Processa o texto reconhecido e o roteia para o action_router.
        """
        print(f"[VOICE] Comando recebido: {text}")
        memory_manager.log_activity(f"Comando de voz: {text}")
        
        # Aqui você pode adicionar lógica para ativar o Jarvis com uma palavra-chave
        # Ex: se o comando começar com "Jarvis", então processar.
        # Caso contrário, apenas logar ou ignorar.
        if text.lower().startswith("jarvis"):
            command_to_route = text[len("jarvis"):].lstrip(', ').strip()
            self.notify_tts(f"Processando seu comando: {command_to_route}")
            # Passar a função action_router_route para o processador cognitivo
            result = self.cognitive_processor.process_command_cognitively(command_to_route, action_router_route)
            print(f"[VOICE] Resultado do processamento cognitivo: {result}")
            
            # Notificar o usuário com a resposta final
            if result.get("success") and isinstance(result.get("result"), str):
                self.notify_tts(result.get("result"))
            elif not result.get("success") and "response" in result:
                # Se falhou, mas há uma resposta cognitiva, notificar.
                self.notify_tts(result.get("response"))
        else:
            print("[VOICE] Comando não direcionado ao Jarvis. Ignorando.")

    def start_listening_loop(self):
        """
        Inicia o loop de escuta contínua.
        """
        self.is_listening = True
        listen_termux_mic_continuous(self.process_command, self.notify_tts)

    def stop_listening_loop(self):
        """
        Para o loop de escuta (ainda não implementado para parar o subprocesso de forma limpa).
        """
        self.is_listening = False
        print("[VOICE] Parando escuta.")
        self.notify_tts("Parando a escuta.")
        # Implementar lógica para parar o subprocesso de gravação de áudio de forma limpa.


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Assistente de Voz J.A.R.V.I.S")
    parser.add_argument("--speak", help="Texto para falar")
    parser.add_argument("--listen-continuous", action="store_true", help="Ouvir comandos de voz continuamente")
    parser.add_argument("--lang", default="pt-BR", help="Idioma (pt-BR, en-US)")
    args = parser.parse_args()
    
    if args.speak:
        # Para testes diretos do módulo, usar a função global de utils
        from core.utils import notify_tts
        notify_tts(args.speak)
    
    elif args.listen_continuous:
        print("Iniciando escuta contínua...")
        from core.utils import notify_tts
        va = VoiceAssistant(notify_tts)
        va.start_listening_loop()
    
    else:
        print("Use --speak 'texto' ou --listen-continuous")


