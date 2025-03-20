# Wrapper 2: Sistema de Adaptação do Treinamento #

import json
import copy
import uuid
import datetime
import jsonschema
import os
import traceback
from typing import Dict, Any, List, Optional

# Importar o WrapperLogger
from logger import WrapperLogger

class SistemaAdaptacao:
    def __init__(self):
        """
        Inicializa o Sistema de Adaptação do Treinamento.
        """
        # Configurar logger
        self.logger = WrapperLogger("Wrapper2_Adaptacao")
        self.logger.info("Inicializando Sistema de Adaptação")
        
        try:
            self.prompt_adaptacao = self._carregar_prompt("/prompt/Prompt Sistema de Adaptação.txt")
            self.logger.info("Prompt de adaptação carregado com sucesso")
        except FileNotFoundError as e:
            self.logger.error(f"Erro ao carregar prompt de adaptação: {str(e)}")
            self.logger.warning("Tentando caminho alternativo para o prompt")
            try:
                alt_path = "Prompt Sistema de Adaptação.txt"
                self.prompt_adaptacao = self._carregar_prompt(alt_path)
                self.logger.info("Prompt carregado do caminho alternativo com sucesso")
            except FileNotFoundError as e2:
                self.logger.critical(f"Não foi possível carregar o prompt de adaptação: {str(e2)}")
                raise
        
        try:
            self.schema = self._carregar_schema_json()
            self.logger.info("Schema JSON carregado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao carregar schema JSON: {str(e)}")
            self.logger.info("Criando schema básico")
        
        # Modificado: Ampliado para 5 níveis de humor
        self.niveis_humor = ["muito_cansado", "cansado", "neutro", "disposto", "muito_disposto"]
        self.logger.debug(f"Níveis de humor configurados: {', '.join(self.niveis_humor)}")
        
        # Modificado: Ampliado para 5 tempos disponíveis
        self.tempos_disponiveis = ["muito_curto", "curto", "padrao", "longo", "muito_longo"]
        self.logger.debug(f"Tempos disponíveis configurados: {', '.join(self.tempos_disponiveis)}")
        
    @WrapperLogger.log_function()
    def _carregar_prompt(self, arquivo_prompt: str) -> str:
        """Carrega o prompt do sistema de adaptação de um arquivo."""
        self.logger.info(f"Tentando carregar prompt do arquivo: {arquivo_prompt}")
        try:
            with open(arquivo_prompt, 'r', encoding='utf-8') as file:
                prompt_content = file.read()
                self.logger.debug(f"Prompt carregado com {len(prompt_content)} caracteres")
                return prompt_content
        except FileNotFoundError:
            self.logger.error(f"Arquivo de prompt '{arquivo_prompt}' não encontrado")
            raise FileNotFoundError(f"Arquivo de prompt '{arquivo_prompt}' não encontrado.")
    
    @WrapperLogger.log_function()
    def _carregar_schema_json(self) -> Dict:
        """Carrega o schema JSON para validação."""
        self.logger.info("Tentando carregar schema_wrapper2.json")
        try:
            with open("schema_wrapper2.json", 'r', encoding='utf-8') as file:
                schema = json.load(file)
                self.logger.debug(f"Schema carregado com sucesso: {len(json.dumps(schema))} caracteres")
                return schema
        except FileNotFoundError:
            self.logger.warning("Arquivo schema_wrapper2.json não encontrado, criando schema básico")
            # Cria um schema básico com base no formato esperado
            return {
                "type": "object",
                "required": ["treinamento_id", "versao", "data_criacao", "usuario", "plano_principal", "adaptacoes"],
                "properties": {
                    "treinamento_id": {"type": "string"},
                    "versao": {"type": "string"},
                    "data_criacao": {"type": "string"},
                    "usuario": {"type": "object"},
                    "plano_principal": {"type": "object"},
                    "adaptacoes": {"type": "object"}
                }
            }
    
    @WrapperLogger.log_function()
    def processar_plano(self, plano_principal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa o plano principal e cria adaptações.
        
        Args:
            plano_principal (Dict): Plano principal do treinador
            
        Returns:
            Dict: Plano completo com adaptações
        """
        self.logger.info(f"Iniciando processamento do plano: {plano_principal.get('treinamento_id', 'ID não encontrado')}")
        
        # Log informações básicas do plano
        self._log_info_basica_plano(plano_principal)
        
        # Inicializa o plano adaptado
        self.logger.info("Criando estrutura do plano adaptado")
        plano_adaptado = {
            "treinamento_id": plano_principal.get("treinamento_id", str(uuid.uuid4())),
            "versao": plano_principal.get("versao", "1.0"),
            "data_criacao": datetime.datetime.now().isoformat(),
            "usuario": plano_principal.get("usuario", {}),
            "plano_principal": plano_principal.get("plano_principal", {}),
            "adaptacoes": {}
        }
        
        # Criar adaptações
        self.logger.info("Iniciando criação de adaptações")
        try:
            plano_adaptado["adaptacoes"] = self._criar_adaptacoes(plano_principal)
            self.logger.info("Adaptações criadas com sucesso")
            self._log_resumo_adaptacoes(plano_adaptado["adaptacoes"])
        except Exception as e:
            self.logger.error(f"Erro ao criar adaptações: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Validar o plano adaptado
        self.logger.info("Validando plano adaptado")
        try:
            plano_validado = self._validar_plano(plano_adaptado)
            self.logger.info("Plano adaptado validado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao validar plano adaptado: {str(e)}")
            self.logger.warning("Continuando com o plano não validado")
            plano_validado = plano_adaptado
        
        return plano_validado
    
    def _log_info_basica_plano(self, plano: Dict[str, Any]) -> None:
        """Registra informações básicas do plano para depuração"""
        try:
            usuario = plano.get("usuario", {})
            plano_principal = plano.get("plano_principal", {})
            
            self.logger.info(f"Plano para usuário: {usuario.get('nome', 'Nome não especificado')}")
            self.logger.info(f"Nível do usuário: {usuario.get('nivel', 'não especificado')}")
            self.logger.info(f"Plano: {plano_principal.get('nome', 'Nome não especificado')}")
            self.logger.info(f"Duração: {plano_principal.get('duracao_semanas', 'não especificada')} semanas")
            self.logger.info(f"Frequência: {plano_principal.get('frequencia_semanal', 'não especificada')} treinos/semana")
            
            # Contar ciclos, microciclos e sessões
            ciclos = plano_principal.get("ciclos", [])
            num_ciclos = len(ciclos)
            num_microciclos = sum(len(ciclo.get("microciclos", [])) for ciclo in ciclos)
            
            self.logger.info(f"Estrutura: {num_ciclos} ciclos, {num_microciclos} microciclos")
        except Exception as e:
            self.logger.warning(f"Erro ao registrar informações básicas do plano: {str(e)}")
    
    def _log_resumo_adaptacoes(self, adaptacoes: Dict[str, Any]) -> None:
        """Registra um resumo das adaptações criadas"""
        try:
            # Contar adaptações de humor
            humor_adaptacoes = adaptacoes.get("humor", {})
            total_humor = sum(len(adaptacoes_nivel) for nivel, adaptacoes_nivel in humor_adaptacoes.items())
            
            # Contar adaptações de tempo
            tempo_adaptacoes = adaptacoes.get("tempo_disponivel", {})
            total_tempo = sum(len(adaptacoes_nivel) for nivel, adaptacoes_nivel in tempo_adaptacoes.items())
            
            self.logger.info(f"Total de adaptações criadas: {total_humor + total_tempo}")
            self.logger.info(f"Adaptações de humor: {total_humor}")
            self.logger.info(f"Adaptações de tempo: {total_tempo}")
            
            # Detalhes por nível
            self.logger.debug("Detalhes das adaptações de humor:")
            for nivel, adaptacoes_nivel in humor_adaptacoes.items():
                self.logger.debug(f"  - {nivel}: {len(adaptacoes_nivel)} adaptações")
            
            self.logger.debug("Detalhes das adaptações de tempo:")
            for nivel, adaptacoes_nivel in tempo_adaptacoes.items():
                self.logger.debug(f"  - {nivel}: {len(adaptacoes_nivel)} adaptações")
        except Exception as e:
            self.logger.warning(f"Erro ao registrar resumo das adaptações: {str(e)}")
    
    @WrapperLogger.log_function()
    def _criar_adaptacoes(self, plano_principal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria adaptações para diferentes estados do usuário.
        
        Args:
            plano_principal (Dict): Plano principal
            
        Returns:
            Dict: Adaptações do plano
        """
        self.logger.info("Criando estrutura de adaptações")
        
        # Modificado: Removida a categoria fadiga e lesao_temporaria
        adaptacoes = {
            "humor": {},
            "tempo_disponivel": {}
        }
        
        # Criar adaptações para humor
        self.logger.info("Iniciando criação de adaptações de humor")
        try:
            adaptacoes["humor"] = self._criar_adaptacoes_humor(plano_principal)
            self.logger.info("Adaptações de humor criadas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao criar adaptações de humor: {str(e)}")
            self.logger.error(traceback.format_exc())
            adaptacoes["humor"] = {nivel: [] for nivel in self.niveis_humor}
        
        # Criar adaptações para tempo disponível
        self.logger.info("Iniciando criação de adaptações de tempo disponível")
        try:
            adaptacoes["tempo_disponivel"] = self._criar_adaptacoes_tempo(plano_principal)
            self.logger.info("Adaptações de tempo disponível criadas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao criar adaptações de tempo disponível: {str(e)}")
            self.logger.error(traceback.format_exc())
            adaptacoes["tempo_disponivel"] = {tempo: [] for tempo in self.tempos_disponiveis}
        
        return adaptacoes
    
    @WrapperLogger.log_function()
    def _criar_adaptacoes_humor(self, plano_principal: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Cria adaptações para diferentes níveis de humor.
        
        Args:
            plano_principal (Dict): Plano principal
            
        Returns:
            Dict: Adaptações por nível de humor
        """
        self.logger.info("Criando adaptações de humor para os níveis: " + ", ".join(self.niveis_humor))
        adaptacoes_humor = {}
        
        # Obter as sessões do plano principal
        self.logger.debug("Extraindo todas as sessões do plano principal")
        sessoes = self._extrair_todas_sessoes(plano_principal)
        self.logger.info(f"Encontradas {len(sessoes)} sessões para adaptar")
        
        # Criar adaptações para cada nível de humor
        for nivel in self.niveis_humor:
            self.logger.info(f"Criando adaptações para o nível de humor: {nivel}")
            adaptacoes_humor[nivel] = []
            
            for i, sessao in enumerate(sessoes):
                self.logger.debug(f"Processando sessão {i+1}/{len(sessoes)}: {sessao.get('nome', 'Sem nome')}")
                adaptacao = self._adaptar_sessao_por_humor(sessao, nivel)
                if adaptacao:
                    adaptacoes_humor[nivel].append(adaptacao)
                    self.logger.debug(f"Adaptação criada com ID: {adaptacao.get('adaptacao_id', 'ID não gerado')}")
                else:
                    self.logger.warning(f"Falha ao criar adaptação para sessão {sessao.get('sessao_id', 'ID não encontrado')}")
            
            self.logger.info(f"Total de {len(adaptacoes_humor[nivel])} adaptações criadas para o nível {nivel}")
        
        return adaptacoes_humor
    
    @WrapperLogger.log_function()
    def _criar_adaptacoes_tempo(self, plano_principal: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Cria adaptações para diferentes tempos disponíveis.
        
        Args:
            plano_principal (Dict): Plano principal
            
        Returns:
            Dict: Adaptações por tempo disponível
        """
        self.logger.info("Criando adaptações de tempo para os níveis: " + ", ".join(self.tempos_disponiveis))
        adaptacoes_tempo = {}
        
        # Obter as sessões do plano principal
        sessoes = self._extrair_todas_sessoes(plano_principal)
        self.logger.info(f"Encontradas {len(sessoes)} sessões para adaptar")
        
        # Criar adaptações para cada tempo disponível
        for tempo in self.tempos_disponiveis:
            self.logger.info(f"Criando adaptações para o tempo disponível: {tempo}")
            adaptacoes_tempo[tempo] = []
            
            for i, sessao in enumerate(sessoes):
                self.logger.debug(f"Processando sessão {i+1}/{len(sessoes)}: {sessao.get('nome', 'Sem nome')}")
                try:
                    adaptacao = self._adaptar_sessao_por_tempo(sessao, tempo)
                    if adaptacao:
                        adaptacoes_tempo[tempo].append(adaptacao)
                        self.logger.debug(f"Adaptação criada com ID: {adaptacao.get('adaptacao_id', 'ID não gerado')}")
                    else:
                        self.logger.warning(f"Falha ao criar adaptação para sessão {sessao.get('sessao_id', 'ID não encontrado')}")
                except Exception as e:
                    self.logger.error(f"Erro ao adaptar sessão por tempo: {str(e)}")
                    self.logger.error(traceback.format_exc())
            
            self.logger.info(f"Total de {len(adaptacoes_tempo[tempo])} adaptações criadas para o tempo {tempo}")
        
        return adaptacoes_tempo
    
    @WrapperLogger.log_function()
    def _extrair_todas_sessoes(self, plano_principal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrai todas as sessões do plano principal.
        
        Args:
            plano_principal (Dict): Plano principal
            
        Returns:
            List: Lista de todas as sessões
        """
        self.logger.info("Extraindo todas as sessões do plano")
        todas_sessoes = []
        
        # Navegar através da estrutura do plano para encontrar todas as sessões
        plano = plano_principal.get("plano_principal", {})
        ciclos = plano.get("ciclos", [])
        
        self.logger.debug(f"Encontrados {len(ciclos)} ciclos")
        
        for ciclo_idx, ciclo in enumerate(ciclos):
            ciclo_id = ciclo.get("ciclo_id", f"ciclo_{ciclo_idx}")
            microciclos = ciclo.get("microciclos", [])
            self.logger.debug(f"Ciclo {ciclo_id}: {len(microciclos)} microciclos")
            
            for micro_idx, microciclo in enumerate(microciclos):
                semana = microciclo.get("semana", micro_idx + 1)
                sessoes = microciclo.get("sessoes", [])
                self.logger.debug(f"Microciclo semana {semana}: {len(sessoes)} sessões")
                
                for sessao in sessoes:
                    # Adicionar metadados úteis para referência
                    sessao_completa = copy.deepcopy(sessao)
                    sessao_completa["_ciclo_id"] = ciclo.get("ciclo_id", "")
                    sessao_completa["_semana"] = microciclo.get("semana", 0)
                    todas_sessoes.append(sessao_completa)
        
        self.logger.info(f"Total de {len(todas_sessoes)} sessões extraídas")
        return todas_sessoes
    
    @WrapperLogger.log_function()
    def _adaptar_sessao_por_humor(self, sessao: Dict[str, Any], nivel_humor: str) -> Dict[str, Any]:
        """
        Adapta uma sessão com base no nível de humor.
        
        Args:
            sessao (Dict): Sessão original
            nivel_humor (str): Nível de humor
            
        Returns:
            Dict: Sessão adaptada
        """
        self.logger.info(f"Adaptando sessão {sessao.get('sessao_id', 'ID não encontrado')} para humor: {nivel_humor}")
        
        # Verificar se há exercícios na sessão
        if not sessao.get("exercicios", []):
            self.logger.warning("Sessão sem exercícios, impossível adaptar")
            return None
            
        # Criar o template da adaptação
        adaptacao_id = str(uuid.uuid4())
        self.logger.debug(f"Criando adaptação com ID: {adaptacao_id}")
        
        adaptacao = {
            "adaptacao_id": adaptacao_id,
            "sessao_original_id": sessao.get("sessao_id", ""),
            "ajustes": {
                "intensidade": None,
                "volume": None,
                "foco": "",
                "exercicios_removidos": [],
                "exercicios_adicionados": [],
                "exercicios_modificados": []
            },
            "duracao_ajustada": None,
            "nivel_intensidade_ajustado": None
        }
        
        # Aplicar ajustes com base no nível de humor (5 níveis)
        duracao_original = sessao.get("duracao_minutos", 60)
        intensidade_original = sessao.get("nivel_intensidade", 7)
        exercicios = sessao.get("exercicios", [])
        
        self.logger.debug(f"Valores originais - Duração: {duracao_original}min, Intensidade: {intensidade_original}, Exercícios: {len(exercicios)}")
        
        if nivel_humor == "muito_cansado":
            self.logger.info("Aplicando adaptações para humor 'muito_cansado'")
            adaptacao["ajustes"]["intensidade"] = -0.20  # Redução de 20%
            adaptacao["ajustes"]["volume"] = -0.30  # Redução de 30%
            adaptacao["ajustes"]["foco"] = "Manutenção mínima"
            adaptacao["duracao_ajustada"] = int(duracao_original * 0.7)  # 70% do tempo original
            adaptacao["nivel_intensidade_ajustado"] = max(1, int(intensidade_original * 0.6))  # 60% da intensidade
            
            # Modificar exercícios (simplificação máxima)
            for exercicio in exercicios[:2]:  # Modificar apenas os dois primeiros exercícios
                adaptacao["ajustes"]["exercicios_modificados"].append({
                    "exercicio_id": exercicio.get("exercicio_id", ""),
                    "series_ajuste": -2,  # Reduzir duas séries
                    "repeticoes_ajuste": "-4",  # Reduzir 4 repetições
                    "tempo_descanso_ajuste": 45  # Aumentar 45s de descanso
                })
            
            # Remover exercícios não essenciais
            if len(exercicios) > 3:
                for exercicio in exercicios[2:]:
                    adaptacao["ajustes"]["exercicios_removidos"].append(exercicio.get("exercicio_id", ""))
        
        elif nivel_humor == "cansado":
            self.logger.info("Aplicando adaptações para humor 'cansado'")
            adaptacao["ajustes"]["intensidade"] = -0.15  # Redução de 15%
            adaptacao["ajustes"]["volume"] = -0.20  # Redução de 20%
            adaptacao["ajustes"]["foco"] = "Manutenção"
            adaptacao["duracao_ajustada"] = int(duracao_original * 0.8)  # 80% do tempo original
            adaptacao["nivel_intensidade_ajustado"] = max(1, int(intensidade_original * 0.7))  # 70% da intensidade
            
            # Modificar exercícios
            for exercicio in exercicios[:3]:  # Modificar os três primeiros exercícios
                adaptacao["ajustes"]["exercicios_modificados"].append({
                    "exercicio_id": exercicio.get("exercicio_id", ""),
                    "series_ajuste": -1,  # Reduzir uma série
                    "repeticoes_ajuste": "-2",  # Reduzir 2 repetições
                    "tempo_descanso_ajuste": 30  # Aumentar 30s de descanso
                })
            
            # Remover exercícios acessórios
            if len(exercicios) > 4:
                for exercicio in exercicios[4:]:
                    adaptacao["ajustes"]["exercicios_removidos"].append(exercicio.get("exercicio_id", ""))
        
        elif nivel_humor == "neutro":
            self.logger.info("Aplicando adaptações para humor 'neutro'")
            # Sem alterações
            adaptacao["ajustes"]["intensidade"] = 0
            adaptacao["ajustes"]["volume"] = 0
            adaptacao["ajustes"]["foco"] = "Normal"
            adaptacao["duracao_ajustada"] = duracao_original
            adaptacao["nivel_intensidade_ajustado"] = intensidade_original
        
        elif nivel_humor == "disposto":
            self.logger.info("Aplicando adaptações para humor 'disposto'")
            # Ajustes para melhorar o treino
            adaptacao["ajustes"]["intensidade"] = 0.10  # Aumento de 10%
            adaptacao["ajustes"]["volume"] = 0.15  # Aumento de 15%
            adaptacao["ajustes"]["foco"] = "Progressão"
            adaptacao["duracao_ajustada"] = int(duracao_original * 1.1)  # 110% do tempo original
            adaptacao["nivel_intensidade_ajustado"] = min(10, int(intensidade_original * 1.2))  # 120% da intensidade
            
            # Adicionar exercícios extras
            exercicio_adicional_id = str(uuid.uuid4())
            self.logger.debug(f"Adicionando exercício extra com ID: {exercicio_adicional_id}")
            
            adaptacao["ajustes"]["exercicios_adicionados"] = [
                {
                    "exercicio_id": exercicio_adicional_id,
                    "nome": "Exercício adicional para estado disposto",
                    "ordem": len(exercicios) + 1,
                    "series": 3,
                    "repeticoes": "10-12",
                    "tempo_descanso": 60
                }
            ]
        
        elif nivel_humor == "muito_disposto":
            self.logger.info("Aplicando adaptações para humor 'muito_disposto'")
            # Ajustes para maximizar o treino
            adaptacao["ajustes"]["intensidade"] = 0.20  # Aumento de 20%
            adaptacao["ajustes"]["volume"] = 0.25  # Aumento de 25%
            adaptacao["ajustes"]["foco"] = "Sobrecarga e intensidade máxima"
            adaptacao["duracao_ajustada"] = int(duracao_original * 1.2)  # 120% do tempo original
            adaptacao["nivel_intensidade_ajustado"] = min(10, int(intensidade_original * 1.3))  # 130% da intensidade
            
            # Modificar exercícios para maior intensidade
            for exercicio in exercicios:
                adaptacao["ajustes"]["exercicios_modificados"].append({
                    "exercicio_id": exercicio.get("exercicio_id", ""),
                    "series_ajuste": 1,  # Adicionar uma série
                    "repeticoes_ajuste": "-1",  # Reduzir 1 repetição (aumentar intensidade)
                    "tempo_descanso_ajuste": -10  # Reduzir 10s de descanso
                })
            
            # Adicionar exercícios extras
            exercicio_1_id = str(uuid.uuid4())
            exercicio_2_id = str(uuid.uuid4())
            self.logger.debug(f"Adicionando 2 exercícios extras com IDs: {exercicio_1_id}, {exercicio_2_id}")
            
            adaptacao["ajustes"]["exercicios_adicionados"] = [
                {
                    "exercicio_id": exercicio_1_id,
                    "nome": "Exercício adicional de alta intensidade",
                    "ordem": len(exercicios) + 1,
                    "series": 4,
                    "repeticoes": "8-10",
                    "tempo_descanso": 45
                },
                {
                    "exercicio_id": exercicio_2_id,
                    "nome": "Exercício técnica avançada",
                    "ordem": len(exercicios) + 2,
                    "series": 3,
                    "repeticoes": "6-8",
                    "tempo_descanso": 90
                }
            ]
        
        self.logger.info(f"Adaptação para humor {nivel_humor} concluída com sucesso")
        return adaptacao
    
    @WrapperLogger.log_function()
    def _adaptar_sessao_por_tempo(self, sessao: Dict[str, Any], tempo_disponivel: str) -> Dict[str, Any]:
        """
        Adapta uma sessão com base no tempo disponível.
        
        Args:
            sessao (Dict): Sessão original
            tempo_disponivel (str): Tempo disponível
            
        Returns:
            Dict: Sessão adaptada
        """
        self.logger.info(f"Adaptando sessão {sessao.get('sessao_id', 'ID não encontrado')} para tempo: {tempo_disponivel}")
        
        # Verificar se há exercícios na sessão
        if not sessao.get("exercicios", []):
            self.logger.warning("Sessão sem exercícios, impossível adaptar")
            return None
        
        adaptacao_id = str(uuid.uuid4())
        self.logger.debug(f"Criando adaptação com ID: {adaptacao_id}")
        
        adaptacao = {
            "adaptacao_id": adaptacao_id,
            "sessao_original_id": sessao.get("sessao_id", ""),
            "duracao_alvo": None,
            "estrategia": "",
            "exercicios_priorizados": [],
            "exercicios_removidos": [],
            "exercicios_modificados": [],
            "circuitos": []  # Para técnicas de densidade temporal
        }
        
        # Aplicar adaptações com base no tempo disponível (5 níveis)
        exercicios = sessao.get("exercicios", [])
        self.logger.debug(f"Número de exercícios originais: {len(exercicios)}")
        
        if tempo_disponivel == "muito_curto":  # ~20 minutos
            self.logger.info("Aplicando adaptações para tempo 'muito_curto' (20 minutos)")
            adaptacao["duracao_alvo"] = 20
            adaptacao["estrategia"] = "Mínimo essencial"
            
            # Manter apenas 2-3 exercícios essenciais
            if exercicios:
                # Priorizar primeiros 2 exercícios (normalmente os compostos principais)
                for i, exercicio in enumerate(exercicios[:2]):
                    adaptacao["exercicios_priorizados"].append(exercicio.get("exercicio_id", ""))
                    adaptacao["exercicios_modificados"].append({
                        "exercicio_id": exercicio.get("exercicio_id", ""),
                        "series_ajuste": -1 if i > 0 else 0,  # Manter séries apenas do primeiro exercício
                        "repeticoes_ajuste": "-2",
                        "tempo_descanso_ajuste": -15,
                        "metodo_ajustado": "alta_densidade"
                    })
                
                # Remover todos os outros exercícios
                for exercicio in exercicios[2:]:
                    adaptacao["exercicios_removidos"].append(exercicio.get("exercicio_id", ""))
                
                # Criar um circuito para maximizar eficiência
                if len(exercicios) >= 2:
                    self.logger.debug("Criando circuito para otimizar o tempo")
                    adaptacao["circuitos"].append({
                        "circuito_id": str(uuid.uuid4()),
                        "exercicios": [ex.get("exercicio_id", "") for ex in exercicios[:2]],
                        "repeticoes_circuito": 3,
                        "tempo_descanso_entre_exercicios": 15,
                        "tempo_descanso_entre_circuitos": 45
                    })
        
        elif tempo_disponivel == "curto":  # ~30 minutos
            self.logger.info("Aplicando adaptações para tempo 'curto' (30 minutos)")
            adaptacao["duracao_alvo"] = 30
            adaptacao["estrategia"] = "Foco em compostos"
            
            exercicios = sessao.get("exercicios", [])
            # Priorizar os primeiros 3-4 exercícios
            for i, exercicio in enumerate(exercicios[:4]):
                adaptacao["exercicios_priorizados"].append(exercicio.get("exercicio_id", ""))
                adaptacao["exercicios_modificados"].append({
                    "exercicio_id": exercicio.get("exercicio_id", ""),
                    "series_ajuste": -1 if i > 1 else 0,  # Manter séries dos 2 primeiros 
                    "repeticoes_ajuste": "-1",
                    "tempo_descanso_ajuste": -15,
                    "metodo_ajustado": "superset" if i % 2 == 1 else ""
                })
            
            # Remover exercícios restantes
            for exercicio in exercicios[4:]:
                adaptacao["exercicios_removidos"].append(exercicio.get("exercicio_id", ""))
            
            # Criar supersets quando possível para grupos musculares não conflitantes
            if len(exercicios) >= 4:
                self.logger.debug("Criando supersets para otimizar o tempo")
                # Exemplos de supersets: push/pull, antagonistas, etc.
                adaptacao["circuitos"].append({
                    "circuito_id": str(uuid.uuid4()),
                    "exercicios": [
                        exercicios[0].get("exercicio_id", ""),
                        exercicios[2].get("exercicio_id", "")
                    ],
                    "repeticoes_circuito": 3,
                    "tempo_descanso_entre_exercicios": 10,
                    "tempo_descanso_entre_circuitos": 60
                })
                
                adaptacao["circuitos"].append({
                    "circuito_id": str(uuid.uuid4()),
                    "exercicios": [
                        exercicios[1].get("exercicio_id", ""),
                        exercicios[3].get("exercicio_id", "")
                    ],
                    "repeticoes_circuito": 3,
                    "tempo_descanso_entre_exercicios": 10,
                    "tempo_descanso_entre_circuitos": 60
                })
        
        elif tempo_disponivel == "padrao":  # ~60 minutos (tempo normal)
            self.logger.info("Aplicando adaptações para tempo 'padrao' (60 minutos)")
            adaptacao["duracao_alvo"] = 60
            adaptacao["estrategia"] = "Treino completo"
            # Nenhuma modificação necessária - é o tempo padrão
            # Manter estrutura original, apenas ajustes menores se necessário
            exercicios = sessao.get("exercicios", [])
            for i, exercicio in enumerate(exercicios):
                # Pequenos ajustes apenas para otimização
                if i >= len(exercicios) - 2:  # Últimos exercícios
                    adaptacao["exercicios_modificados"].append({
                        "exercicio_id": exercicio.get("exercicio_id", ""),
                        "series_ajuste": 0,
                        "repeticoes_ajuste": "0",
                        "tempo_descanso_ajuste": 0,
                        "metodo_ajustado": "normal"
                    })
        
        elif tempo_disponivel == "longo":  # ~90 minutos
            self.logger.info("Aplicando adaptações para tempo 'longo' (90 minutos)")
            adaptacao["duracao_alvo"] = 90
            adaptacao["estrategia"] = "Treino expandido"
            
            exercicios = sessao.get("exercicios", [])
            # Aumentar sets ou adicionar variações
            for i, exercicio in enumerate(exercicios):
                adaptacao["exercicios_modificados"].append({
                    "exercicio_id": exercicio.get("exercicio_id", ""),
                    "series_ajuste": 1,  # Adicionar uma série a cada exercício
                    "repeticoes_ajuste": "0",  # Manter repetições
                    "tempo_descanso_ajuste": 10,  # Ligeiro aumento no descanso
                    "metodo_ajustado": "variacao_avancada" if i < 3 else "normal"
                })
            
            # Se tiver menos que 6-7 exercícios, adicionar exercícios complementares
            if len(exercicios) < 6:
                self.logger.debug("Adicionando exercícios complementares")
                adaptacao["exercicios_priorizados"] = [ex.get("exercicio_id", "") for ex in exercicios]
                
                # Exemplo de adição de exercício complementar
                # (Na implementação real, isso seria baseado no tipo de treino)
                exercicio_complementar_id = str(uuid.uuid4())
                adaptacao["exercicios_adicionados"] = [{
                    "exercicio_id": exercicio_complementar_id,
                    "nome": "Exercício complementar de finalização",
                    "ordem": len(exercicios) + 1,
                    "series": 3,
                    "repeticoes": "12-15",
                    "tempo_descanso": 60,
                    "metodo_ajustado": "normal"
                }]
        
        elif tempo_disponivel == "muito_longo":  # ~120 minutos ou mais
            self.logger.info("Aplicando adaptações para tempo 'muito_longo' (120 minutos)")
            adaptacao["duracao_alvo"] = 120
            adaptacao["estrategia"] = "Treino expandido com técnicas avançadas"
            
            exercicios = sessao.get("exercicios", [])
            # Aumentar significativamente o volume e adicionar técnicas avançadas
            for i, exercicio in enumerate(exercicios):
                metodo = "normal"
                if i < 2:
                    metodo = "piramide"  # Para primeiros exercícios
                elif i < 4:
                    metodo = "drop_set"  # Para exercícios intermediários
                else:
                    metodo = "rest_pause"  # Para últimos exercícios
                
                adaptacao["exercicios_modificados"].append({
                    "exercicio_id": exercicio.get("exercicio_id", ""),
                    "series_ajuste": 2,  # Adicionar duas séries a cada exercício
                    "repeticoes_ajuste": "+2" if i >= 4 else "-2",  # Variação de intensidade
                    "tempo_descanso_ajuste": 15 if i < 3 else -10,  # Variação de descanso
                    "metodo_ajustado": metodo
                })
            
            # Adicionar exercícios complementares e de especialização
            self.logger.debug("Adicionando exercícios extras de especialização")
            adaptacao["exercicios_adicionados"] = []
            
            # Exercício complementar 1
            ex1_id = str(uuid.uuid4())
            adaptacao["exercicios_adicionados"].append({
                "exercicio_id": ex1_id,
                "nome": "Exercício complementar de alta intensidade",
                "ordem": len(exercicios) + 1,
                "series": 4,
                "repeticoes": "8-10",
                "tempo_descanso": 90,
                "metodo_ajustado": "drop_set"
            })
            
            # Exercício complementar 2
            ex2_id = str(uuid.uuid4())
            adaptacao["exercicios_adicionados"].append({
                "exercicio_id": ex2_id,
                "nome": "Exercício de especialização muscular",
                "ordem": len(exercicios) + 2,
                "series": 3,
                "repeticoes": "12-15",
                "tempo_descanso": 60,
                "metodo_ajustado": "isometrico"
            })
            
            # Exercício de finalização
            ex3_id = str(uuid.uuid4())
            adaptacao["exercicios_adicionados"].append({
                "exercicio_id": ex3_id,
                "nome": "Exercício de finalização (bombeamento)",
                "ordem": len(exercicios) + 3,
                "series": 2,
                "repeticoes": "20-25",
                "tempo_descanso": 45,
                "metodo_ajustado": "queima"
            })
        
        self.logger.info(f"Adaptação para tempo {tempo_disponivel} concluída com sucesso")
        return adaptacao
    
    @WrapperLogger.log_function()
    def _validar_plano(self, plano: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida o plano adaptado contra o schema esperado.
        
        Args:
            plano (Dict): Plano adaptado
            
        Returns:
            Dict: Plano validado
        """
        self.logger.info("Validando plano adaptado contra o schema")
        try:
            jsonschema.validate(instance=plano, schema=self.schema)
            self.logger.info("Plano adaptado validado com sucesso")
            return plano
        except jsonschema.exceptions.ValidationError as e:
            self.logger.error(f"Erro de validação: {e}")
            self.logger.warning("Tentando corrigir o plano para validação")
            
            # Tentar corrigir o plano para corresponder ao schema
            plano_corrigido = self._corrigir_plano_para_validacao(plano, str(e))
            
            try:
                jsonschema.validate(instance=plano_corrigido, schema=self.schema)
                self.logger.info("Plano corrigido validado com sucesso")
                return plano_corrigido
            except jsonschema.exceptions.ValidationError as e2:
                self.logger.error(f"Falha na correção do plano: {e2}")
                self.logger.warning("Retornando plano não validado (pode causar problemas)")
                # Em um ambiente de produção, implementaríamos correções ou logging adequado
                return plano  # Retorna sem validação em caso de erro
    
    def _corrigir_plano_para_validacao(self, plano: Dict[str, Any], erro_msg: str) -> Dict[str, Any]:
        """
        Tenta corrigir problemas comuns para validação do plano.
        
        Args:
            plano (Dict): Plano com erro de validação
            erro_msg (str): Mensagem de erro da validação
            
        Returns:
            Dict: Plano com tentativas de correção
        """
        self.logger.info("Iniciando correções para validação do plano")
        plano_corrigido = copy.deepcopy(plano)
        
        # Verificar adaptações vazias
        adaptacoes = plano_corrigido.get("adaptacoes", {})
        
        # Corrigir adaptações de humor
        humor = adaptacoes.get("humor", {})
        for nivel in self.niveis_humor:
            if nivel not in humor:
                self.logger.warning(f"Nível de humor '{nivel}' ausente, adicionando lista vazia")
                humor[nivel] = []
        
        # Corrigir adaptações de tempo
        tempo = adaptacoes.get("tempo_disponivel", {})
        for nivel in self.tempos_disponiveis:
            if nivel not in tempo:
                self.logger.warning(f"Nível de tempo '{nivel}' ausente, adicionando lista vazia")
                tempo[nivel] = []
        
        # Verificar campos obrigatórios no plano principal
        if "plano_principal" in plano_corrigido:
            pp = plano_corrigido["plano_principal"]
            
            # Verificar campos essenciais
            if "duracao_semanas" not in pp or pp["duracao_semanas"] is None:
                self.logger.warning("Campo 'duracao_semanas' ausente ou nulo, definindo como 12")
                pp["duracao_semanas"] = 12
                
            if "frequencia_semanal" not in pp or pp["frequencia_semanal"] is None:
                self.logger.warning("Campo 'frequencia_semanal' ausente ou nulo, definindo como 3")
                pp["frequencia_semanal"] = 3
        
        # Verificar campos obrigatórios do usuário
        if "usuario" in plano_corrigido:
            usuario = plano_corrigido["usuario"]
            
            if "id" not in usuario or not usuario["id"]:
                self.logger.warning("ID do usuário ausente, gerando novo ID")
                usuario["id"] = str(uuid.uuid4())
                
            if "objetivos" not in usuario:
                self.logger.warning("Campo 'objetivos' ausente, adicionando lista vazia")
                usuario["objetivos"] = []
                
            if "restricoes" not in usuario:
                self.logger.warning("Campo 'restricoes' ausente, adicionando lista vazia")
                usuario["restricoes"] = []
        
        self.logger.info("Correções para validação concluídas")
        return plano_corrigido
    
    def enviar_para_wrapper3(self, plano_adaptado: Dict[str, Any], wrapper3) -> Dict[str, Any]:
        """
        Envia o plano adaptado para o wrapper 3.
        
        Args:
            plano_adaptado (Dict): Plano adaptado validado
            wrapper3: Instância do wrapper3
            
        Returns:
            Dict: Resultado do processamento do wrapper3
        """
        self.logger.info("Enviando plano adaptado para o Wrapper 3 (Distribuidor BD)")
        try:
            resultado = wrapper3.processar_plano(plano_adaptado)
            self.logger.info("Plano processado com sucesso pelo Wrapper 3")
            return resultado
        except Exception as e:
            self.logger.error(f"Erro ao processar plano no Wrapper 3: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise