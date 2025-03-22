# Arquivo de configuração com carregamento de variáveis de ambiente #

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def get_claude_api_key() -> str:
    """
    Obtém a chave da API Claude de fontes seguras.
    
    Returns:
        str: Chave da API Claude
    """
    # API Key armazenada em variável de ambiente
    api_key_env = os.getenv("CLAUDE_API_KEY", "")
    
    if api_key_env and api_key_env.strip():
        return api_key_env.strip()
        
    # API Key armazenada em arquivo .env na raiz
    try:
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("CLAUDE_API_KEY="):
                        key = line[len("CLAUDE_API_KEY="):].strip()
                        if key:
                            return key
    except Exception:
        pass
        
    # Retorna string vazia se não encontrar chave
    return ""

def get_claude_config() -> Dict[str, str]:
    """
    Obtém as configurações de conexão com a API Claude.
    
    Returns:
        Dict: Configurações da API Claude
    """
    return {
        "api_key": get_claude_api_key(),  # Use a função segura
        "api_url": os.getenv("CLAUDE_API_URL", "https://api.anthropic.com/v1/messages"),
        "model": os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
    }

def get_supabase_config() -> Dict[str, str]:
    """
    Obtém as configurações de conexão com a Supabase.
    
    Returns:
        Dict: Configurações da Supabase
    """
    return {
        "url": os.getenv("SUPABASE_URL", ""),
        "api_key": os.getenv("SUPABASE_API_KEY", ""),
        "service_key": os.getenv("SUPABASE_SERVICE_KEY", "")
    }

def get_db_config() -> Dict[str, Any]:
    """
    Obtém as configurações do banco de dados PostgreSQL.
    
    Returns:
        Dict: Configurações do banco de dados
    """
    return {
        "host": os.getenv("DB_HOST", os.getenv("SUPABASE_URL", "").replace("https://", "")),
        "porta": int(os.getenv("DB_PORT", "5432")),
        "usuario": os.getenv("DB_USER", "postgres"),
        "senha": os.getenv("DB_PASSWORD", os.getenv("SUPABASE_SERVICE_KEY", "")),
        "database": os.getenv("DB_NAME", "postgres"),
        "ssl_mode": os.getenv("DB_SSL_MODE", "require")
    }

def get_app_config() -> Dict[str, Any]:
    """
    Obtém as configurações gerais da aplicação.
    
    Returns:
        Dict: Configurações da aplicação
    """
    return {
        "debug": os.getenv("DEBUG", "False").lower() in ("true", "1", "t"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "environment": os.getenv("ENVIRONMENT", "production")
    }

def init_config() -> Dict[str, Dict[str, Any]]:
    """
    Inicializa todas as configurações.
    
    Returns:
        Dict: Todas as configurações
    """
    return {
        "claude": get_claude_config(),
        "supabase": get_supabase_config(),
        "database": get_db_config(),
        "app": get_app_config()
    }

# Configuração global
config = init_config()

def get_config(section: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtém a configuração completa ou uma seção específica.
    
    Args:
        section (str, optional): Nome da seção de configuração
        
    Returns:
        Dict: Configuração completa ou da seção especificada
    """
    if section:
        return config.get(section, {})
    return config