#!/bin/bash
# ==========================
# 🧠 JARVIS ULTRA - SETUP AUTOMÁTICO INTELIGENTE
# ==========================

# 1️⃣ Preparar ambiente
pkg update -y && pkg upgrade -y
pkg install git python nodejs tmux proot-distro -y

# 2️⃣ Instalar Ubuntu dentro do Termux (caso ainda não tenha)
proot-distro install ubuntu || true

# 3️⃣ Entrar no Ubuntu
proot-distro login ubuntu --shared-tmp <<'EOF'
apt update -y && apt upgrade -y
apt install python3 python3-pip nodejs npm git tmux -y

# 4️⃣ Clonar repositório JARVIS ULTRA
cd ~

# Configuração de autenticação Git (Token Pessoal)
echo ""
echo "=========================================="
echo "🔑 Configuração de Autenticação GitHub"
echo "=========================================="
echo "Para clonar repositórios privados ou evitar limites de taxa, insira seu Token Pessoal (PAT)."
echo "Se você não tiver um, pressione Enter para usar o método anônimo (pode falhar)."
echo ""

read -s -p "Token Pessoal do GitHub (PAT): " GITHUB_PAT
echo

if [ -n "$GITHUB_PAT" ]; then
    # Armazena o token em uma variável de ambiente temporária para o clone
    export GITHUB_TOKEN="$GITHUB_PAT"
    # Usa o token para clonar o repositório
    git clone https://willianlima1533@github.com/willianlima1533/JARVIS-ULTRA.git
    # Configura o git para usar o token para futuras operações (opcional, mas útil)
    git config --global credential.helper store
    echo "https://willianlima1533:$GITHUB_PAT@github.com" > ~/.git-credentials
else
    git clone https://github.com/willianlima1533/JARVIS-ULTRA.git
fi

cd JARVIS-ULTRA

# 5️⃣ Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 6️⃣ Instalar dependências Python e Node
pip install --upgrade pip
pip install -r requirements.txt || true
pip install cryptography flask flask-cors streamlit requests pandas numpy MetaTrader5
npm install -g npm

# 7️⃣ Criar chave de criptografia segura
python3 - <<'PY'
from cryptography.fernet import Fernet
open("secure.key","wb").write(Fernet.generate_key())
print("✅ secure.key criado com sucesso.")
PY

# 8️⃣ Configurar credenciais MT5 (Substitua pelos seus dados)
echo ""
echo "=========================================="
echo "🔑 Configuração de Credenciais MT5"
echo "=========================================="
echo "Atenção: A senha temporária da imagem tem validade de 24h."
echo "Você deve gerar uma nova senha no seu broker e usá-la aqui."
echo ""

# Credenciais da imagem (apenas para referência)
# Login: 41996359
# Senha: 85,20dY!
# Servidor: FBS-Real

read -p "Login MT5 (Acesso): " MT5_LOGIN
read -s -p "Senha MT5 (Gerada no Broker): " MT5_PASSWORD
echo
read -p "Servidor MT5 (Ex: FBS-Real): " MT5_SERVER

python3 - <<PY
from core.secrets_manager import setup_mt5_credentials
setup_mt5_credentials("$MT5_LOGIN", "$MT5_PASSWORD", "$MT5_SERVER")
PY

# 9️⃣ Subir tudo com TMUX (modo autônomo)
tmux kill-session -t jarvis_backend 2>/dev/null || true
tmux kill-session -t jarvis_ui 2>/dev/null || true

tmux new-session -d -s jarvis_backend 'source venv/bin/activate && python3 core/assistente_main.py'
tmux new-session -d -s jarvis_ui 'source venv/bin/activate && streamlit run interface/streamlit_dashboard.py --server.port 8501'

# 🔟 Configurar inicialização automática no Termux/Ubuntu
# O Termux não usa .bashrc para login não interativo, mas o Ubuntu dentro do proot-distro sim.
# Vamos criar um script de inicialização que verifica se o JARVIS já está rodando.

# Script de inicialização para o Ubuntu (dentro do proot-distro)
cat <<'INIT_SCRIPT' > ~/.bashrc_jarvis_init
# Script de inicialização automática do JARVIS-ULTRA
# Executado ao entrar no proot-distro login ubuntu

# Verifica se a sessão TMUX do backend já está ativa
if ! tmux has-session -t jarvis_backend 2>/dev/null; then
    echo "Iniciando JARVIS-ULTRA automaticamente..."
    cd ~/JARVIS-ULTRA
    source venv/bin/activate
    
    # Inicia o backend e a UI em sessões TMUX separadas
    tmux new-session -d -s jarvis_backend 'python3 core/assistente_main.py'
    tmux new-session -d -s jarvis_ui 'streamlit run interface/streamlit_dashboard.py --server.port 8501'
    
    echo "🚀 JARVIS-ULTRA iniciado em segundo plano."
    echo "🌐 Interface: http://localhost:8501"
    echo "Para ver logs: tmux attach -t jarvis_backend"
fi
INIT_SCRIPT

# Adicionar a chamada ao script de inicialização no .bashrc principal do Ubuntu
echo 'source ~/.bashrc_jarvis_init' >> ~/.bashrc

# 🔟 Mostrar status
echo ""
echo "🚀 JARVIS-ULTRA está em execução!"
echo "🌐 Interface: http://localhost:8501"
echo "⚙️ Backend:   rodando em tmux (sessão jarvis_backend)"
echo ""
echo "Para ver logs em tempo real:"
echo "tmux attach -t jarvis_backend  # backend"
echo "tmux attach -t jarvis_ui       # interface"
echo ""
echo "✅ Tudo pronto."
EOF
