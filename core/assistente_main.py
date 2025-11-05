
#!/usr/bin/env python3
# core/assistente_main.py
"""
Loop principal do assistente J.A.R.V.I.S.
Integra reconhecimento de voz contínuo e roteamento de ações.
"""
import sys
import os
from pathlib import Path
import threading
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.voice_assistant import VoiceAssistant
from core.utils import notify_tts
from core import memory_manager
from core import auto_updater

class JarvisMainAssistant:
    def __init__(self):
        self.voice_assistant = VoiceAssistant(tts_notifier=notify_tts)
        self.running = False
        self.listening_thread = None
        self.update_thread = None

    def start(self):
        memory_manager.log_activity("Iniciando J.A.R.V.I.S Main Assistant...")
        notify_tts("J.A.R.V.I.S ativado. Estou pronto.")
        self.running = True
        
        # Iniciar a escuta contínua em uma thread separada
        self.listening_thread = threading.Thread(target=self.voice_assistant.start_listening_loop)
        self.listening_thread.daemon = True # Permite que o programa principal saia mesmo se a thread estiver rodando
        self.listening_thread.start()

        # Iniciar thread de verificação de atualização em segundo plano
        self.update_thread = threading.Thread(target=self._update_checker_loop, daemon=True)
        self.update_thread.start()

        try:
            while self.running:
                # O loop principal pode fazer outras coisas ou simplesmente esperar
                # Por exemplo, verificar o estado do sistema, processar eventos em segundo plano, etc.
                time.sleep(1) # Evita que o loop consuma 100% da CPU
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        memory_manager.log_activity("Parando J.A.R.V.I.S Main Assistant...")
        notify_tts("Desativando J.A.R.V.I.S. Até logo!")
        self.running = False
        self.voice_assistant.stop_listening_loop() # Sinaliza para a thread de escuta parar
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=5) # Espera a thread de escuta terminar
            if self.listening_thread.is_alive():
                print("[MAIN] Aviso: Thread de escuta não terminou em tempo.")
        memory_manager.log_activity("J.A.R.V.I.S Main Assistant parado.")

    def _update_checker_loop(self):
        """
        Loop para verificar atualizações periodicamente.
        """
        while self.running:
            memory_manager.log_activity("Executando verificação de atualização em segundo plano...")
            auto_updater.auto_update_cycle()
            time.sleep(3600) # Verificar a cada hora

if __name__ == "__main__":
    assistant = JarvisMainAssistant()
    assistant.start()

