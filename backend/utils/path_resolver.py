# Path Resolver para Gerenciamento de Caminhos de Arquivos #

import os
import sys
from typing import Optional, List, Tuple
import logging

# Importar logger do projeto
try:
    from .logger import WrapperLogger
    logger = WrapperLogger("PathResolver")
except ImportError:
    # Fallback para logging padrão caso o WrapperLogger não esteja disponível
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("PathResolver")

# Determinar o diretório raiz do projeto
# Tenta diferentes abordagens para encontrar o diretório raiz do projeto
def _get_project_root() -> str:
    """
    Identifica o diretório raiz do projeto usando diferentes estratégias.
    
    Returns:
        str: Caminho absoluto para o diretório raiz do projeto
    """
    # Estratégia 1: Usar o ambiente
    if "APP_FORCA_ROOT" in os.environ:
        root = os.environ["APP_FORCA_ROOT"]
        logger.debug(f"Diretório raiz encontrado via variável de ambiente: {root}")
        return root
    
    # Estratégia 2: Subir a partir do diretório atual até encontrar o diretório FORCA_V1
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navegar até 4 níveis acima procurando o diretório FORCA_V1
    for _ in range(4):  # Limitar a busca para evitar loops infinitos
        parent_dir = os.path.dirname(current_dir)
        if os.path.basename(current_dir) == "FORCA_V1":
            logger.debug(f"Diretório raiz encontrado via navegação: {current_dir}")
            return current_dir
        if os.path.basename(parent_dir) == "FORCA_V1":
            logger.debug(f"Diretório raiz encontrado via navegação: {parent_dir}")
            return parent_dir
        current_dir = parent_dir
    
    # Estratégia 3: Usar o diretório atual como fallback
    fallback_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    logger.warning(f"Diretório raiz não identificado, usando fallback: {fallback_dir}")
    return fallback_dir

# Diretório raiz do projeto
PROJECT_ROOT = _get_project_root()

# Definir constantes para os diretórios importantes
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
PROMPTS_DIR = os.path.join(BACKEND_DIR, "prompt")
SCHEMAS_DIR = os.path.join(BACKEND_DIR, "schemas")
JSON_TEMPLATES_DIR = os.path.join(BACKEND_DIR, "json")
WRAPPERS_DIR = os.path.join(BACKEND_DIR, "wrappers")

# Verificar a existência dos diretórios e criar se necessário
def ensure_directory(directory: str) -> None:
    """
    Verifica se um diretório existe e o cria caso necessário.
    
    Args:
        directory (str): Caminho do diretório a ser verificado/criado
    """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logger.info(f"Diretório criado: {directory}")
        except OSError as e:
            logger.error(f"Erro ao criar diretório {directory}: {str(e)}")

# Garantir que os diretórios existam
for directory in [PROMPTS_DIR, SCHEMAS_DIR, JSON_TEMPLATES_DIR]:
    ensure_directory(directory)

def resolve_path(filename: str, base_dirs: List[str], create_parent: bool = False) -> str:
    """
    Resolve o caminho absoluto de um arquivo, buscando em múltiplos diretórios.
    
    Args:
        filename (str): Nome do arquivo ou caminho relativo
        base_dirs (List[str]): Lista de diretórios base para procurar o arquivo
        create_parent (bool): Se True, cria o diretório pai se necessário
        
    Returns:
        str: Caminho absoluto para o arquivo
    """
    # Se o caminho já for absoluto, retornar diretamente
    if os.path.isabs(filename):
        logger.debug(f"Caminho já é absoluto: {filename}")
        return filename
    
    # Verificar se filename já contém parte do caminho
    filename_normalized = os.path.normpath(filename)
    
    # Buscar em cada diretório
    for base_dir in base_dirs:
        # Construir caminho completo
        full_path = os.path.join(base_dir, filename_normalized)
        
        # Verificar se o arquivo existe
        if os.path.exists(full_path):
            logger.debug(f"Arquivo encontrado: {full_path}")
            return full_path
    
    # Se não encontrou o arquivo, usar o primeiro diretório base
    full_path = os.path.join(base_dirs[0], filename_normalized)
    
    # Criar diretório pai se solicitado
    if create_parent:
        parent_dir = os.path.dirname(full_path)
        ensure_directory(parent_dir)
    
    logger.debug(f"Arquivo não encontrado, retornando caminho no diretório base: {full_path}")
    return full_path

