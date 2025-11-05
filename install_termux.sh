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
git clone https://github.com/willianlima1533/JARVIS-ULTRA.git
cd JARVIS-ULTRA

# 5️⃣ Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 6️⃣ Instalar dependências Python e Node
pip install --upgrade pip
pip install -r requirements.txt || true
pip install cryptography flask flask-cors streamlit requests pandas numpy
npm install -g npm

# 7️⃣ Criar chave de criptografia segura
python3 - <<'PY'
from cryptography.fernet import Fernet
open("secure.key","wb").write(Fernet.generate_key())
print("✅ secure.key criado com sucesso.")
PY

# 8️⃣ Subir tudo com TMUX (modo autônomo)
tmux kill-session -t jarvis_backend 2>/dev/null || true
tmux kill-session -t jarvis_ui 2>/dev/null || true

tmux new-session -d -s jarvis_backend 'source venv/bin/activate && python3 core/assistente_main.py'
tmux new-session -d -s jarvis_ui 'source venv/bin/activate && streamlit run interface/streamlit_dashboard.py --server.port 8501'

# 9️⃣ Mostrar status
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
