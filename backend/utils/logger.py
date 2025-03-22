# Logger para Sistema FORCA #

import logging
import functools
import os
import datetime
import inspect
from typing import Callable, Optional, Any, Dict, Union

# Configurar diretório de logs
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configurar formato de log
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

class WrapperLogger:
    """
    Logger especializado para os wrappers do sistema FORCA.
    Gerencia logs em console e arquivo, com diferentes níveis de detalhe.
    """
    
    def __init__(self, name: str, level: int = logging.INFO, log_to_file: bool = True):
        """
        Inicializa o WrapperLogger com nome e nível específicos.
        
        Args:
            name (str): Nome do logger, geralmente o nome do wrapper
            level (int): Nível de logging (default: logging.INFO)
            log_to_file (bool): Se True, salva logs em arquivo
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Limpar handlers anteriores
        
        # Handler de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(LOG_FORMAT, TIMESTAMP_FORMAT)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Handler de arquivo
        if log_to_file:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            log_filename = f"{today}_{name}.log"
            log_filepath = os.path.join(LOG_DIR, log_filename)
            
            file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(LOG_FORMAT, TIMESTAMP_FORMAT)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Registra mensagem de nível DEBUG."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Registra mensagem de nível INFO."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Registra mensagem de nível WARNING."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Registra mensagem de nível ERROR."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Registra mensagem de nível CRITICAL."""
        self.logger.critical(message)
    
    @staticmethod
    def log_function(level: int = logging.INFO) -> Callable:
        """
        Decorador para registrar entrada e saída de funções.
        
        Args:
            level (int): Nível de logging para este decorador
            
        Returns:
            Callable: Decorador configurado
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                logger = getattr(self, 'logger', None)
                if not logger:
                    return func(self, *args, **kwargs)
                
                # Obter nome da função e argumentos
                func_name = func.__name__
                arg_names = inspect.getfullargspec(func).args[1:]  # pular 'self'
                arg_values = dict(zip(arg_names, args))
                arg_values.update(kwargs)
                
                # Obter argumentos formatados (limitados para evitar logs enormes)
                formatted_args = []
                for name, value in arg_values.items():
                    if isinstance(value, (str, dict, list)) and len(str(value)) > 50:
                        formatted_value = f"{str(value)[:50]}... ({len(str(value))} chars)"
                    else:
                        formatted_value = str(value)
                    formatted_args.append(f"{name}={formatted_value}")
                
                args_str = ", ".join(formatted_args)
                
                # Log de entrada
                if level == logging.INFO:
                    logger.info(f"Iniciando {func_name}({args_str})")
                elif level == logging.DEBUG:
                    logger.debug(f"Iniciando {func_name}({args_str})")
                elif level == logging.WARNING:
                    logger.warning(f"Iniciando {func_name}({args_str})")
                elif level == logging.ERROR:
                    logger.error(f"Iniciando {func_name}({args_str})")
                else:
                    logger.info(f"Iniciando {func_name}({args_str})")
                
                try:
                    # Executar função
                    result = func(self, *args, **kwargs)
                    
                    # Log de saída
                    msg = ""
                    if result is None:
                        msg = f"Concluído {func_name} -> None"
                    elif isinstance(result, (str, dict, list)) and len(str(result)) > 50:
                        msg = f"Concluído {func_name} -> {str(result)[:50]}... ({len(str(result))} chars)"
                    else:
                        msg = f"Concluído {func_name} -> {result}"
                    
                    if level == logging.INFO:
                        logger.info(msg)
                    elif level == logging.DEBUG:
                        logger.debug(msg)
                    elif level == logging.WARNING:
                        logger.warning(msg)
                    elif level == logging.ERROR:
                        logger.error(msg)
                    else:
                        logger.info(msg)
                    
                    return result
                    
                except Exception as e:
                    # Log de erro
                    logger.error(f"Erro em {func_name}: {str(e)}")
                    raise
                    
            return wrapper
        
        return decorator

# Função auxiliar para obter logger com configuração padrão
def get_logger(name: str, level: int = logging.INFO) -> WrapperLogger:
    """
    Obtém um logger configurado com o nome e nível especificados.
    
    Args:
        name (str): Nome do logger
        level (int): Nível de logging (default: logging.INFO)
        
    Returns:
        WrapperLogger: Logger configurado
    """
    return WrapperLogger(name, level)