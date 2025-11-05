import MetaTrader5 as mt5
from core.secrets_manager import get_mt5_credentials
from typing import Optional, Dict, Any
import time

class MT5Trader:
    """
    Gerencia a conexão e operações de trading via MetaTrader5.
    """
    def __init__(self):
        self.credentials = get_mt5_credentials()
        self.is_connected = False
        if not self.credentials:
            print("AVISO: Credenciais MT5 não encontradas ou não descriptografadas.")

    def connect(self) -> bool:
        """
        Estabelece a conexão com o MetaTrader 5.
        """
        if not self.credentials:
            print("ERRO: Não é possível conectar. Credenciais MT5 ausentes.")
            return False

        login = int(self.credentials.get("MT5_LOGIN"))
        password = self.credentials.get("MT5_PASSWORD")
        server = self.credentials.get("MT5_SERVER")
        path = self.credentials.get("MT5_PATH") # Ignorado no Termux/Linux

        if not mt5.initialize(login=login, password=password, server=server):
            print(f"ERRO: Falha ao inicializar a conexão MT5. Código: {mt5.last_error()}")
            self.is_connected = False
            return False
        
        self.is_connected = True
        print(f"✅ Conexão MT5 estabelecida com sucesso para o login {login}.")
        return True

    def disconnect(self):
        """
        Finaliza a conexão com o MetaTrader 5.
        """
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            print("✅ Conexão MT5 finalizada.")

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Retorna informações da conta.
        """
        if not self.is_connected:
            if not self.connect():
                return None
        
        info = mt5.account_info()
        if info:
            return info._asdict()
        return None

    def send_order(self, symbol: str, type: int, volume: float, price: float, sl: float = 0.0, tp: float = 0.0) -> Optional[Dict[str, Any]]:
        """
        Envia uma ordem de negociação.
        type: mt5.ORDER_TYPE_BUY ou mt5.ORDER_TYPE_SELL
        """
        if not self.is_connected:
            if not self.connect():
                return None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 10,
            "magic": 202405,
            "comment": "JARVIS_ULTRA_TRADE",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"ERRO ao enviar ordem: {result.comment} (Código: {result.retcode})")
            return None
        
        print(f"✅ Ordem enviada com sucesso. Ticket: {result.order}")
        return result._asdict()

    # Adicione outras funções de trading conforme necessário (ex: get_positions, get_history)

if __name__ == '__main__':
    # Exemplo de uso (apenas para demonstração)
    # Este módulo deve ser importado e usado pelo assistente principal.
    print("Módulo MT5Trader carregado.")
    # Para testar, o arquivo secrets.json.enc deve existir e a chave secure.key deve estar presente.
    # trader = MT5Trader()
    # if trader.connect():
    #     info = trader.get_account_info()
    #     print(info)
    #     trader.disconnect()
