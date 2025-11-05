#!/usr/bin/env bash

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
        echo "Para parar, execute: bash $PROJECT_DIR/scripts/stop_assistente.sh"
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
    echo "Por favor, execute o script de instalação (install_jarvis.sh) primeiro."
    exit 1
fi

# Iniciar em background usando nohup para que continue rodando após fechar o terminal
nohup python3 "$ASSISTENTE_PY" > "$HOME/.jarvis_assistente.log" 2>&1 &
ASSISTENTE_PID=$!

# Salvar PID
echo "$ASSISTENTE_PID" > "$PID_FILE"

echo "✅ J.A.R.V.I.S iniciado (PID: $ASSISTENTE_PID)"
echo ""
echo "Para ver os logs:"
echo "  tail -f $HOME/.jarvis_assistente.log"
echo ""
echo "Para parar o assistente:"
echo "  bash $PROJECT_DIR/scripts/stop_assistente.sh"
echo ""

