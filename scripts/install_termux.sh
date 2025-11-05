#!/data/data/com.termux/files/usr/bin/bash

# scripts/install_termux.sh
# Script de instalação completo para J.A.R.V.I.S no Termux

PROJECT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"

echo "=========================================="
echo "🚀 Instalando J.A.R.V.I.S Ultra Autoevolutivo"
echo "=========================================="

# 1. Atualizar repositórios e instalar dependências do sistema
echo "\n[1/7] Atualizando repositórios e instalando dependências do sistema..."
pkg update -y
pkg upgrade -y
pkg install -y python nodejs git unzip ffmpeg termux-api libsndfile

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências do sistema. Verifique sua conexão e tente novamente."
    exit 1
fi
echo "✅ Dependências do sistema instaladas."

# 2. Atualizar pip
echo "\n[2/7] Atualizando pip..."
python -m pip install --upgrade pip setuptools wheel

if [ $? -ne 0 ]; then
    echo "❌ Erro ao atualizar pip."
    exit 1
fi
echo "✅ Pip atualizado."

# 3. Instalar dependências Python essenciais
echo "\n[3/7] Instalando dependências Python essenciais..."

# Instalar bibliotecas que geralmente funcionam bem
python -m pip install streamlit flask gTTS huggingface-hub virtualenv

# Tentar instalar vosk de forma mais robusta
echo "Tentando instalar vosk..."
python -m pip install vosk
if [ $? -ne 0 ]; then
    echo "⚠️  Falha ao instalar vosk diretamente. Tentando com --no-binary..."
    python -m pip install --no-binary :all: vosk
    if [ $? -ne 0 ]; then
        echo "❌ Falha ao instalar vosk. Reconhecimento de voz offline pode não funcionar."
    else
        echo "✅ vosk instalado com --no-binary."
    fi
else
    echo "✅ vosk instalado."
fi

# pyttsx3 pode ter problemas no Termux, instalar mas avisar
echo "Tentando instalar pyttsx3..."
python -m pip install pyttsx3
if [ $? -ne 0 ]; then
    echo "⚠️  Falha ao instalar pyttsx3. Síntese de voz offline pode não funcionar."
else
    echo "✅ pyttsx3 instalado."
fi

# pyaudio é problemático no Termux, vamos removê-lo do requirements e focar em alternativas
# Se for estritamente necessário, o usuário precisará compilar portaudio e pyaudio manualmente.

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar algumas dependências Python. Verifique os logs acima."
    # Não sair aqui, pois algumas falhas podem ser aceitáveis (ex: pyttsx3)
fi
echo "✅ Dependências Python essenciais instaladas (com possíveis avisos).
"

# 4. Baixar modelo VOSK português (pequeno)
VOSK_MODEL_DIR="$HOME/vosk-model-small-pt-0.3"
if [ ! -d "$VOSK_MODEL_DIR" ]; then
    echo "\n[4/7] Baixando modelo VOSK português..."
    cd ~
    wget -q --show-progress https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
    if [ $? -eq 0 ]; then
        unzip -q vosk-model-small-pt-0.3.zip
        rm vosk-model-small-pt-0.3.zip
        echo "✅ Modelo VOSK baixado."
    else
        echo "⚠️  Falha ao baixar modelo VOSK. Reconhecimento de voz offline não estará disponível."
    fi
    cd "$PROJECT_DIR"
else
    echo "\n[4/7] Modelo VOSK já existe."
fi

# 5. Configurar estrutura de diretórios
echo "\n[5/7] Configurando estrutura de diretórios..."
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

# 6. Inicializar repositório Git (para autoatualização)
echo "\n[6/7] Inicializando repositório Git..."
if [ ! -d "$PROJECT_DIR/.git" ]; then
    cd "$PROJECT_DIR"
    git init
    git branch -M main
    git add .
    git commit -m "Initial commit by J.A.R.V.I.S installer"
    # Adicione o repositório remoto aqui se for conhecido para autoatualização
    # Ex: git remote add origin https://github.com/seu_usuario/seu_repo.git
    cd -
    echo "✅ Repositório Git inicializado."
else
    echo "✅ Repositório Git já existe."
fi

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

