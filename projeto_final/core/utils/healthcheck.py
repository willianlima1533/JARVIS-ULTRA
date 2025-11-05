import time, json, os, random
from datetime import datetime

class HealthCheck:
    def __init__(self):
        self.start_time = time.time()
        self.daily_goal = (50, 1000)  # meta configurada: 50 → 1000 por dia
        self.balance = 1000.0
        self.demo_trades = []
        self.last_check = datetime.now()

    def simulate_trade(self):
        # simula operações em modo demo inteligente
        result = random.uniform(-3, 7)  # variação aleatória por trade
        self.balance += result
        self.demo_trades.append(result)
        if len(self.demo_trades) > 100:
            self.demo_trades.pop(0)
        return result

    def status(self):
        uptime = round(time.time() - self.start_time, 2)
        profit = round(sum(self.demo_trades), 2)
        progress = round(((profit - self.daily_goal[0]) / (self.daily_goal[1]-self.daily_goal[0])) * 100, 2)
        progress = min(max(progress, 0), 100)
        return {
            "uptime_s": uptime,
            "balance": round(self.balance, 2),
            "profit_today": profit,
            "progress_percent": progress,
            "last_check": str(self.last_check),
            "trades_demo_count": len(self.demo_trades),
            "mode": os.getenv("JARVIS_MODE", "dry_run"),
            "silent_mode": True,
        }

health = HealthCheck()

if __name__ == "__main__":
    for i in range(5):
        health.simulate_trade()
    print(json.dumps(health.status(), indent=2))
