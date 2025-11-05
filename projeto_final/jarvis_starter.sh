#!/usr/bin/env bash
# Starter script para rodar JARVIS-ULTRA em modo DEMO/dry-run
source .venv/bin/activate

# Variáveis de configuração (edite conforme necessário)
export JARVIS_MODE="dry_run"
export JARVIS_LOG="./.jarvis_activity.log"
export JARVIS_DISABLE_EXTERNAL_APIS="1"   # evita chamadas externas por segurança

echo "Iniciando JARVIS-ULTRA em modo \$JARVIS_MODE..."
# Se existir assistente_main.py (ou similar), roda ele; senão, roda o README demo
if [ -f core/assistente_main.py ]; then
  python core/assistente_main.py --mode \$JARVIS_MODE 2>&1 | tee -a \$JARVIS_LOG
elif [ -f projeto_final/start_assistente.py ]; then
  python projeto_final/start_assistente.py --mode \$JARVIS_MODE 2>&1 | tee -a \$JARVIS_LOG
else
  echo "Nenhum entrypoint encontrado. Exibindo README e carregando modo demo."
  cat README.md
  # fallback: rodar um pequeno servidor demo (FastAPI) para mostrar o status
  python - <<PY
import time, uvicorn, sys
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def read_root(): return {"status":"jarvis-demo","mode":"dry_run","time":time.ctime()}
if __name__ == "__main__":
    print("Rodando demo FastAPI em http://0.0.0.0:8000 (Ctrl-C para sair)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
PY
fi
