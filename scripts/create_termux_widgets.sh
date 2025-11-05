#!/data/data/com.termux/files/usr/bin/bash

# scripts/create_termux_widgets.sh
# Este script é chamado pelo shortcuts_manager.py para criar atalhos de widget.
# No contexto do Termux, os atalhos são criados no diretório ~/.shortcuts
# e são automaticamente detectados pelo widget do Termux.

# Este script em si não faz nada além de ser um placeholder ou para ser chamado
# pelo Python para garantir que o diretório ~/.shortcuts exista e tenha as permissões corretas.

SHORTCUTS_DIR="$HOME/.shortcuts"

mkdir -p "$SHORTCUTS_DIR"
chmod 700 "$SHORTCUTS_DIR"

echo "[WIDGETS] Diretório de atalhos do Termux garantido: $SHORTCUTS_DIR"
echo "[WIDGETS] Os atalhos serão criados pelo core/shortcuts_manager.py."

