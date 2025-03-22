# Wrapper para API Claude #

import json
import requests
import traceback
from typing import Dict, Any, List, Optional, Union
import anthropic
from anthropic import Anthropic

# Importar logger
from ..utils.logger import WrapperLogger
from ..utils.config import get_claude_config

class ClaudeWrapper:
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o wrapper da API Claude.
        
        Args:
            api_key (str, optional): Chave de API para o serviço Claude. Se não fornecida, será obtida da configuração.
        """
        # Configurar logger
        self.logger = WrapperLogger("ClaudeWrapper")
        self.logger.info("Inicializando Wrapper Claude")
        
        # Obter configurações se não fornecidas
        config = get_claude_config()
        self.api_key = api_key or config.get('api_key')
        self.api_url = config.get('api_url')
        self.default_model = config.get('model', 'claude-3-opus-20240229')
        
        if not self.api_key:
            self.logger.error("API key da Claude não fornecida")
            raise ValueError("API key da Claude é obrigatória")
        
        self.logger.debug(f"Usando modelo padrão: {self.default_model}")
        try:
            # Inicializar cliente da biblioteca anthropic
            self.client = Anthropic(api_key=self.api_key)
            self.logger.info("Cliente Claude inicializado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar cliente Claude: {str(e)}")
            raise
    
    def generate_response(self, 
                         prompt: str, 
                         model: Optional[str] = None,
                         max_tokens: int = 4000,
                         temperature: float = 0.7,
                         system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia um prompt para a API Claude e obtém uma resposta.
        
        Args:
            prompt (str): Prompt para enviar ao Claude
            model (str, optional): Modelo a ser usado. Se não fornecido, usa o modelo padrão
            max_tokens (int, optional): Número máximo de tokens na resposta
            temperature (float, optional): Temperatura da amostragem
            system_prompt (str, optional): Prompt de sistema para contextualização
            
        Returns:
            Dict: Resposta do Claude
        """
        model = model or self.default_model
        self.logger.info(f"Enviando requisição ao Claude usando modelo: {model}")
        self.logger.debug(f"Parâmetros - max_tokens: {max_tokens}, temperature: {temperature}")
        
        try:
            # Preparar mensagens
            messages = [{"role": "user", "content": prompt}]
            
            # Criar a mensagem
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )
            
            self.logger.info("Resposta obtida com sucesso do Claude")
            self.logger.debug(f"Tokens usados: {response.usage.input_tokens} (entrada), {response.usage.output_tokens} (saída)")
            
            result = {
                "status": "success",
                "content": response.content,
                "message_id": response.id,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
            return result
            
        except anthropic.APIError as e:
            self.logger.error(f"Erro de API Claude: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro de API: {str(e)}",
                "error_type": "api_error"
            }
        except anthropic.RateLimitError as e:
            self.logger.error(f"Erro de limite de taxa: {str(e)}")
            return {
                "status": "error",
                "message": "Limite de taxa excedido. Tente novamente mais tarde.",
                "error_type": "rate_limit"
            }
        except anthropic.APIConnectionError as e:
            self.logger.error(f"Erro de conexão: {str(e)}")
            return {
                "status": "error",
                "message": "Erro de conexão com a API Claude.",
                "error_type": "connection_error"
            }
        except anthropic.AuthenticationError as e:
            self.logger.error(f"Erro de autenticação: {str(e)}")
            return {
                "status": "error",
                "message": "Falha na autenticação com a API Claude.",
                "error_type": "authentication_error"
            }
        except Exception as e:
            self.logger.error(f"Erro inesperado: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Erro inesperado: {str(e)}",
                "error_type": "unexpected_error"
            }
    
    def extract_json_from_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai conteúdo JSON da resposta do Claude.
        
        Args:
            response (Dict): Resposta do Claude
            
        Returns:
            Dict: JSON extraído ou erro
        """
        self.logger.info("Extraindo JSON da resposta do Claude")
        
        if response.get("status") != "success":
            self.logger.error("Tentativa de extrair JSON de uma resposta com erro")
            return {
                "status": "error",
                "message": "Não é possível extrair JSON de uma resposta com erro",
                "original_error": response.get("message", "Erro desconhecido")
            }
        
        try:
            # Extrair o conteúdo
            content = []
            if isinstance(response.get("content"), list):
                content = response.get("content", [])
            else:
                content = [{"text": response.get("content", "")}]
            
            # Procurar blocos de código JSON
            json_text = ""
            
            for item in content:
                text = item.get("text", "")
                
                # Procurar por blocos ```json ... ```
                import re
                json_blocks = re.findall(r'```json(.*?)```', text, re.DOTALL)
                
                if json_blocks:
                    self.logger.debug(f"Encontrado bloco JSON marcado")
                    json_text = json_blocks[0].strip()
                    break
                
                # Se não encontrar, verificar se o texto completo é JSON
                if text.strip().startswith("{") and text.strip().endswith("}"):
                    self.logger.debug("Encontrado JSON direto no texto")
                    json_text = text.strip()
                    break
            
            if not json_text:
                self.logger.error("Nenhum JSON encontrado na resposta")
                return {
                    "status": "error",
                    "message": "Não foi possível encontrar JSON na resposta",
                    "content": response.get("content", "")
                }
            
            # Converter para objeto Python
            json_obj = json.loads(json_text)
            
            return {
                "status": "success",
                "data": json_obj
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro ao decodificar JSON: {str(e)}",
                "json_text": json_text[:200] + "..." if len(json_text) > 200 else json_text
            }
        except Exception as e:
            self.logger.error(f"Erro ao extrair JSON: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro inesperado ao extrair JSON: {str(e)}"
            }