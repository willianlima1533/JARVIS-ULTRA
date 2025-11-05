#!/data/data/com.termux/files/usr/bin/bash

# scripts/start_assistente.sh
# Inicia o assistente de voz J.A.R.V.I.S

PROJECT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"
ASSISTENTE_PY="$PROJECT_DIR/core/assistente_main.py"
PID_FILE="$HOME/.jarvis_assistente.pid"

echo "=========================================="
echo "🤖 Iniciando J.A.R.V.I.S"
echo "=========================================="

# Verificar se já está rodando
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  J.A.R.V.I.S já está rodando (PID: $OLD_PID)"
        echo "Para parar, execute: kill $OLD_PID"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

# Iniciar assistente em background
echo "Iniciando assistente de voz..."

# Verificar se o arquivo existe
if [ ! -f "$ASSISTENTE_PY" ]; then
    echo "❌ Arquivo do assistente não encontrado: $ASSISTENTE_PY"
    echo "Criando arquivo básico..."
    
    cat > "$ASSISTENTE_PY" << 'EOF'
#!/usr/bin/env python3
# core/assistente_main.py
"""
Loop principal do assistente de voz J.A.R.V.I.S.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import memory_manager, voice_assistant, action_router

def main():
    """Loop principal do assistente."""
    memory_manager.log_activity("J.A.R.V.I.S iniciado")
    voice_assistant.notify_tts("J.A.R.V.I.S iniciado e pronto")
    
    print("J.A.R.V.I.S está ouvindo...")
    print("Comandos disponíveis:")
    print("  - 'Jarvis, escaneie downloads'")
    print("  - 'Jarvis, escaneie projetos'")
    print("  - 'Jarvis, configure ambientes'")
    print("\nPressione Ctrl+C para sair\n")
    
    try:
        while True:
            # Aguardar comando de voz
            text = voice_assistant.listen(timeout=10)
            
            if text:
                print(f"Comando reconhecido: {text}")
                memory_manager.log_activity(f"Comando de voz: {text}")
                
                # Processar comando
                text_lower = text.lower()
                
                if "jarvis" in text_lower:
                    if "download" in text_lower or "baixar" in text_lower:
                        voice_assistant.notify_tts("Escaneando downloads")
                        action_router.route("scan_downloads")
                    
                    elif "projeto" in text_lower or "project" in text_lower:
                        voice_assistant.notify_tts("Escaneando projetos")
                        action_router.route("scan_projects")
                    
                    elif "config" in text_lower or "ambiente" in text_lower:
                        voice_assistant.notify_tts("Configurando ambientes")
                        action_router.route("setup")
                    
                    else:
                        voice_assistant.notify_tts("Comando não reconhecido")
            
            # Pequena pausa
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nEncerrando J.A.R.V.I.S...")
        memory_manager.log_activity("J.A.R.V.I.S encerrado")
        voice_assistant.notify_tts("J.A.R.V.I.S encerrado")

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "$ASSISTENTE_PY"
fi

# Iniciar em background
nohup python "$ASSISTENTE_PY" > "$HOME/.jarvis_assistente.log" 2>&1 &
ASSISTENTE_PID=$!

# Salvar PID
echo "$ASSISTENTE_PID" > "$PID_FILE"

echo "✅ J.A.R.V.I.S iniciado (PID: $ASSISTENTE_PID)"
echo ""
echo "Para ver os logs:"
echo "  tail -f $HOME/.jarvis_assistente.log"
echo ""
echo "Para parar o assistente:"
echo "  kill $ASSISTENTE_PID"
echo ""
echo "Ou execute:"
echo "  bash $PROJECT_DIR/scripts/stop_assistente.sh"
echo ""

