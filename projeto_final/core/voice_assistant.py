#!/usr/bin/env python3
# core/voice_assistant.py
"""
Assistente de voz do J.A.R.V.I.S.
Reconhecimento de fala (VOSK/Whisper) e síntese de voz (TTS).
"""
import os
import subprocess
import sys
from typing import Optional, Tuple

def check_termux_tts() -> bool:
    """Verifica se termux-tts-speak está disponível."""
    try:
        result = subprocess.run(
            ["which", "termux-tts-speak"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def check_pyttsx3() -> bool:
    """Verifica se pyttsx3 está disponível."""
    try:
        import pyttsx3
        return True
    except ImportError:
        return False

def check_gtts() -> bool:
    """Verifica se gTTS está disponível."""
    try:
        from gtts import gTTS
        return True
    except ImportError:
        return False

def speak_termux(text: str, language: str = "pt-BR") -> bool:
    """Fala usando termux-tts-speak."""
    try:
        # Mapear pt-BR para pt para o Termux TTS
        lang_code = language.split("-")[0] if "-" in language else language
        
        subprocess.run(
            ["termux-tts-speak", "-l", lang_code, text],
            check=True
        )
        return True
    except Exception as e:
        print(f"[VOICE] Erro no termux-tts-speak: {e}")
        return False

def speak_pyttsx3(text: str, language: str = "pt-BR") -> bool:
    """Fala usando pyttsx3."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Configurar voz em português se disponível
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'portuguese' in voice.name.lower() or 'brasil' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"[VOICE] Erro no pyttsx3: {e}")
        return False

def speak_gtts(text: str, language: str = "pt-BR") -> bool:
    """Fala usando gTTS (requer internet)."""
    try:
        from gtts import gTTS
        import tempfile
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        
        # Gerar áudio
        tts = gTTS(text=text, lang=language.split("-")[0], slow=False)
        tts.save(tmp_path)
        
        # Reproduzir
        if sys.platform.startswith('linux'):
            # Tentar termux-media-player primeiro
            try:
                subprocess.run(["termux-media-player", "play", tmp_path], check=True)
            except:
                # Fallback para mpg123 ou ffplay
                try:
                    subprocess.run(["mpg123", tmp_path], check=True)
                except:
                    subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp_path], check=True)
        
        # Limpar arquivo temporário
        os.unlink(tmp_path)
        return True
    except Exception as e:
        print(f"[VOICE] Erro no gTTS: {e}")
        return False

def notify_tts(text: str, language: str = "pt-BR") -> bool:
    """
    Notifica o usuário por voz usando o melhor método disponível.
    
    Args:
        text: Texto para falar
        language: Código do idioma (ex: pt-BR, en-US)
        
    Returns:
        True se conseguiu falar, False caso contrário
    """
    print(f"[VOICE] Falando: {text}")
    
    # Tentar termux-tts-speak primeiro (melhor para Termux)
    if check_termux_tts():
        if speak_termux(text, language):
            return True
    
    # Tentar pyttsx3 (offline, mas pode não funcionar bem no Termux)
    if check_pyttsx3():
        if speak_pyttsx3(text, language):
            return True
    
    # Tentar gTTS (requer internet)
    if check_gtts():
        if speak_gtts(text, language):
            return True
    
    print("[VOICE] Nenhum método de TTS disponível")
    return False

def check_vosk() -> bool:
    """Verifica se VOSK está disponível."""
    try:
        import vosk
        return True
    except ImportError:
        return False

def check_whisper() -> bool:
    """Verifica se Whisper está disponível."""
    try:
        import whisper
        return True
    except ImportError:
        return False

def listen_vosk(timeout: int = 5) -> Optional[str]:
    """
    Captura áudio e reconhece fala usando VOSK.
    
    Args:
        timeout: Tempo máximo de gravação em segundos
        
    Returns:
        Texto reconhecido ou None
    """
    try:
        import vosk
        import pyaudio
        import json
        
        # Configurar modelo VOSK
        model_path = os.path.expanduser("~/vosk-model-small-pt-0.3")
        if not os.path.exists(model_path):
            print(f"[VOICE] Modelo VOSK não encontrado em {model_path}")
            return None
        
        model = vosk.Model(model_path)
        rec = vosk.KaldiRecognizer(model, 16000)
        
        # Capturar áudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000
        )
        stream.start_stream()
        
        print("[VOICE] Ouvindo...")
        
        frames = 0
        max_frames = timeout * 16000 // 8000
        
        while frames < max_frames:
            data = stream.read(8000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    return text
            frames += 1
        
        # Finalizar
        result = json.loads(rec.FinalResult())
        text = result.get("text", "")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        return text if text else None
        
    except Exception as e:
        print(f"[VOICE] Erro no VOSK: {e}")
        return None

def listen(timeout: int = 5, method: str = "auto") -> Optional[str]:
    """
    Captura e reconhece fala.
    
    Args:
        timeout: Tempo máximo de gravação
        method: Método de reconhecimento (auto, vosk, whisper)
        
    Returns:
        Texto reconhecido ou None
    """
    if method == "auto":
        # Tentar VOSK primeiro (mais rápido)
        if check_vosk():
            result = listen_vosk(timeout)
            if result:
                return result
        
        # TODO: Implementar Whisper se necessário
        print("[VOICE] Nenhum método de reconhecimento de fala disponível")
        return None
    
    elif method == "vosk":
        return listen_vosk(timeout)
    
    else:
        print(f"[VOICE] Método desconhecido: {method}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Assistente de Voz J.A.R.V.I.S")
    parser.add_argument("--speak", help="Texto para falar")
    parser.add_argument("--listen", action="store_true", help="Ouvir comando de voz")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout para escuta")
    parser.add_argument("--lang", default="pt-BR", help="Idioma (pt-BR, en-US)")
    args = parser.parse_args()
    
    if args.speak:
        notify_tts(args.speak, args.lang)
    
    elif args.listen:
        text = listen(timeout=args.timeout)
        if text:
            print(f"Reconhecido: {text}")
        else:
            print("Nada reconhecido")
    
    else:
        print("Use --speak 'texto' ou --listen")

