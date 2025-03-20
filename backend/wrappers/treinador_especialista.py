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

# Importar o WrapperLogger
from logger import WrapperLogger

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
            self.prompt_template = self._carregar_prompt("/prompt/PROMPT DO TREINADOR ESPECIALISTA.txt")
            self.logger.info("Prompt do treinador carregado com sucesso")
        except FileNotFoundError as e:
            self.logger.error(f"Erro ao carregar prompt do treinador: {str(e)}")
            raise
            
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
        try:
            with open(arquivo_prompt, 'r', encoding='utf-8') as file:
                prompt_content = file.read()
                self.logger.debug(f"Prompt carregado com {len(prompt_content)} caracteres")
                return prompt_content
        except FileNotFoundError:
            self.logger.error(f"Arquivo de prompt '{arquivo_prompt}' não encontrado")
            # Tentar caminho alternativo
            alt_path = os.path.basename(arquivo_prompt)
            self.logger.info(f"Tentando caminho alternativo: {alt_path}")
            try:
                with open(alt_path, 'r', encoding='utf-8') as file:
                    prompt_content = file.read()
                    self.logger.info(f"Prompt carregado do caminho alternativo com sucesso")
                    return prompt_content
            except FileNotFoundError:
                self.logger.critical(f"Prompt não encontrado também no caminho alternativo")
                raise FileNotFoundError(f"Arquivo de prompt '{arquivo_prompt}' não encontrado.")
    
    @WrapperLogger.log_function(logging.INFO)
    def _carregar_schema_json(self) -> Dict:
        """Carrega o schema JSON para validação."""
        self.logger.info("Tentando carregar schema_wrapper1.json")
        try:
            with open("schema_wrapper1.json", 'r', encoding='utf-8') as file:
                schema = json.load(file)
                self.logger.debug(f"Schema carregado com sucesso: {len(schema)} elementos de topo")
                return schema
        except FileNotFoundError:
            self.logger.warning("Arquivo schema_wrapper1.json não encontrado, criando schema básico")
            # Cria um schema básico com base no formato esperado
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
        try:
            with open("JSON para Wrapper 1 Treinador.txt", 'r', encoding='utf-8') as file:
                template = file.read()
                self.logger.debug(f"Template JSON carregado do arquivo com {len(template)} caracteres")
                return template
        except FileNotFoundError:
            self.logger.warning("Arquivo de template JSON não encontrado, usando template simplificado")
            # Template simplificado caso o arquivo não seja encontrado
            template_simplificado = """
            {
              "treinamento_id": "",
              "versao": "",
              "data_criacao": "",
              "usuario": {
                "id": "",
                "nome": "",
                "nivel": "",
                "objetivos": [],
                "restricoes": []
              },
              "plano_principal": {
                "nome": "",
                "descricao": "",
                "periodizacao": {
                  "tipo": "",
                  "descricao": ""
                },
                "duracao_semanas": null,
                "frequencia_semanal": null,
                "ciclos": []
              }
            }
            """
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
        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json"
        }
        
        data = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        self.logger.debug(f"Usando modelo: {data['model']}, max_tokens: {data['max_tokens']}")
        
        try:
            self.logger.info(f"Enviando requisição POST para {self.api_url}")
            response = requests.post(self.api_url, headers=headers, json=data)
            
            self.logger.debug(f"Status da resposta: {response.status_code}")
            
            # Verificar o status da resposta
            if response.status_code != 200:
                self.logger.error(f"Erro na API: status {response.status_code}")
                self.logger.error(f"Resposta da API: {response.text[:500]}...")
                response.raise_for_status()
            
            resposta_json = response.json()
            self.logger.info("Resposta obtida e convertida para JSON com sucesso")
            return resposta_json
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro na requisição HTTP: {str(e)}")
            raise Exception(f"Erro ao fazer requisição para a API Claude: {str(e)}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON da resposta: {str(e)}")
            raise Exception(f"Resposta inválida da API Claude: {str(e)}")
    
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
            
            self.logger.debug(f"Analisando {len(conteudo)} blocos de conteúdo")
            
            for i, item in enumerate(conteudo):
                text = item.get("text", "")
                self.logger.debug(f"Analisando bloco {i+1} com {len(text)} caracteres")
                
                # Procurar por blocos de código JSON
                import re
                json_blocks = re.findall(r'```json(.*?)```', text, re.DOTALL)
                
                if json_blocks:
                    self.logger.debug(f"Encontrados {len(json_blocks)} blocos JSON no texto")
                    json_text = json_blocks[0]
                    break
                
                # Se não encontrar blocos, tentar extrair diretamente
                if text.strip().startswith("{") and text.strip().endswith("}"):
                    self.logger.debug("Encontrado JSON diretamente no texto")
                    json_text = text
            
            if not json_text:
                self.logger.error("Nenhum JSON encontrado na resposta")
                self.logger.debug(f"Conteúdo da resposta: {json.dumps(conteudo)[:500]}...")
                raise ValueError("Nenhum JSON encontrado na resposta")
            
            # Limpar o texto e converter para JSON
            self.logger.info("Convertendo texto para JSON")
            json_obj = json.loads(json_text)
            self.logger.info("JSON extraído com sucesso")
            
            return json_obj
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Erro ao extrair JSON da resposta: {str(e)}")
            self.logger.debug(f"Texto JSON problemático: {json_text[:500]}...")
            raise ValueError(f"Erro ao extrair JSON da resposta: {str(e)}")
    
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