def find_file(filename: str, search_dirs: Optional[List[str]] = None, 
              fallback_content: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Busca um arquivo em múltiplos diretórios e opcionalmente retorna conteúdo de fallback.
    
    Args:
        filename (str): Nome do arquivo para buscar
        search_dirs (List[str], optional): Lista de diretórios onde buscar
        fallback_content (str, optional): Conteúdo a retornar se o arquivo não for encontrado
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (caminho do arquivo, conteúdo do arquivo) ou (None, fallback_content)
    """
    # Usar diretórios padrão se não fornecido
    search_dirs = search_dirs or [PROJECT_ROOT, BACKEND_DIR]
    
    # Verificar se o caminho é absoluto
    if os.path.isabs(filename) and os.path.exists(filename):
        logger.debug(f"Arquivo encontrado com caminho absoluto: {filename}")
        return filename, None
    
    # Buscar em cada diretório
    for directory in search_dirs:
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            logger.debug(f"Arquivo encontrado: {path}")
            return path, None
    
    # Tentar extrair o nome base do arquivo e buscar novamente
    base_filename = os.path.basename(filename)
    for directory in search_dirs:
        path = os.path.join(directory, base_filename)
        if os.path.exists(path):
            logger.debug(f"Arquivo encontrado pelo nome base: {path}")
            return path, None
    
    # Não encontrou o arquivo
    logger.warning(f"Arquivo não encontrado: {filename}")
    return None, fallback_content

def get_prompt_path(prompt_name: str) -> str:
    """
    Obtém o caminho absoluto para um arquivo de prompt.
    
    Args:
        prompt_name (str): Nome do arquivo de prompt
        
    Returns:
        str: Caminho absoluto para o arquivo de prompt
    """
    # Diretórios onde procurar prompts, em ordem de prioridade
    prompt_dirs = [
        PROMPTS_DIR,  # Diretório principal de prompts
        BACKEND_DIR,  # Diretório backend
        PROJECT_ROOT, # Raiz do projeto
        os.path.dirname(os.path.abspath(__file__)),  # Diretório atual
        os.getcwd()   # Diretório de trabalho atual
    ]
    
    # Resolver caminho
    return resolve_path(prompt_name, prompt_dirs)

def get_schema_path(schema_name: str) -> str:
    """
    Obtém o caminho absoluto para um arquivo de schema.
    
    Args:
        schema_name (str): Nome do arquivo de schema
        
    Returns:
        str: Caminho absoluto para o arquivo de schema
    """
    # Diretórios onde procurar schemas, em ordem de prioridade
    schema_dirs = [
        SCHEMAS_DIR,   # Diretório específico para schemas
        BACKEND_DIR,   # Diretório backend
        WRAPPERS_DIR,  # Diretório dos wrappers
        PROJECT_ROOT,  # Raiz do projeto
        os.getcwd()    # Diretório de trabalho atual
    ]
    
    # Resolver caminho
    return resolve_path(schema_name, schema_dirs)

def get_template_path(template_name: str) -> str:
    """
    Obtém o caminho absoluto para um arquivo de template JSON.
    
    Args:
        template_name (str): Nome do arquivo de template
        
    Returns:
        str: Caminho absoluto para o arquivo de template
    """
    # Diretórios onde procurar templates, em ordem de prioridade
    template_dirs = [
        JSON_TEMPLATES_DIR, # Diretório específico para templates JSON
        BACKEND_DIR,        # Diretório backend
        PROJECT_ROOT,       # Raiz do projeto
        os.getcwd()         # Diretório de trabalho atual
    ]
    
    # Resolver caminho
    return resolve_path(template_name, template_dirs)

def load_file_with_fallback(file_path: str, fallback_content: Optional[str] = None, 
                           encoding: str = 'utf-8') -> Tuple[bool, str]:
    """
    Carrega um arquivo com conteúdo de fallback em caso de erro.
    
    Args:
        file_path (str): Caminho do arquivo a ser carregado
        fallback_content (str, optional): Conteúdo a retornar em caso de erro
        encoding (str): Codificação do arquivo
        
    Returns:
        Tuple[bool, str]: (sucesso, conteúdo do arquivo ou fallback)
    """
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
            logger.debug(f"Arquivo carregado com sucesso: {file_path}")
            return True, content
    except Exception as e:
        logger.warning(f"Erro ao carregar arquivo {file_path}: {str(e)}")
        if fallback_content is not None:
            logger.info("Usando conteúdo de fallback")
            return False, fallback_content
        else:
            logger.error("Nenhum conteúdo de fallback disponível")
            raise