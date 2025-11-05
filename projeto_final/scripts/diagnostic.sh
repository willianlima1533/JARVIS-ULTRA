#!/data/data/com.termux/files/usr/bin/bash

# scripts/diagnostic.sh
# Diagnóstico do ambiente J.A.R.V.I.S

echo "=========================================="
echo "🔍 J.A.R.V.I.S - Diagnóstico do Sistema"
echo "=========================================="

# Função para verificar comando
check_command() {
    local cmd=$1
    local name=$2
    
    if command -v "$cmd" &> /dev/null; then
        version=$($cmd --version 2>&1 | head -n 1)
        echo "✅ $name: $version"
        return 0
    else
        echo "❌ $name: MISSING"
        return 1
    fi
}

# Função para verificar módulo Python
check_python_module() {
    local module=$1
    
    if python -c "import $module" 2>/dev/null; then
        echo "✅ Python module '$module': OK"
        return 0
    else
        echo "❌ Python module '$module': MISSING"
        return 1
    fi
}

echo ""
echo "📦 Ferramentas do Sistema:"
echo "---"

check_command "python" "Python"
check_command "pip" "Pip"
check_command "node" "Node.js"
check_command "npm" "NPM"
check_command "git" "Git"
check_command "unzip" "Unzip"
check_command "ffmpeg" "FFmpeg"

echo ""
echo "🎤 Ferramentas de Voz (Termux):"
echo "---"

check_command "termux-tts-speak" "Termux TTS"
check_command "termux-microphone-record" "Termux Microphone"
check_command "arecord" "ALSA Record"

echo ""
echo "🐍 Módulos Python Essenciais:"
echo "---"

check_python_module "streamlit"
check_python_module "flask"
check_python_module "virtualenv"

echo ""
echo "🔊 Módulos Python de Voz:"
echo "---"

check_python_module "gtts"
check_python_module "pyttsx3"
check_python_module "vosk"
check_python_module "pyaudio"

echo ""
echo "🤖 Módulos Python de IA:"
echo "---"

check_python_module "huggingface_hub"

echo ""
echo "📁 Estrutura de Diretórios:"
echo "---"

PROJECT_DIR="$HOME/projects/projeto_final"

if [ -d "$PROJECT_DIR" ]; then
    echo "✅ Projeto instalado em: $PROJECT_DIR"
    
    if [ -d "$PROJECT_DIR/core" ]; then
        echo "✅ Módulo core: OK"
    else
        echo "❌ Módulo core: MISSING"
    fi
    
    if [ -d "$PROJECT_DIR/engineer" ]; then
        echo "✅ Módulo engineer: OK"
    else
        echo "❌ Módulo engineer: MISSING"
    fi
    
    if [ -d "$PROJECT_DIR/interface" ]; then
        echo "✅ Módulo interface: OK"
    else
        echo "❌ Módulo interface: MISSING"
    fi
    
    if [ -d "$PROJECT_DIR/scripts" ]; then
        echo "✅ Scripts: OK"
    else
        echo "❌ Scripts: MISSING"
    fi
else
    echo "❌ Projeto não encontrado em: $PROJECT_DIR"
fi

echo ""
echo "🔑 Permissões de Armazenamento:"
echo "---"

if [ -d "$HOME/storage" ]; then
    echo "✅ Acesso ao armazenamento: OK"
    if [ -d "$HOME/storage/downloads" ]; then
        echo "✅ Pasta downloads acessível"
    else
        echo "⚠️  Pasta downloads não encontrada"
    fi
else
    echo "❌ Acesso ao armazenamento: MISSING"
    echo "   Execute: termux-setup-storage"
fi

echo ""
echo "=========================================="
echo "📊 Resumo do Diagnóstico"
echo "=========================================="
echo ""
echo "Se algum item estiver MISSING, execute:"
echo "  bash $PROJECT_DIR/scripts/install_termux.sh"
echo ""
echo "Para configurar armazenamento, execute:"
echo "  termux-setup-storage"
echo ""

