#!/data/data/com.termux/files/usr/bin/bash

# scripts/install_termux.sh
# Script de instalação completo para J.A.R.V.I.S no Termux

PROJECT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"

echo "=========================================="
echo "🚀 Instalando J.A.R.V.I.S Ultra Autoevolutivo"
echo "=========================================="

# 1. Atualizar repositórios
echo "\n[1/7] Atualizando repositórios..."
pkg update -y

# 2. Instalar dependências do sistema
echo "\n[2/7] Instalando dependências do sistema..."
pkg install -y python nodejs git unzip ffmpeg termux-api

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências do sistema."
    exit 1
fi
echo "✅ Dependências do sistema instaladas."

# 3. Atualizar pip
echo "\n[3/7] Atualizando pip..."
python -m pip install --upgrade pip setuptools wheel

# 4. Instalar dependências Python essenciais
echo "\n[4/7] Instalando dependências Python essenciais..."
python -m pip install -r "$PROJECT_DIR/requirements.txt"

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências Python essenciais."
    exit 1
fi
echo "✅ Dependências Python essenciais instaladas."

# 5. Instalar módulos de voz
echo "\n[5/7] Instalando módulos de voz..."

# gTTS (online)
python -m pip install gTTS

# pyttsx3 (offline, pode não funcionar bem no Termux)
python -m pip install pyttsx3

# PyAudio (para VOSK)
echo "Tentando instalar PyAudio..."
python -m pip install pyaudio
if [ $? -ne 0 ]; then
    echo "⚠️  PyAudio falhou. Tentando com portaudio..."
    pkg install -y portaudio
    python -m pip install pyaudio
fi

# VOSK (reconhecimento de voz offline)
echo "Instalando VOSK..."
python -m pip install vosk

# Baixar modelo VOSK português (pequeno)
VOSK_MODEL_DIR="$HOME/vosk-model-small-pt-0.3"
if [ ! -d "$VOSK_MODEL_DIR" ]; then
    echo "Baixando modelo VOSK português..."
    cd ~
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
    if [ $? -eq 0 ]; then
        unzip -q vosk-model-small-pt-0.3.zip
        rm vosk-model-small-pt-0.3.zip
        echo "✅ Modelo VOSK baixado."
    else
        echo "⚠️  Falha ao baixar modelo VOSK. Reconhecimento de voz offline não estará disponível."
    fi
    cd "$PROJECT_DIR"
else
    echo "✅ Modelo VOSK já existe."
fi

echo "✅ Módulos de voz instalados."

# 6. Configurar estrutura de diretórios
echo "\n[6/7] Configurando estrutura de diretórios..."
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/history"
mkdir -p "$HOME/.jarvis_backups"
mkdir -p "$HOME/projects"

# Inicializar arquivos de memória
python -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
from core import memory_manager
memory_manager.ensure_memory()
print('Memória inicializada.')
"

echo "✅ Estrutura de diretórios configurada."

# 7. Criar atalhos
echo "\n[7/7] Criando atalhos..."
python "$PROJECT_DIR/core/shortcuts_manager.py" --dashboard

if [ $? -ne 0 ]; then
    echo "⚠️  Erro ao criar atalhos."
fi
echo "✅ Atalhos criados em ~/.shortcuts."

echo "\n=========================================="
echo "🎉 Instalação do J.A.R.V.I.S CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "  1. Configure o armazenamento (se ainda não fez):"
echo "     termux-setup-storage"
echo ""
echo "  2. Inicie o assistente:"
echo "     bash $PROJECT_DIR/scripts/start_assistente.sh"
echo ""
echo "  3. Ou abra o dashboard:"
echo "     ~/.shortcuts/open_dashboard.sh"
echo ""

