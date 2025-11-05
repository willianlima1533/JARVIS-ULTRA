#!/bin/bash

mkdir -p logs

# Inicia o backend Flask
tmux new-session -d -s jarvis_backend 'python3 core/api_server.py >> logs/backend.log 2>&1'

# Inicia a interface Streamlit
tmux new-session -d -s jarvis_ui 'streamlit run interface.py >> logs/ui.log 2>&1'

echo "✅ JARVIS-ULTRA iniciado com backend e interface."
