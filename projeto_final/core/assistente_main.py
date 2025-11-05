import time, json, os, threading
from fastapi import FastAPI
import uvicorn
from core.utils.healthcheck import health

app = FastAPI(title="JARVIS ULTRA Silent Mode")

@app.get("/")
def root():
    """Retorna status geral"""
    health.simulate_trade()
    return health.status()

@app.get("/profit")
def profit():
    """Retorna lucro simulado e progresso da meta"""
    return {"profit_today": health.status()["profit_today"],
            "progress_percent": health.status()["progress_percent"]}

def auto_update():
    """Loop silencioso para simular operações"""
    while True:
        health.simulate_trade()
        time.sleep(60)  # simula 1 operação por minuto

if __name__ == "__main__":
    if os.getenv("JARVIS_MODE") == "dry_run":
        threading.Thread(target=auto_update, daemon=True).start()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("Modo real desativado (segurança). Use JARVIS_MODE=dry_run para simular.")
