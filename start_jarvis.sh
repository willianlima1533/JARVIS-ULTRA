#!/bin/bash

echo "🔍 Detectando ambiente Termux..."

if [ -n "$PREFIX" ]; then
  echo "✅ Termux detectado. Instalando Ubuntu via proot-distro..."
  pkg update && pkg install proot-distro -y
  proot-distro install ubuntu
  echo "🔁 Entrando no Ubuntu..."
  proot-distro login ubuntu --shared-tmp --bind ~/JARVIS-ULTRA:/root/JARVIS-ULTRA
else
  echo "❌ Este script deve ser executado no Termux."
  exit 1
fi

echo "📦 Instalando dependências no Ubuntu..."
apt update && apt install python3 python3-pip tmux -y
cd /root/JARVIS-ULTRA
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "🔗 Criando aliases permanentes..."
echo "alias jarvis='bash /root/JARVIS-ULTRA/start_jarvis_all.sh'" >> ~/.bashrc
echo "alias jarvis_backend='bash /root/JARVIS-ULTRA/start_jarvis.sh'" >> ~/.bashrc

echo "✅ Instalação concluída. Use 'jarvis' para iniciar o sistema completo."
