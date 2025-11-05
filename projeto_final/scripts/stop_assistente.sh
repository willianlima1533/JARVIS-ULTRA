#!/data/data/com.termux/files/usr/bin/bash

# scripts/stop_assistente.sh
# Para o assistente de voz J.A.R.V.I.S

PID_FILE="$HOME/.jarvis_assistente.pid"

echo "=========================================="
echo "🛑 Parando J.A.R.V.I.S"
echo "=========================================="

if [ ! -f "$PID_FILE" ]; then
    echo "❌ J.A.R.V.I.S não está rodando (PID file não encontrado)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "Parando processo PID: $PID"
    kill "$PID"
    
    # Aguardar um pouco
    sleep 2
    
    # Verificar se parou
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Processo não parou. Forçando..."
        kill -9 "$PID"
    fi
    
    rm "$PID_FILE"
    echo "✅ J.A.R.V.I.S parado"
else
    echo "⚠️  Processo $PID não está rodando"
    rm "$PID_FILE"
fi

