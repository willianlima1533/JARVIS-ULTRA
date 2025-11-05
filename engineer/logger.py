#!/usr/bin/env python3
# engineer/logger.py
"""
Sistema de logging estruturado em JSON.
"""
import logging
import json
import sys
import os
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formatador que gera logs em formato JSON."""
    
    def format(self, record):
        """
        Formata um registro de log como JSON.
        
        Args:
            record: Registro de log
            
        Returns:
            String JSON do log
        """
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adicionar informações de exceção se disponível
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        
        # Adicionar campos extras se disponíveis
        if hasattr(record, "extra_data"):
            payload["extra"] = record.extra_data
        
        return json.dumps(payload, ensure_ascii=False)

def get_logger(name: str = "projeto_final", level: int = logging.INFO, logfile: str = None) -> logging.Logger:
    """
    Cria ou retorna um logger configurado.
    
    Args:
        name: Nome do logger
        level: Nível de log (INFO, DEBUG, etc.)
        logfile: Caminho do arquivo de log (opcional)
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar adicionar handlers duplicados
    if not logger.handlers:
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(JSONFormatter())
        logger.addHandler(console_handler)
        
        # Handler para arquivo se especificado
        if logfile:
            logdir = os.path.dirname(logfile)
            if logdir and not os.path.exists(logdir):
                os.makedirs(logdir, exist_ok=True)
            
            file_handler = logging.FileHandler(logfile, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(JSONFormatter())
            logger.addHandler(file_handler)
    
    return logger

def log_with_extra(logger: logging.Logger, level: str, message: str, **kwargs):
    """
    Loga uma mensagem com dados extras.
    
    Args:
        logger: Logger a usar
        level: Nível de log ('info', 'debug', 'warning', 'error')
        message: Mensagem de log
        **kwargs: Dados extras para incluir no log
    """
    log_func = getattr(logger, level.lower())
    
    # Criar um LogRecord com dados extras
    extra = {"extra_data": kwargs}
    log_func(message, extra=extra)

if __name__ == "__main__":
    # Teste do logger
    test_logger = get_logger("test", level=logging.DEBUG, logfile="test.log")
    
    test_logger.info("Teste de log INFO")
    test_logger.debug("Teste de log DEBUG")
    test_logger.warning("Teste de log WARNING")
    test_logger.error("Teste de log ERROR")
    
    log_with_extra(test_logger, "info", "Teste com dados extras", user="admin", action="test")
    
    try:
        raise ValueError("Teste de exceção")
    except Exception:
        test_logger.exception("Exceção capturada")
    
    print("\nLogs salvos em: test.log")

