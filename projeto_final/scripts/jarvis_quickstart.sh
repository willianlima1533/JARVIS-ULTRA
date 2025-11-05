#!/data/data/com.termux/files/usr/bin/bash

# scripts/jarvis_quickstart.sh
# Script de início rápido do J.A.R.V.I.S
# Executa diagnóstico, instalação e inicialização em sequência

PROJECT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"

echo "=========================================="
echo "⚡ J.A.R.V.I.S Quick Start"
echo "=========================================="

# 1. Diagnóstico
echo "\n🔍 Executando diagnóstico..."
bash "$PROJECT_DIR/scripts/diagnostic.sh"

read -p "\nContinuar com a instalação? (s/n): " choice
if [[ ! "$choice" =~ ^[Ss]$ ]]; then
    echo "Instalação cancelada."
    exit 0
fi

# 2. Garantir acesso ao armazenamento
echo "\n📁 Configurando acesso ao armazenamento..."
if [ ! -d "$HOME/storage" ]; then
    echo "Execute o comando abaixo e permita o acesso:"
    echo "  termux-setup-storage"
    echo ""
    read -p "Pressione Enter após configurar o armazenamento..."
fi

# 3. Instalação
echo "\n📦 Instalando dependências..."
bash "$PROJECT_DIR/scripts/install_termux.sh"

if [ $? -ne 0 ]; then
    echo "❌ Erro na instalação. Verifique os logs acima."
    exit 1
fi

# 4. Iniciar assistente
echo "\n🚀 Iniciando J.A.R.V.I.S..."
bash "$PROJECT_DIR/scripts/start_assistente.sh"

echo "\n=========================================="
echo "✅ J.A.R.V.I.S Quick Start Concluído!"
echo "=========================================="
echo ""
echo "O assistente está rodando em background."
echo "Para ver os logs:"
echo "  tail -f ~/.jarvis_assistente.log"
echo ""
echo "Para abrir o dashboard:"
echo "  ~/.shortcuts/open_dashboard.sh"
echo ""

