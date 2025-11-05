#!/data/data/com.termux/files/usr/bin/bash

# Script de instalação unificado para o Projeto Final no Termux

PROJECT_DIR="$(dirname "$(readlink -f "$0")")"

echo "=========================================="
echo "🚀 Iniciando instalação do Projeto Final 🚀"
echo "=========================================="

# 1. Instalar dependências do sistema via pkg
echo "\n[1/5] Instalando dependências do sistema (python, nodejs, git, unzip)..."
pkg update -y
pkg upgrade -y
pkg install -y python nodejs git unzip

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências do sistema. Verifique sua conexão e tente novamente."
    exit 1
fi
echo "✅ Dependências do sistema instaladas."

# 2. Atualizar pip
echo "\n[2/5] Atualizando pip..."
python -m pip install --upgrade pip setuptools wheel

if [ $? -ne 0 ]; then
    echo "❌ Erro ao atualizar pip."
    exit 1
fi
echo "✅ Pip atualizado."

# 3. Instalar dependências Python via requirements.txt
echo "\n[3/5] Instalando dependências Python..."

# Tentar instalar faiss-cpu, com fallback para annoy
FAISS_INSTALLED=false
if python -c "import sys; sys.exit(not sys.platform.startswith(\'linux\'))"; then
    echo "Tentando instalar faiss-cpu..."
    python -m pip install faiss-cpu
    if [ $? -eq 0 ]; then
        echo "✅ faiss-cpu instalado com sucesso."
        FAISS_INSTALLED=true
    else
        echo "⚠️ Falha ao instalar faiss-cpu. Usando Annoy como fallback."
    fi
fi

# Instalar outras dependências e Annoy se faiss-cpu não foi instalado
if [ "$FAISS_INSTALLED" = false ]; then
    echo "Instalando dependências restantes e Annoy..."
    python -m pip install -r "$PROJECT_DIR/requirements.txt" annoy
else
    echo "Instalando dependências restantes..."
    python -m pip install -r "$PROJECT_DIR/requirements.txt"
fi

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências Python. Verifique o requirements.txt."
    exit 1
fi
echo "✅ Dependências Python instaladas."

# 4. Configurar o ambiente inicial (scan e setup)
echo "\n[4/5] Escaneando projetos e configurando ambientes..."

# Criar diretórios de dados e histórico se não existirem
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/history"

# Executar o scan de projetos
python "$PROJECT_DIR/core/project_scan.py" --dirs "$HOME/storage/downloads" "$HOME/projects" --data-dir "$PROJECT_DIR/data"

if [ $? -ne 0 ]; then
    echo "❌ Erro ao escanear projetos."
    exit 1
fi

# Configurar ambientes para os projetos encontrados
python "$PROJECT_DIR/core/env_manager.py" --index "$PROJECT_DIR/data/index.json"

if [ $? -ne 0 ]; then
    echo "❌ Erro ao configurar ambientes de projetos."
    exit 1
fi
echo "✅ Projetos escaneados e ambientes configurados."

# 5. Criar atalhos do Termux
echo "\n[5/5] Criando atalhos do Termux..."
python "$PROJECT_DIR/core/shortcuts_manager.py" --index "$PROJECT_DIR/data/index.json"

if [ $? -ne 0 ]; then
    echo "❌ Erro ao criar atalhos do Termux."
    exit 1
fi
echo "✅ Atalhos do Termux criados em ~/.shortcuts."

echo "\n=========================================="
echo "🎉 Instalação do Projeto Final CONCLUÍDA! 🎉"
echo "=========================================="
echo "Para iniciar o dashboard, execute: ~/.shortcuts/open_dashboard.sh"
echo "Para gerenciar projetos, verifique os atalhos em ~/.shortcuts/"

