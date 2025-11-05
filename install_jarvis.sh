#!/usr/bin/env bash

# Script de instalação unificado e inteligente para o J.A.R.V.I.S Ultra Sentient

PROJECT_ROOT_DIR="$(dirname "$(readlink -f "$0")")"

echo "=========================================="
echo "🚀 Iniciando instalação inteligente do J.A.R.V.I.S 🚀"
echo "=========================================="

# Tenta encontrar o executável do python3
if command -v python3 &> /dev/null; then
    PYTHON_EXEC="python3"
elif command -v python &> /dev/null; then
    PYTHON_EXEC="python"
else
    echo "❌ Python não encontrado. Por favor, instale Python 3.8+ e tente novamente."
    exit 1
fi

# Adicionar o diretório raiz do projeto ao PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT_DIR:$PYTHONPATH"

# Executar o JarvisInstaller para lidar com as dependências do sistema e Python
"$PYTHON_EXEC" "$PROJECT_ROOT_DIR/core/jarvis_installer.py"

if [ $? -ne 0 ]; then
    echo "❌ Erro durante a execução do JarvisInstaller. A instalação falhou."
    exit 1
fi

# --- Passos Pós-Instalação ---

echo "\n[Pós-Instalação] Executando tarefas de configuração..."

# 2. Escanear projetos e configurar ambientes
echo "\n[2/3] Escaneando projetos e configurando ambientes..."
"$PYTHON_EXEC" "$PROJECT_ROOT_DIR/core/project_scan.py" --dirs "$HOME/storage/downloads" "$HOME/projects" --data-dir "$PROJECT_ROOT_DIR/data"

if [ $? -ne 0 ]; then
    echo "⚠️  Aviso: Erro ao escanear projetos. Você pode fazer isso manualmente mais tarde."
else
    # Configurar ambientes para os projetos encontrados (usando o env_manager original para projetos)
    "$PYTHON_EXEC" "$PROJECT_ROOT_DIR/core/env_manager.py" --index "$PROJECT_ROOT_DIR/data/index.json"
    if [ $? -ne 0 ]; then
        echo "⚠️  Aviso: Erro ao configurar ambientes de projetos."
    else
        echo "✅ Projetos escaneados e ambientes configurados."
    fi
fi

# 3. Criar atalhos
echo "\n[3/3] Criando atalhos..."
"$PYTHON_EXEC" "$PROJECT_ROOT_DIR/core/shortcuts_manager.py" --index "$PROJECT_ROOT_DIR/data/index.json"

if [ $? -ne 0 ]; then
    echo "⚠️  Aviso: Erro ao criar atalhos."
else
    echo "✅ Atalhos criados em ~/.shortcuts."
fi

echo "\n================================================="
echo "🎉 Instalação principal do J.A.R.V.I.S CONCLUÍDA! 🎉"
echo "================================================="
echo "Para iniciar o dashboard, execute: ~/.shortcuts/open_dashboard.sh"
echo "Para gerenciar projetos, verifique os atalhos em ~/.shortcuts/"

