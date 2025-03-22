# Wrapper para API Supabase #

import os
from typing import Dict, Any, List, Optional, Union
import json
from supabase import create_client, Client
from postgrest.exceptions import APIError

# Importar logger
from ..utils.logger import WrapperLogger
from ..utils.config import get_supabase_config

class SupabaseWrapper:
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Inicializa o wrapper da Supabase.
        
        Args:
            url (str, optional): URL da Supabase. Se não fornecido, será obtido da configuração
            api_key (str, optional): Chave de API da Supabase. Se não fornecida, será obtida da configuração
        """
        # Configurar logger
        self.logger = WrapperLogger("SupabaseWrapper")
        self.logger.info("Inicializando Wrapper Supabase")
        
        # Obter configurações se não fornecidas
        config = get_supabase_config()
        self.url = url or config.get('url')
        self.api_key = api_key or config.get('api_key')
        
        if not self.url or not self.api_key:
            self.logger.error("URL ou API key da Supabase não fornecidos")
            raise ValueError("URL e API key da Supabase são obrigatórios")
        
        self.logger.debug(f"Conectando à Supabase: {self.url}")
        try:
            self.client = create_client(self.url, self.api_key)
            self.logger.info("Cliente Supabase criado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao conectar com a Supabase: {str(e)}")
            raise
    
    def fetch_data(self, table: str, query: Dict[str, Any] = None, 
                   fields: List[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Busca dados de uma tabela na Supabase.
        
        Args:
            table (str): Nome da tabela
            query (Dict, optional): Critérios de filtro
            fields (List[str], optional): Campos a serem retornados
            limit (int, optional): Limite de registros
            
        Returns:
            List[Dict]: Dados encontrados
        """
        self.logger.info(f"Buscando dados da tabela: {table}")
        
        try:
            # Iniciar consulta
            query_builder = self.client.from_(table).select(",".join(fields) if fields else "*")
            
            # Aplicar filtros se fornecidos
            if query:
                for key, value in query.items():
                    if isinstance(value, dict) and "operator" in value:
                        # Formato: {"column": {"operator": "eq", "value": 123}}
                        op = value["operator"]
                        val = value["value"]
                        
                        if op == "eq":
                            query_builder = query_builder.eq(key, val)
                        elif op == "neq":
                            query_builder = query_builder.neq(key, val)
                        elif op == "gt":
                            query_builder = query_builder.gt(key, val)
                        elif op == "lt":
                            query_builder = query_builder.lt(key, val)
                        elif op == "gte":
                            query_builder = query_builder.gte(key, val)
                        elif op == "lte":
                            query_builder = query_builder.lte(key, val)
                        elif op == "in":
                            query_builder = query_builder.in_(key, val)
                        elif op == "contains":
                            query_builder = query_builder.contains(key, val)
                    else:
                        # Filtro simples de igualdade
                        query_builder = query_builder.eq(key, value)
            
            # Aplicar limite
            query_builder = query_builder.limit(limit)
            
            # Executar consulta
            response = query_builder.execute()
            
            # Verificar erros
            if hasattr(response, 'error') and response.error:
                self.logger.error(f"Erro ao buscar dados: {response.error}")
                return []
            
            data = response.data
            self.logger.info(f"Encontrados {len(data)} registros")
            return data
            
        except APIError as e:
            self.logger.error(f"Erro de API Supabase ao buscar dados: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados: {str(e)}")
            return []
    
    def insert_data(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]],
                   upsert: bool = False) -> Dict[str, Any]:
        """
        Insere dados em uma tabela na Supabase.
        
        Args:
            table (str): Nome da tabela
            data (Dict ou List[Dict]): Dados a serem inseridos
            upsert (bool, optional): Se True, atualiza registros existentes
            
        Returns:
            Dict: Resultado da operação
        """
        self.logger.info(f"Inserindo dados na tabela: {table}")
        
        try:
            # Verificar se é inserção única ou múltipla
            is_bulk = isinstance(data, list)
            count = len(data) if is_bulk else 1
            
            self.logger.debug(f"Inserindo {'vários' if is_bulk else 'um'} registros ({count})")
            
            # Preparar a requisição
            if upsert:
                response = self.client.from_(table).upsert(data).execute()
            else:
                response = self.client.from_(table).insert(data).execute()
            
            # Verificar erros
            if hasattr(response, 'error') and response.error:
                self.logger.error(f"Erro ao inserir dados: {response.error}")
                return {"status": "error", "message": str(response.error)}
            
            result = {
                "status": "success",
                "data": response.data,
                "count": len(response.data) if response.data else 0
            }
            
            self.logger.info(f"Dados inseridos com sucesso: {result['count']} registros")
            return result
            
        except APIError as e:
            self.logger.error(f"Erro de API Supabase ao inserir dados: {str(e)}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Erro ao inserir dados: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def update_data(self, table: str, data: Dict[str, Any], 
                   filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza dados em uma tabela na Supabase.
        
        Args:
            table (str): Nome da tabela
            data (Dict): Dados a serem atualizados
            filters (Dict): Critérios para selecionar os registros
            
        Returns:
            Dict: Resultado da operação
        """
        self.logger.info(f"Atualizando dados na tabela: {table}")
        
        try:
            # Iniciar builder
            query_builder = self.client.from_(table).update(data)
            
            # Aplicar filtros
            for key, value in filters.items():
                if isinstance(value, dict) and "operator" in value:
                    # Aplicar operadores personalizados
                    op = value["operator"]
                    val = value["value"]
                    
                    if op == "eq":
                        query_builder = query_builder.eq(key, val)
                    elif op == "neq":
                        query_builder = query_builder.neq(key, val)
                    # ... outros operadores conforme necessário
                else:
                    # Filtro padrão de igualdade
                    query_builder = query_builder.eq(key, value)
            
            # Executar atualização
            response = query_builder.execute()
            
            # Verificar erros
            if hasattr(response, 'error') and response.error:
                self.logger.error(f"Erro ao atualizar dados: {response.error}")
                return {"status": "error", "message": str(response.error)}
            
            result = {
                "status": "success",
                "data": response.data,
                "count": len(response.data) if response.data else 0
            }
            
            self.logger.info(f"Dados atualizados com sucesso: {result['count']} registros")
            return result
            
        except APIError as e:
            self.logger.error(f"Erro de API Supabase ao atualizar dados: {str(e)}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Erro ao atualizar dados: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def delete_data(self, table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove dados de uma tabela na Supabase.
        
        Args:
            table (str): Nome da tabela
            filters (Dict): Critérios para selecionar os registros
            
        Returns:
            Dict: Resultado da operação
        """
        self.logger.info(f"Removendo dados da tabela: {table}")
        
        try:
            # Iniciar builder
            query_builder = self.client.from_(table).delete()
            
            # Aplicar filtros
            for key, value in filters.items():
                if isinstance(value, dict) and "operator" in value:
                    # Aplicar operadores personalizados
                    op = value["operator"]
                    val = value["value"]
                    
                    if op == "eq":
                        query_builder = query_builder.eq(key, val)
                    elif op == "neq":
                        query_builder = query_builder.neq(key, val)
                    # ... outros operadores conforme necessário
                else:
                    # Filtro padrão de igualdade
                    query_builder = query_builder.eq(key, value)
            
            # Executar remoção
            response = query_builder.execute()
            
            # Verificar erros
            if hasattr(response, 'error') and response.error:
                self.logger.error(f"Erro ao remover dados: {response.error}")
                return {"status": "error", "message": str(response.error)}
            
            result = {
                "status": "success",
                "data": response.data,
                "count": len(response.data) if response.data else 0
            }
            
            self.logger.info(f"Dados removidos com sucesso: {result['count']} registros")
            return result
            
        except APIError as e:
            self.logger.error(f"Erro de API Supabase ao remover dados: {str(e)}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Erro ao remover dados: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def execute_rpc(self, function_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executa uma função RPC na Supabase.
        
        Args:
            function_name (str): Nome da função
            params (Dict, optional): Parâmetros para a função
            
        Returns:
            Dict: Resultado da execução
        """
        self.logger.info(f"Executando função RPC: {function_name}")
        
        try:
            params = params or {}
            response = self.client.rpc(function_name, params).execute()
            
            # Verificar erros
            if hasattr(response, 'error') and response.error:
                self.logger.error(f"Erro ao executar RPC: {response.error}")
                return {"status": "error", "message": str(response.error)}
            
            result = {
                "status": "success",
                "data": response.data
            }
            
            self.logger.info(f"Função RPC executada com sucesso")
            return result
            
        except APIError as e:
            self.logger.error(f"Erro de API Supabase ao executar RPC: {str(e)}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Erro ao executar RPC: {str(e)}")
            return {"status": "error", "message": str(e)}