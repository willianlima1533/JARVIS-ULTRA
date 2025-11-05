#!/usr/bin/env bash

# scripts/stop_assistente.sh
# Para o assistente de voz J.A.R.V.I.S

PID_FILE="$HOME/.jarvis_assistente.pid"
PROJECT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"

echo "=========================================="
echo "🛑 Parando J.A.R.V.I.S"
echo "=========================================="

if [ ! -f "$PID_FILE" ]; then
    echo "❌ J.A.R.V.I.S não está rodando (PID file não encontrado)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "Tentando parar o processo PID: $PID graciosamente..."
    # Envia um SIGTERM para o processo Python, que pode ser capturado para um desligamento limpo
    kill -SIGTERM "$PID"
    
    # Aguardar um tempo para o processo Python realizar o desligamento
    for i in {1..10}; do # Espera até 10 segundos
        if ! ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ J.A.R.V.I.S parado graciosamente."
            rm "$PID_FILE"
            exit 0
        fi
        sleep 1
    done
    
    echo "⚠️  Processo não parou após tentativa graciosa. Forçando..."
    kill -9 "$PID"
    
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ J.A.R.V.I.S parado forçadamente."
        rm "$PID_FILE"
    else
        echo "❌ Falha ao parar J.A.R.V.I.S mesmo com kill -9. Intervenção manual pode ser necessária."
    fi
else
    echo "⚠️  Processo $PID não está rodando ou já parou."
    rm -f "$PID_FILE" # Remover arquivo PID se o processo não existir
fi

