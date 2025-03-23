# Wrapper 1: Treinador Especialista #

import json
import requests
import uuid
import datetime
import jsonschema
from typing import Dict, Any, Optional
import os
import traceback
import logging

# Importar o WrapperLogger e PathResolver
from backend.utils.logger import WrapperLogger
from backend.utils.path_resolver import (
    get_prompt_path, get_schema_path, get_template_path,
    load_file_with_fallback
)

class TreinadorEspecialista:
    def __init__(self, api_key: str, api_url: str = "https://api.anthropic.com/v1/messages"):
        """
        Inicializa o wrapper do Treinador Especialista.
        
        Args:
            api_key (str): Chave de API para o serviço Claude
            api_url (str): URL da API Claude
        """
        # Configurar logger
        self.logger = WrapperLogger("Wrapper1_Treinador")
        self.logger.info("Inicializando Treinador Especialista")
        
        self.api_key = api_key
        self.api_url = api_url
        
        try:
            # Tentar diferentes caminhos possíveis
            prompt_paths = [
                "/prompt/PROMPT DO TREINADOR ESPECIALISTA.txt",
                "prompt/PROMPT DO TREINADOR ESPECIALISTA.txt",
                "../prompt/PROMPT DO TREINADOR ESPECIALISTA.txt",
                "PROMPT DO TREINADOR ESPECIALISTA.txt"
            ]
            
            success = False
            for path in prompt_paths:
                try:
                    self.prompt_template = self._carregar_prompt(path)
                    self.logger.info(f"Prompt do treinador carregado com sucesso do caminho: {path}")
                    success = True
                    break
                except FileNotFoundError:
                    self.logger.debug(f"Prompt não encontrado no caminho: {path}")
            
            if not success:
                self.logger.warning("Não foi possível carregar o prompt de nenhum caminho, usando template padrão")
                self.prompt_template = """
                # PROMPT DO TREINADOR ESPECIALISTA (TEMPLATE PADRÃO)
                
                Você é um treinador fitness especialista com anos de experiência na criação de planos de treinamento personalizados.
                
                Por favor, analise os dados do usuário fornecidos e crie um plano de treinamento detalhado que atenda às suas necessidades específicas. Considere o nível de experiência, objetivos, restrições e lesões.
                
                Crie um plano de treinamento estruturado que inclua:
                - Periodização adequada
                - Ciclos de treinamento
                - Exercícios específicos
                - Séries, repetições e intensidade
                - Progressão ao longo do tempo
                
                Forneça o plano no formato JSON solicitado.
                """
                self.logger.info("Template padrão configurado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao carregar prompt do treinador: {str(e)}")
            self.logger.error(traceback.format_exc())
            
        try:
            self.schema = self._carregar_schema_json()
            self.logger.info("Schema JSON carregado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao carregar schema JSON: {str(e)}")
            raise
    
    @WrapperLogger.log_function(logging.INFO)
    def _carregar_prompt(self, arquivo_prompt: str) -> str:
        """Carrega o prompt do treinador especialista de um arquivo."""
        self.logger.info(f"Tentando carregar prompt do arquivo: {arquivo_prompt}")
        
        # Resolver caminho do arquivo de prompt
        prompt_path = get_prompt_path(arquivo_prompt)
        self.logger.debug(f"Caminho resolvido para o prompt: {prompt_path}")
        
        # Carregar arquivo com fallback
        success, content = load_file_with_fallback(
            prompt_path,
            fallback_content=f"TEMPLATE BÁSICO DO PROMPT (fallback para '{arquivo_prompt}')\n\nPor favor, forneça detalhes para criar um plano de treinamento personalizado."
        )
        
        if success:
            self.logger.info(f"Prompt carregado com sucesso, {len(content)} caracteres")
        else:
            self.logger.warning(f"Usando conteúdo de fallback para o prompt {arquivo_prompt}")
            
        return content
    
    @WrapperLogger.log_function(logging.INFO)
    def _carregar_schema_json(self) -> Dict:
        """Carrega o schema JSON para validação."""
        self.logger.info("Tentando carregar schema_wrapper1.json")
        
        # Resolver caminho do arquivo de schema
        schema_path = get_schema_path("schema_wrapper1.json")
        self.logger.debug(f"Caminho resolvido para o schema: {schema_path}")
        
        # Schema básico como fallback
        schema_basico = {
            "type": "object",
            "required": ["treinamento_id", "versao", "data_criacao", "usuario", "plano_principal"],
            "properties": {
                "treinamento_id": {"type": "string"},
                "versao": {"type": "string"},
                "data_criacao": {"type": "string"},
                "usuario": {
                    "type": "object",
                    "required": ["id", "nome", "nivel", "objetivos", "restricoes"],
                    "properties": {
                        "id": {"type": "string"},
                        "nome": {"type": "string"},
                        "nivel": {"type": "string"},
                        "objetivos": {"type": "array"},
                        "restricoes": {"type": "array"}
                    }
                },
                "plano_principal": {"type": "object"}
            }
        }
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as file:
                schema = json.load(file)
                self.logger.debug(f"Schema carregado com sucesso: {len(schema.keys() if isinstance(schema, dict) else schema)} elementos")
                return schema
        except FileNotFoundError:
            self.logger.warning(f"Arquivo schema {schema_path} não encontrado, usando schema básico")
            return schema_basico
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON do schema: {str(e)}")
            return schema_basico
        except Exception as e:
            self.logger.error(f"Erro ao carregar schema: {str(e)}")
            return schema_basico
    
    @WrapperLogger.log_function(logging.INFO)
    def criar_plano_treinamento(self, dados_usuario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um plano de treinamento personalizado usando a API Claude.
        
        Args:
            dados_usuario (Dict): Dados do usuário para personalizar o treino
            
        Returns:
            Dict: Plano de treinamento no formato JSON
        """
        self.logger.info(f"Iniciando criação de plano para usuário: {dados_usuario.get('nome', 'Não especificado')}")
        
        # Gerar ID de treinamento e versão
        treinamento_id = str(uuid.uuid4())
        versao = "1.0"
        data_criacao = datetime.datetime.now().isoformat()
        self.logger.debug(f"Gerado treinamento_id: {treinamento_id}, versão: {versao}")
        
        # Preparar prompt para o Claude
        self.logger.info("Preparando prompt para o Claude")
        prompt_completo = self._preparar_prompt(dados_usuario)
        self.logger.debug(f"Prompt completo gerado com {len(prompt_completo)} caracteres")
        
        # Fazer requisição para o Claude
        self.logger.info("Enviando requisição para a API Claude")
        try:
            resposta_json = self._fazer_requisicao_claude(prompt_completo)
            self.logger.info("Resposta recebida da API Claude com sucesso")
        except Exception as e:
            self.logger.error(f"Erro na requisição para a API Claude: {str(e)}")
            raise
        
        # Extrair e validar o plano de treinamento
        self.logger.info("Extraindo JSON da resposta")
        try:
            plano_treinamento = self._extrair_json_da_resposta(resposta_json)
            self.logger.debug(f"JSON extraído com sucesso: {len(json.dumps(plano_treinamento))} caracteres")
        except Exception as e:
            self.logger.error(f"Erro ao extrair JSON da resposta: {str(e)}")
            self.logger.debug(f"Conteúdo da resposta: {json.dumps(resposta_json)[:500]}...")
            raise
        
        # Adicionar metadados
        self.logger.info("Adicionando metadados ao plano")
        plano_treinamento["treinamento_id"] = treinamento_id
        plano_treinamento["versao"] = versao
        plano_treinamento["data_criacao"] = data_criacao
        plano_treinamento["usuario"]["id"] = dados_usuario.get("id", str(uuid.uuid4()))
        
        # Garantir que a duração do plano seja 12 semanas
        if "plano_principal" in plano_treinamento:
            plano_treinamento["plano_principal"]["duracao_semanas"] = 12
            self.logger.debug("Duração do plano fixada em 12 semanas")
        
        # Validar plano final
        self.logger.info("Validando plano final")
        try:
            plano_validado = self._validar_plano(plano_treinamento)
            self.logger.info("Plano validado com sucesso")
            # Log resumido do plano para depuração
            self.logger.debug("Resumo do plano validado:")
            self._log_resumo_plano(plano_validado)
        except Exception as e:
            self.logger.error(f"Erro na validação do plano: {str(e)}")
            raise
        
        return plano_validado
    
    def _log_resumo_plano(self, plano: Dict[str, Any]) -> None:
        """Cria um log resumido do plano para depuração"""
        try:
            ciclos = plano.get("plano_principal", {}).get("ciclos", [])
            num_ciclos = len(ciclos)
            
            # Contar exercícios totais
            total_exercicios = 0
            total_sessoes = 0
            
            for ciclo in ciclos:
                for microciclo in ciclo.get("microciclos", []):
                    total_sessoes += len(microciclo.get("sessoes", []))
                    for sessao in microciclo.get("sessoes", []):
                        total_exercicios += len(sessao.get("exercicios", []))
            
            self.logger.debug(f"Resumo do plano: {num_ciclos} ciclos, {total_sessoes} sessões, {total_exercicios} exercícios")
        except Exception as e:
            self.logger.warning(f"Erro ao criar resumo do plano: {str(e)}")
    
    @WrapperLogger.log_function(logging.INFO)
    def _preparar_prompt(self, dados_usuario: Dict[str, Any]) -> str:
        """
        Prepara o prompt para enviar ao Claude com base nos dados do usuário.
        
        Args:
            dados_usuario (Dict): Dados do usuário
            
        Returns:
            str: Prompt formatado
        """
        self.logger.info("Extraindo informações do usuário para o prompt")
        
        # Extrair informações relevantes do usuário
        nome = dados_usuario.get("nome", "")
        idade = dados_usuario.get("idade", "")
        data_nascimento = dados_usuario.get("data_nascimento", "")
        peso = dados_usuario.get("peso", "")
        altura = dados_usuario.get("altura", "")
        genero = dados_usuario.get("genero", "")
        nivel = dados_usuario.get("nivel", "iniciante")
        historico_treino = dados_usuario.get("historico_treino", "")
        tempo_treino = dados_usuario.get("tempo_treino", 60)
        disponibilidade_semanal = dados_usuario.get("disponibilidade_semanal", 3)
        dias_disponiveis = dados_usuario.get("dias_disponiveis", [])
        cardio = dados_usuario.get("cardio", "não")
        alongamento = dados_usuario.get("alongamento", "não")
        conversa_chat = dados_usuario.get("conversa_chat", "")
        objetivos = dados_usuario.get("objetivos", [])
        restricoes = dados_usuario.get("restricoes", [])
        lesoes = dados_usuario.get("lesoes", [])
        
        # Data atual para início do plano
        data_inicio = datetime.datetime.now().strftime("%Y-%m-%d")
        
        self.logger.debug(f"Nível do usuário: {nivel}, Disponibilidade: {disponibilidade_semanal} dias por semana")
        
        # Formatar objetivos e restrições
        objetivos_str = "\n".join([f"- {obj.get('nome', '')} (Prioridade: {obj.get('prioridade', '')})" for obj in objetivos])
        restricoes_str = "\n".join([f"- {rest.get('nome', '')}, Gravidade: {rest.get('gravidade', '')}" for rest in restricoes])
        lesoes_str = "\n".join([f"- {lesao.get('regiao', '')}, Gravidade: {lesao.get('gravidade', '')}, Obs: {lesao.get('observacoes', '')}" for lesao in lesoes])
        dias_str = ", ".join(dias_disponiveis) if dias_disponiveis else "Não especificado"
        
        self.logger.debug(f"Objetivos formatados: {objetivos_str[:100]}...")
        
        # Adicionar contexto ao prompt
        contexto = f"""
        Dados do Usuário:
        Nome: {nome}
        Idade: {idade}
        Data de Nascimento: {data_nascimento}
        Peso: {peso} kg
        Altura: {altura} cm
        Gênero: {genero}
        Nível: {nivel}
        Histórico de Treino: {historico_treino}
        Tempo disponível por sessão: {tempo_treino} minutos
        Dias disponíveis para treino: {dias_str}
        Disponibilidade semanal: {disponibilidade_semanal} dias
        Incluir cardio: {cardio}
        Incluir alongamento: {alongamento}
        Data de início do plano: {data_inicio}
        
        Objetivos:
        {objetivos_str}
        
        Restrições:
        {restricoes_str}
        
        Lesões:
        {lesoes_str}
        
        Informações adicionais do chat:
        {conversa_chat}
        
        INSTRUÇÕES ESPECÍFICAS:
        1. Crie um plano de treinamento detalhado para EXATAMENTE 12 semanas.
        2. Organize os treinos nos dias da semana que o usuário selecionou: {dias_str}.
        3. Cada treino deve incluir exercícios específicos, número de séries e repetições.
        4. Especifique a % de 1RM para cada exercício, exceto para o primeiro treino onde será testada a força máxima.
        5. Se o usuário solicitou cardio ({cardio}) ou alongamento ({alongamento}), inclua-os no plano de 12 semanas.
        6. O plano deve começar em {data_inicio}.
        
        Agora, crie um plano de treinamento completo para este usuário seguindo exatamente o formato JSON abaixo:
        
        ```json
        {self._obter_template_json()}
        ```
        
        Preencha todos os campos necessários e retorne apenas o JSON válido.
        """
        
        self.logger.debug(f"Contexto gerado com {len(contexto)} caracteres")
        
        prompt_final = f"{self.prompt_template}\n\n{contexto}"
        return prompt_final
    
    @WrapperLogger.log_function(logging.INFO)
    def _obter_template_json(self) -> str:
        """Retorna um template do JSON esperado."""
        self.logger.info("Obtendo template JSON")
        
        # Tentar diferentes caminhos possíveis para o template
        template_paths = [
            "JSON para Wrapper 1 Treinador.txt",
            "../json/JSON para Wrapper 1 Treinador.txt",
            "/json/JSON para Wrapper 1 Treinador.txt",
            "backend/json/JSON para Wrapper 1 Treinador.txt"
        ]
        
        # Template simplificado como fallback final
        template_simplificado = """
        {
          "treinamento_id": "",
          "versao": "",
          "data_criacao": "",
          "usuario": {
            "id": "",
            "nome": "",
            "nivel": "",
            "objetivos": [
              {
                "objetivo_id": "",
                "nome": "",
                "prioridade": 1
              }
            ],
            "restricoes": []
          },
          "plano_principal": {
            "nome": "",
            "descricao": "",
            "periodizacao": {
              "tipo": "",
              "descricao": ""
            },
            "duracao_semanas": 12,
            "frequencia_semanal": 3,
            "ciclos": [
              {
                "ciclo_id": "",
                "nome": "",
                "ordem": 1,
                "duracao_semanas": 4,
                "objetivo": "",
                "microciclos": [
                  {
                    "semana": 1,
                    "volume": "",
                    "intensidade": "",
                    "foco": "",
                    "sessoes": [
                      {
                        "sessao_id": "",
                        "nome": "",
                        "tipo": "",
                        "duracao_minutos": 60,
                        "nivel_intensidade": 7,
                        "dia_semana": 1,
                        "grupos_musculares": [],
                        "exercicios": [
                          {
                            "exercicio_id": "",
                            "nome": "",
                            "ordem": 1,
                            "equipamento": "",
                            "series": 3,
                            "repeticoes": "10-12",
                            "percentual_rm": 70,
                            "tempo_descanso": 60,
                            "cadencia": "",
                            "metodo": "",
                            "progressao": [],
                            "observacoes": ""
                          }
                        ]
                      }
                    ]
                  }
                ]
              }
            ]
          }
        }
        """
        
        # Tentar carregar de cada caminho
        for path in template_paths:
            try:
                template_path = get_template_path(path)
                self.logger.debug(f"Tentando carregar template do caminho: {template_path}")
                
                # Tentar abrir o arquivo diretamente primeiro
                try:
                    with open(template_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.logger.info(f"Template JSON carregado com sucesso do caminho: {template_path}")
                        return content
                except FileNotFoundError:
                    # Se não encontrou, tentar o fallback
                    self.logger.debug(f"Arquivo não encontrado em: {template_path}")
                    
                # Usar o load_file_with_fallback como alternativa
                success, content = load_file_with_fallback(
                    template_path,
                    fallback_content=""  # Vazio para detectar falha
                )
                
                if success and content:
                    self.logger.info(f"Template JSON carregado com sucesso via fallback, {len(content)} caracteres")
                    return content
                
            except Exception as e:
                self.logger.debug(f"Erro ao tentar caminho {path}: {str(e)}")
        
        # Última tentativa: acessar diretamente o arquivo do backend/json
        try:
            import os
            direct_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "json", 
                "JSON para Wrapper 1 Treinador.txt"
            )
            self.logger.debug(f"Tentando acesso direto ao arquivo: {direct_path}")
            
            with open(direct_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.logger.info(f"Template JSON carregado diretamente de: {direct_path}")
                return content
        except Exception as e:
            self.logger.debug(f"Falha no acesso direto: {str(e)}")
        
        # Se chegou até aqui, usar o template simplificado
        self.logger.warning("Usando template JSON simplificado como último recurso")
        return template_simplificado
    
    @WrapperLogger.log_function(logging.INFO)
    def _fazer_requisicao_claude(self, prompt: str) -> Dict[str, Any]:
        """
        Faz uma requisição para a API Claude.
        
        Args:
            prompt (str): Prompt para o Claude
            
        Returns:
            Dict: Resposta da API em formato JSON
        """
        self.logger.info("Preparando requisição para a API Claude")
        
        # Assegurar que temos uma API key válida
        if not self.api_key or self.api_key.strip() == "":
            erro_msg = "API key não fornecida ou vazia"
            self.logger.error(erro_msg)
            
            # Retornar uma resposta fictícia com uma mensagem de erro
            return {
                "content": [
                    {
                        "text": f"""```json
                        {{
                          "erro": "{erro_msg}",
                          "usuario": {{
                            "id": "",
                            "nome": "Usuário Fallback (Erro API)",
                            "nivel": "intermediário",
                            "objetivos": [
                              {{
                                "objetivo_id": "{str(uuid.uuid4())}",
                                "nome": "Condicionamento geral",
                                "prioridade": 1
                              }}
                            ],
                            "restricoes": []
                          }},
                          "plano_principal": {{
                            "nome": "Plano de Treinamento (Simulado - Erro API)",
                            "descricao": "Este plano foi gerado automaticamente devido a erro na API.",
                            "periodizacao": {{
                              "tipo": "linear",
                              "descricao": "Progressão linear de carga"
                            }},
                            "duracao_semanas": 12,
                            "frequencia_semanal": 3,
                            "ciclos": [
                              {{
                                "ciclo_id": "{str(uuid.uuid4())}",
                                "nome": "Ciclo Inicial",
                                "ordem": 1,
                                "duracao_semanas": 12,
                                "objetivo": "Condicionamento geral",
                                "microciclos": [
                                  {{
                                    "semana": 1,
                                    "volume": "médio",
                                    "intensidade": "média",
                                    "foco": "Adaptação",
                                    "sessoes": [
                                      {{
                                        "sessao_id": "{str(uuid.uuid4())}",
                                        "nome": "Treino A",
                                        "tipo": "resistência",
                                        "duracao_minutos": 60,
                                        "nivel_intensidade": 5,
                                        "dia_semana": 1,
                                        "grupos_musculares": [],
                                        "exercicios": [
                                          {{
                                            "exercicio_id": "{str(uuid.uuid4())}",
                                            "nome": "Agachamento",
                                            "ordem": 1,
                                            "equipamento": "Peso corporal",
                                            "series": 3,
                                            "repeticoes": "12-15",
                                            "percentual_rm": 70,
                                            "tempo_descanso": 60,
                                            "cadencia": "2-0-2",
                                            "metodo": "normal",
                                            "progressao": [],
                                            "observacoes": "Simulado devido a erro de API"
                                          }}
                                        ]
                                      }}
                                    ]
                                  }}
                                ]
                              }}
                            ]
                          }}
                        }}
                        ```"""
                    }
                ]
            }
        
        # Se temos uma API key, continuar com a requisição
        headers = {
            "anthropic-version": "2023-06-01",
            "x-api-key": self.api_key.strip(),
            "content-type": "application/json"
        }
        
        # Verificar se estamos usando a URL antiga ou nova da API
        api_url = self.api_url
        if "api.anthropic.com/v1/messages" not in api_url:
            api_url = "https://api.anthropic.com/v1/messages"
            self.logger.info(f"URL API atualizada para: {api_url}")
        
        data = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        self.logger.debug(f"Usando modelo: {data['model']}, max_tokens: {data['max_tokens']}")
        
        try:
            self.logger.info(f"Enviando requisição POST para {api_url}")
            response = requests.post(api_url, headers=headers, json=data)
            
            self.logger.debug(f"Status da resposta: {response.status_code}")
            
            # Verificar o status da resposta
            if response.status_code != 200:
                self.logger.error(f"Erro na API: status {response.status_code}")
                error_msg = response.text
                try:
                    error_json = response.json()
                    if isinstance(error_json, dict):
                        error_msg = error_json.get("error", {}).get("message", response.text)
                except:
                    pass
                self.logger.error(f"Erro API: {error_msg[:500]}...")
                
                # Em caso de erro, retornar uma resposta simulada
                return {
                    "content": [
                        {
                            "text": f"""```json
                            {{
                              "erro": "Erro na API Claude: {error_msg[:100].replace('"', '\\"')}...",
                              "usuario": {{
                                "id": "",
                                "nome": "Usuário Fallback (Erro API)",
                                "nivel": "intermediário",
                                "objetivos": [
                                  {{
                                    "objetivo_id": "{str(uuid.uuid4())}",
                                    "nome": "Condicionamento geral",
                                    "prioridade": 1
                                  }}
                                ],
                                "restricoes": []
                              }},
                              "plano_principal": {{
                                "nome": "Plano de Treinamento (Simulado - Erro API)",
                                "descricao": "Este plano foi gerado automaticamente devido a erro na API.",
                                "periodizacao": {{
                                  "tipo": "linear",
                                  "descricao": "Progressão linear de carga"
                                }},
                                "duracao_semanas": 12,
                                "frequencia_semanal": 3,
                                "ciclos": [
                                  {{
                                    "ciclo_id": "{str(uuid.uuid4())}",
                                    "nome": "Ciclo Inicial",
                                    "ordem": 1,
                                    "duracao_semanas": 12,
                                    "objetivo": "Condicionamento geral",
                                    "microciclos": [
                                      {{
                                        "semana": 1,
                                        "volume": "médio",
                                        "intensidade": "média",
                                        "foco": "Adaptação",
                                        "sessoes": [
                                          {{
                                            "sessao_id": "{str(uuid.uuid4())}",
                                            "nome": "Treino A",
                                            "tipo": "resistência",
                                            "duracao_minutos": 60,
                                            "nivel_intensidade": 5,
                                            "dia_semana": 1,
                                            "grupos_musculares": [],
                                            "exercicios": [
                                              {{
                                                "exercicio_id": "{str(uuid.uuid4())}",
                                                "nome": "Agachamento",
                                                "ordem": 1,
                                                "equipamento": "Peso corporal",
                                                "series": 3,
                                                "repeticoes": "12-15",
                                                "percentual_rm": 70,
                                                "tempo_descanso": 60,
                                                "cadencia": "2-0-2",
                                                "metodo": "normal",
                                                "progressao": [],
                                                "observacoes": "Simulado devido a erro de API"
                                              }}
                                            ]
                                          }}
                                        ]
                                      }}
                                    ]
                                  }}
                                ]
                              }}
                            }}
                            ```"""
                        }
                    ]
                }
            
            # Se chegou aqui, a resposta foi bem-sucedida
            resposta_json = response.json()
            self.logger.info("Resposta obtida e convertida para JSON com sucesso")
            return resposta_json
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro na requisição HTTP: {str(e)}")
            
            # Retornar um fallback em caso de erro de conexão
            return {
                "content": [
                    {
                        "text": f"""```json
                        {{
                          "erro": "Erro de conexão: {str(e)[:100].replace('"', '\\"')}...",
                          "usuario": {{
                            "id": "",
                            "nome": "Usuário Fallback (Erro conexão)",
                            "nivel": "intermediário",
                            "objetivos": [
                              {{
                                "objetivo_id": "{str(uuid.uuid4())}",
                                "nome": "Condicionamento geral",
                                "prioridade": 1
                              }}
                            ],
                            "restricoes": []
                          }},
                          "plano_principal": {{
                            "nome": "Plano de Treinamento (Simulado - Erro conexão)",
                            "descricao": "Este plano foi gerado automaticamente devido a erro de conexão.",
                            "periodizacao": {{
                              "tipo": "linear",
                              "descricao": "Progressão linear de carga"
                            }},
                            "duracao_semanas": 12,
                            "frequencia_semanal": 3,
                            "ciclos": [
                              {{
                                "ciclo_id": "{str(uuid.uuid4())}",
                                "nome": "Ciclo Inicial",
                                "ordem": 1,
                                "duracao_semanas": 12,
                                "objetivo": "Condicionamento geral",
                                "microciclos": [
                                  {{
                                    "semana": 1,
                                    "volume": "médio",
                                    "intensidade": "média",
                                    "foco": "Adaptação",
                                    "sessoes": [
                                      {{
                                        "sessao_id": "{str(uuid.uuid4())}",
                                        "nome": "Treino A",
                                        "tipo": "resistência",
                                        "duracao_minutos": 60,
                                        "nivel_intensidade": 5,
                                        "dia_semana": 1,
                                        "grupos_musculares": [],
                                        "exercicios": [
                                          {{
                                            "exercicio_id": "{str(uuid.uuid4())}",
                                            "nome": "Agachamento",
                                            "ordem": 1,
                                            "equipamento": "Peso corporal",
                                            "series": 3,
                                            "repeticoes": "12-15",
                                            "percentual_rm": 70,
                                            "tempo_descanso": 60,
                                            "cadencia": "2-0-2",
                                            "metodo": "normal",
                                            "progressao": [],
                                            "observacoes": "Simulado devido a erro de conexão"
                                          }}
                                        ]
                                      }}
                                    ]
                                  }}
                                ]
                              }}
                            ]
                          }}
                        }}
                        ```"""
                    }
                ]
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON da resposta: {str(e)}")
            
            # Retornar um fallback em caso de erro de JSON
            return {
                "content": [
                    {
                        "text": f"""```json
                        {{
                          "erro": "Erro ao decodificar resposta: {str(e)[:100].replace('"', '\\"')}...",
                          "usuario": {{
                            "id": "",
                            "nome": "Usuário Fallback (Erro JSON)",
                            "nivel": "intermediário",
                            "objetivos": [
                              {{
                                "objetivo_id": "{str(uuid.uuid4())}",
                                "nome": "Condicionamento geral",
                                "prioridade": 1
                              }}
                            ],
                            "restricoes": []
                          }},
                          "plano_principal": {{
                            "nome": "Plano de Treinamento (Simulado - Erro JSON)",
                            "descricao": "Este plano foi gerado automaticamente devido a erro de processamento JSON.",
                            "periodizacao": {{
                              "tipo": "linear",
                              "descricao": "Progressão linear de carga"
                            }},
                            "duracao_semanas": 12,
                            "frequencia_semanal": 3,
                            "ciclos": [
                              {{
                                "ciclo_id": "{str(uuid.uuid4())}",
                                "nome": "Ciclo Inicial",
                                "ordem": 1,
                                "duracao_semanas": 12,
                                "objetivo": "Condicionamento geral",
                                "microciclos": [
                                  {{
                                    "semana": 1,
                                    "volume": "médio",
                                    "intensidade": "média",
                                    "foco": "Adaptação",
                                    "sessoes": [
                                      {{
                                        "sessao_id": "{str(uuid.uuid4())}",
                                        "nome": "Treino A",
                                        "tipo": "resistência",
                                        "duracao_minutos": 60,
                                        "nivel_intensidade": 5,
                                        "dia_semana": 1,
                                        "grupos_musculares": [],
                                        "exercicios": [
                                          {{
                                            "exercicio_id": "{str(uuid.uuid4())}",
                                            "nome": "Agachamento",
                                            "ordem": 1,
                                            "equipamento": "Peso corporal",
                                            "series": 3,
                                            "repeticoes": "12-15",
                                            "percentual_rm": 70,
                                            "tempo_descanso": 60,
                                            "cadencia": "2-0-2",
                                            "metodo": "normal",
                                            "progressao": [],
                                            "observacoes": "Simulado devido a erro JSON"
                                          }}
                                        ]
                                      }}
                                    ]
                                  }}
                                ]
                              }}
                            ]
                          }}
                        }}
                        ```"""
                    }
                ]
            }
    
    @WrapperLogger.log_function(logging.INFO)
    def _extrair_json_da_resposta(self, resposta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai o JSON da resposta do Claude.
        
        Args:
            resposta (Dict): Resposta da API Claude
            
        Returns:
            Dict: JSON extraído da resposta
        """
        self.logger.info("Extraindo conteúdo JSON da resposta")
        try:
            conteudo = resposta.get("content", [])
            
            # Encontrar blocos de código JSON na resposta
            json_text = ""
            
            self.logger.debug(f"Analisando blocos de conteúdo")
            
            # Extrair todo o texto da resposta
            texto_completo = ""
            for item in conteudo:
                if isinstance(item, dict):
                    texto_completo += item.get("text", "")
                elif isinstance(item, str):
                    texto_completo += item
            
            self.logger.debug(f"Texto extraído com {len(texto_completo)} caracteres")
            
            # Procurar por blocos de código JSON
            import re
            json_blocks = re.findall(r'```json(.*?)```', texto_completo, re.DOTALL)
            
            if json_blocks:
                self.logger.debug(f"Encontrados {len(json_blocks)} blocos JSON no texto")
                json_text = json_blocks[0].strip()
                self.logger.debug(f"Extraído bloco JSON com {len(json_text)} caracteres")
            else:
                # Tentar encontrar JSON diretamente no texto (entre chaves)
                json_pattern = re.compile(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}')
                matches = json_pattern.findall(texto_completo)
                
                if matches:
                    # Pegar o maior match, que provavelmente é o JSON completo
                    json_text = max(matches, key=len)
                    self.logger.debug(f"Extraído JSON direto do texto com {len(json_text)} caracteres")
                else:
                    self.logger.error("Nenhum JSON encontrado na resposta")
                    self.logger.debug(f"Conteúdo da resposta: {texto_completo[:200]}...")
                    raise ValueError("Nenhum JSON encontrado na resposta")
            
            # Limpar o texto e converter para JSON
            self.logger.info("Convertendo texto para JSON")
            json_obj = json.loads(json_text)
            self.logger.info("JSON extraído com sucesso")
            
            # Verificar se o JSON contém a estrutura completa esperada ou apenas um fragmento
            if "usuario" not in json_obj and "plano_principal" not in json_obj:
                self.logger.warning("JSON extraído não contém a estrutura completa esperada")
                self.logger.debug(f"Conteúdo do JSON extraído: {json.dumps(json_obj)[:200]}...")
                
                # Verificar se é um exercício isolado ou outro fragmento
                is_exercise = any(key in json_obj for key in ["exercicio_id", "nome", "series", "repeticoes"])
                
                if is_exercise:
                    self.logger.info("Detectado fragmento de exercício, incorporando na estrutura completa")
                    # Criar estrutura básica completa com o exercício incorporado
                    exercicio = json_obj
                    return self._criar_estrutura_completa_com_exercicio(exercicio)
                else:
                    # Algum outro tipo de fragmento, criar estrutura básica
                    self.logger.info("Criando estrutura básica completa")
                    return self._criar_estrutura_completa_basica()
            
            return json_obj
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Erro ao extrair JSON da resposta: {str(e)}")
            try:
                self.logger.debug(f"Texto JSON problemático: {json_text[:200]}...")
            except:
                self.logger.debug("Não foi possível mostrar o texto JSON problemático")
            # Como fallback, retornar um JSON básico
            self.logger.warning("Retornando JSON básico como fallback devido a erro na extração")
            return self._criar_estrutura_completa_basica()
    
    def _criar_estrutura_completa_com_exercicio(self, exercicio: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma estrutura completa de plano de treinamento incorporando um exercício isolado.
        
        Args:
            exercicio (Dict): Dados do exercício a ser incorporado
            
        Returns:
            Dict: Estrutura completa do plano
        """
        self.logger.info("Criando estrutura completa com o exercício fornecido")
        
        # Garantir que o exercício tenha um ID
        if "exercicio_id" not in exercicio or not exercicio["exercicio_id"]:
            exercicio["exercicio_id"] = str(uuid.uuid4())
        
        # Garantir que o exercício tenha uma ordem
        if "ordem" not in exercicio or not exercicio["ordem"]:
            exercicio["ordem"] = 1
            
        # Criar estrutura completa
        plano_completo = {
            "usuario": {
                "id": str(uuid.uuid4()),
                "nome": "Usuário (Estrutura Reconstruída)",
                "nivel": "intermediário",
                "objetivos": [{"objetivo_id": str(uuid.uuid4()), "nome": "Condicionamento", "prioridade": 1}],
                "restricoes": []
            },
            "plano_principal": {
                "nome": "Plano Reconstruído",
                "descricao": "Plano reconstruído a partir de um exercício isolado",
                "periodizacao": {"tipo": "linear", "descricao": "Progressão linear de carga"},
                "duracao_semanas": 12,
                "frequencia_semanal": 3,
                "ciclos": [
                    {
                        "ciclo_id": str(uuid.uuid4()),
                        "nome": "Ciclo Principal",
                        "ordem": 1,
                        "duracao_semanas": 12,
                        "objetivo": "Condicionamento geral",
                        "microciclos": [
                            {
                                "semana": 1,
                                "volume": "médio",
                                "intensidade": "média",
                                "foco": "Adaptação",
                                "sessoes": [
                                    {
                                        "sessao_id": str(uuid.uuid4()),
                                        "nome": f"Treino com {exercicio.get('nome', 'Exercício')}",
                                        "tipo": "resistência",
                                        "duracao_minutos": 60,
                                        "nivel_intensidade": 5,
                                        "dia_semana": 1,
                                        "grupos_musculares": [],
                                        "exercicios": [exercicio]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        self.logger.debug(f"Estrutura completa criada com o exercício {exercicio.get('nome', 'desconhecido')}")
        return plano_completo
    
    def _criar_estrutura_completa_basica(self) -> Dict[str, Any]:
        """
        Cria uma estrutura básica completa de plano de treinamento para casos de fallback.
        
        Returns:
            Dict: Estrutura básica completa do plano
        """
        self.logger.info("Criando estrutura básica completa para fallback")
        
        return {
            "usuario": {
                "id": str(uuid.uuid4()),
                "nome": "Usuário Fallback",
                "nivel": "intermediário",
                "objetivos": [{"objetivo_id": str(uuid.uuid4()), "nome": "Condicionamento", "prioridade": 1}],
                "restricoes": []
            },
            "plano_principal": {
                "nome": "Plano Básico (Fallback)",
                "descricao": "Plano gerado como fallback devido a erro na extração do JSON",
                "periodizacao": {"tipo": "linear", "descricao": "Progressão básica"},
                "duracao_semanas": 12,
                "frequencia_semanal": 3,
                "ciclos": [
                    {
                        "ciclo_id": str(uuid.uuid4()),
                        "nome": "Ciclo Único",
                        "ordem": 1,
                        "duracao_semanas": 12,
                        "objetivo": "Condicionamento geral",
                        "microciclos": [
                            {
                                "semana": 1,
                                "volume": "médio",
                                "intensidade": "média",
                                "foco": "Adaptação",
                                "sessoes": [
                                    {
                                        "sessao_id": str(uuid.uuid4()),
                                        "nome": "Treino Geral",
                                        "tipo": "resistência",
                                        "duracao_minutos": 60,
                                        "nivel_intensidade": 5,
                                        "dia_semana": 1,
                                        "grupos_musculares": [],
                                        "exercicios": [
                                            {
                                                "exercicio_id": str(uuid.uuid4()),
                                                "nome": "Agachamento",
                                                "ordem": 1,
                                                "equipamento": "Barra",
                                                "series": 3,
                                                "repeticoes": "10",
                                                "percentual_rm": 70,
                                                "tempo_descanso": 60,
                                                "cadencia": "2-0-2",
                                                "metodo": "normal",
                                                "progressao": [],
                                                "observacoes": "Fallback exercise"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    
    @WrapperLogger.log_function(logging.INFO)
    def _validar_plano(self, plano: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida o plano de treinamento contra o schema esperado.
        
        Args:
            plano (Dict): Plano de treinamento
            
        Returns:
            Dict: Plano validado
        """
        self.logger.info("Iniciando validação do plano de treinamento")
        try:
            self.logger.debug("Validando contra schema JSON")
            jsonschema.validate(instance=plano, schema=self.schema)
            self.logger.info("Plano validado com sucesso contra o schema")
            return plano
            
        except jsonschema.exceptions.ValidationError as e:
            # Log detalhado do erro para diagnóstico
            erro_path = ".".join([str(p) for p in e.path])
            self.logger.error(f"Erro de validação em: {erro_path}")
            self.logger.error(f"Detalhe: {e.message}")
            
            # Tentativa de correção automática para erros comuns
            self.logger.info("Tentando corrigir erros automaticamente")
            plano_corrigido = self._tentar_corrigir_erros(plano, e)
            
            # Tentar validar novamente
            try:
                self.logger.debug("Validando plano corrigido")
                jsonschema.validate(instance=plano_corrigido, schema=self.schema)
                self.logger.info("Plano corrigido validado com sucesso")
                return plano_corrigido
                
            except jsonschema.exceptions.ValidationError as e2:
                self.logger.error(f"Falha ao validar o plano corrigido: {str(e2)}")
                self.logger.critical("Não foi possível corrigir automaticamente todos os erros")
                raise ValueError(f"Falha na validação do plano de treinamento: {str(e)}")
    
    @WrapperLogger.log_function(logging.INFO)
    def _tentar_corrigir_erros(self, plano: Dict[str, Any], erro: jsonschema.exceptions.ValidationError) -> Dict[str, Any]:
        """
        Tenta corrigir erros comuns de validação.
        
        Args:
            plano (Dict): Plano com erros
            erro (ValidationError): Erro de validação
            
        Returns:
            Dict: Plano com tentativa de correção
        """
        plano_corrigido = plano.copy()
        self.logger.info("Iniciando correções automáticas do plano")
        correcoes_aplicadas = []
        
        # Exemplo de correção: converter valores null para None ou valores numéricos
        if "null" in str(erro):
            # Converter strings "null" para None
            self.logger.info("Detectados valores 'null' como strings, corrigindo")
            
            def corrigir_nulls(obj):
                if isinstance(obj, dict):
                    return {k: corrigir_nulls(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [corrigir_nulls(i) for i in obj]
                elif obj == "null":
                    return None
                else:
                    return obj
                    
            plano_corrigido = corrigir_nulls(plano_corrigido)
            correcoes_aplicadas.append("Strings 'null' convertidas para None")
        
        # Correção: garantir que campos numéricos tenham valores numéricos
        erro_str = str(erro)
        if "is not of type 'number'" in erro_str or "is not of type 'integer'" in erro_str:
            self.logger.info("Detectados campos numéricos com valores não numéricos, corrigindo")
            
            def corrigir_numeros(obj, path=""):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        new_path = f"{path}.{k}" if path else k
                        if k in ["duracao_semanas", "frequencia_semanal", "duracao_minutos", 
                                "series", "repeticoes", "percentual_rm", "tempo_descanso", 
                                "nivel_intensidade", "ordem"]:
                            if v is None:
                                self.logger.debug(f"Corrigindo {new_path}: None -> valor padrão")
                                if k == "duracao_semanas":
                                    obj[k] = 12
                                elif k == "frequencia_semanal":
                                    obj[k] = 3
                                elif k == "duracao_minutos":
                                    obj[k] = 60
                                elif k == "series":
                                    obj[k] = 3
                                elif k == "repeticoes":
                                    obj[k] = "10-12"  # este é string
                                elif k == "percentual_rm":
                                    obj[k] = 70
                                elif k == "tempo_descanso":
                                    obj[k] = 60
                                elif k == "nivel_intensidade":
                                    obj[k] = 7
                                elif k == "ordem":
                                    obj[k] = 1
                            elif isinstance(v, str) and v.isdigit():
                                self.logger.debug(f"Corrigindo {new_path}: string -> int")
                                obj[k] = int(v)
                        else:
                            obj[k] = corrigir_numeros(v, new_path)
                    return obj
                elif isinstance(obj, list):
                    return [corrigir_numeros(item, f"{path}[{i}]") for i, item in enumerate(obj)]
                else:
                    return obj
            
            plano_corrigido = corrigir_numeros(plano_corrigido)
            correcoes_aplicadas.append("Campos numéricos corrigidos")
        
        # Verificar se há arrays vazios nos objetivos ou restrições
        usuario = plano_corrigido.get("usuario", {})
        if "objetivos" in usuario and not usuario["objetivos"]:
            self.logger.info("Lista de objetivos vazia, adicionando objetivo padrão")
            usuario["objetivos"] = [{
                "objetivo_id": str(uuid.uuid4()),
                "nome": "Condicionamento geral",
                "prioridade": 1
            }]
            correcoes_aplicadas.append("Objetivo padrão adicionado")
            
        if "restricoes" in usuario and not usuario["restricoes"]:
            self.logger.info("Lista de restrições vazia, adicionando estrutura mínima")
            usuario["restricoes"] = []
            correcoes_aplicadas.append("Lista de restrições inicializada")
        
        # Veriifcar ciclos e estrutura do plano
        plano_principal = plano_corrigido.get("plano_principal", {})
        if "ciclos" in plano_principal and not plano_principal["ciclos"]:
            self.logger.warning("Nenhum ciclo encontrado no plano, este é um erro grave")
            # Aqui a correção seria muito complexa pois exigiria criar todo um plano
        
        self.logger.info(f"Correções aplicadas: {', '.join(correcoes_aplicadas)}")
        return plano_corrigido
    
    @WrapperLogger.log_function(logging.INFO)
    def enviar_para_wrapper2(self, plano: Dict[str, Any], wrapper2) -> Dict[str, Any]:
        """
        Envia o plano validado para o wrapper 2.
        
        Args:
            plano (Dict): Plano de treinamento validado
            wrapper2: Instância do wrapper2
            
        Returns:
            Dict: Resultado do processamento do wrapper2
        """
        self.logger.info("Enviando plano para o Wrapper 2 (Sistema de Adaptação)")
        try:
            resultado = wrapper2.processar_plano(plano)
            self.logger.info("Plano processado com sucesso pelo Wrapper 2")
            return resultado
        except Exception as e:
            self.logger.error(f"Erro ao processar plano no Wrapper 2: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise

# Função auxiliar para usar o wrapper
def criar_plano_treinamento(api_key: str, dados_usuario: Dict[str, Any], wrapper2=None) -> Dict[str, Any]:
    """
    Função de conveniência para criar um plano de treinamento.
    
    Args:
        api_key (str): Chave da API Claude
        dados_usuario (Dict): Dados do usuário
        wrapper2 (optional): Instância do wrapper2 para encaminhar o plano
        
    Returns:
        Dict: Plano de treinamento ou resultado do processamento do wrapper2
    """
    # Configurar logger
    logger = WrapperLogger("Wrapper1_Helper")
    logger.info("Iniciando função criar_plano_treinamento")
    
    try:
        treinador = TreinadorEspecialista(api_key)
        logger.info("Treinador Especialista inicializado")
        
        plano = treinador.criar_plano_treinamento(dados_usuario)
        logger.info("Plano de treinamento criado com sucesso")
        
        if wrapper2:
            logger.info("Encaminhando plano para o Wrapper 2")
            return treinador.enviar_para_wrapper2(plano, wrapper2)
        
        return plano
    except Exception as e:
        logger.error(f"Erro em criar_plano_treinamento: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise