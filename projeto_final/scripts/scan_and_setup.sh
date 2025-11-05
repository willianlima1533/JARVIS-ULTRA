#!/data/data/com.termux/files/usr/bin/bash

# scripts/scan_and_setup.sh
# Orquestra o escaneamento de projetos e a configuração de ambientes.

PROJECT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"

echo "[SETUP] Iniciando escaneamento e configuração de ambientes..."

# 1. Escanear projetos
python "$PROJECT_DIR/core/project_scan.py" --dirs "$HOME/storage/downloads" "$HOME/projects" --data-dir "$PROJECT_DIR/data"

if [ $? -ne 0 ]; then
    echo "[SETUP] Erro ao escanear projetos."
    exit 1
fi

echo "[SETUP] Projetos escaneados. Configurando ambientes..."

# 2. Configurar ambientes
python "$PROJECT_DIR/core/env_manager.py" --index "$PROJECT_DIR/data/index.json"

if [ $? -ne 0 ]; then
    echo "[SETUP] Erro ao configurar ambientes de projetos."
    exit 1
fi

echo "[SETUP] Escaneamento e configuração de ambientes concluídos."

