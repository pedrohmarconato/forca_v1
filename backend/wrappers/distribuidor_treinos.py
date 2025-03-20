# Wrapper 3: Distribuidor dos Treinos para BD #

import json
import copy
import uuid
import datetime
import jsonschema
import os
import traceback
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field

# Importar o WrapperLogger
from logger import WrapperLogger

@dataclass
class TabelaMapping:
    tabela: str
    campos: List[Dict[str, str]] = field(default_factory=list)


class DistribuidorBD:
    def __init__(self, config_db: Optional[Dict[str, Any]] = None):
        """
        Inicializa o Distribuidor de Treinos para o BD.
        
        Args:
            config_db (Dict, optional): Configuração de conexão com o banco de dados
        """
        # Configurar logger
        self.logger = WrapperLogger("Wrapper3_Distribuidor")
        self.logger.info("Inicializando Distribuidor BD")
        
        self.config_db = config_db or {}
        self.logger.debug("Configuração de BD fornecida" if config_db else "Nenhuma configuração de BD fornecida")
        
        try:
            self.schema = self._carregar_schema_json()
            self.logger.info("Schema JSON carregado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao carregar schema JSON: {str(e)}")
            self.logger.warning("Criando schema básico")
            self.schema = self._criar_schema_padrao()
        
        try:
            self.mapeamento_tabelas = self._criar_mapeamento_tabelas()
            self.logger.info("Mapeamento de tabelas criado com sucesso")
            self.logger.debug(f"Tabelas mapeadas: {list(self.mapeamento_tabelas.keys())}")
        except Exception as e:
            self.logger.error(f"Erro ao criar mapeamento de tabelas: {str(e)}")
            raise
        
        self.conexao_db = None
        
        # Níveis de humor atualizados para 5 níveis
        self.niveis_humor = ["muito_cansado", "cansado", "neutro", "disposto", "muito_disposto"]
        
        # Níveis de tempo disponível atualizados para 5 níveis
        self.tempos_disponiveis = ["muito_curto", "curto", "padrao", "longo", "muito_longo"]
        
        self.logger.info("Distribuidor BD inicializado com sucesso")
    
    def _criar_schema_padrao(self) -> Dict:
        """Cria um schema básico quando o arquivo não é encontrado"""
        self.logger.info("Criando schema básico para validação")
        schema_basico = {
            "type": "object",
            "required": ["treinamento_id", "operacao", "timestamp", "dados", "mapeamento_tabelas", "validacao"],
            "properties": {
                "treinamento_id": {"type": "string"},
                "operacao": {"type": "string"},
                "timestamp": {"type": "string"},
                "dados": {"type": "object"},
                "mapeamento_tabelas": {"type": "object"},
                "validacao": {"type": "object"}
            }
        }
        return schema_basico
    
    @WrapperLogger.log_function()
    def _carregar_schema_json(self) -> Dict:
        """Carrega o schema JSON para validação."""
        self.logger.info("Tentando carregar schema_wrapper3.json")
        try:
            with open("schema_wrapper3.json", 'r', encoding='utf-8') as file:
                schema = json.load(file)
                self.logger.debug(f"Schema carregado com sucesso: {len(json.dumps(schema))} caracteres")
                return schema
        except FileNotFoundError:
            self.logger.warning("Arquivo schema_wrapper3.json não encontrado, será criado um schema básico")
            # Retornar None para que a função _criar_schema_padrao seja chamada
            return None
    
    @WrapperLogger.log_function()
    def _criar_mapeamento_tabelas(self) -> Dict[str, TabelaMapping]:
        """
        Cria o mapeamento de campos entre o JSON e as tabelas do banco de dados.
        
        Returns:
            Dict: Mapeamento de campos por tabela
        """
        self.logger.info("Criando mapeamento de tabelas para o banco de dados")
        
        mapeamento = {
            "treinamento": TabelaMapping(
                tabela="Fato_Treinamento",
                campos=[
                    {"json_path": "dados.plano_principal.nome", "tabela_campo": "nome"},
                    {"json_path": "dados.plano_principal.descricao", "tabela_campo": "descricao"},
                    {"json_path": "dados.plano_principal.duracao_semanas", "tabela_campo": "duracao_semanas"},
                    {"json_path": "dados.plano_principal.frequencia_semanal", "tabela_campo": "frequencia_semanal"},
                    {"json_path": "treinamento_id", "tabela_campo": "treinamento_id"},
                    {"json_path": "dados.usuario.id", "tabela_campo": "usuario_id"},
                    {"json_path": "timestamp", "tabela_campo": "data_criacao"},
                    {"json_path": "dados.plano_principal.periodizacao.tipo", "tabela_campo": "tipo_periodizacao"}
                ]
            ),
            "ciclos": TabelaMapping(
                tabela="Fato_CicloTreinamento",
                campos=[
                    {"json_path": "ciclo_id", "tabela_campo": "ciclo_id"},
                    {"json_path": "treinamento_id", "tabela_campo": "treinamento_id"},
                    {"json_path": "nome", "tabela_campo": "nome"},
                    {"json_path": "ordem", "tabela_campo": "ordem"},
                    {"json_path": "duracao_semanas", "tabela_campo": "duracao_semanas"},
                    {"json_path": "objetivo", "tabela_campo": "objetivo_especifico"}
                ]
            ),
            "microciclos": TabelaMapping(
                tabela="Fato_MicrocicloSemanal",
                campos=[
                    {"json_path": "microciclo_id", "tabela_campo": "microciclo_id", "is_generated": True},
                    {"json_path": "ciclo_id", "tabela_campo": "ciclo_id"},
                    {"json_path": "semana", "tabela_campo": "semana"},
                    {"json_path": "volume", "tabela_campo": "volume_planejado"},
                    {"json_path": "intensidade", "tabela_campo": "intensidade_planejada"},
                    {"json_path": "foco", "tabela_campo": "foco"}
                ]
            ),
            "sessoes": TabelaMapping(
                tabela="Fato_SessaoTreinamento",
                campos=[
                    {"json_path": "sessao_id", "tabela_campo": "sessao_id"},
                    {"json_path": "microciclo_id", "tabela_campo": "microciclo_id"},
                    {"json_path": "nome", "tabela_campo": "nome"},
                    {"json_path": "tipo", "tabela_campo": "tipo"},
                    {"json_path": "duracao_minutos", "tabela_campo": "duracao_minutos"},
                    {"json_path": "nivel_intensidade", "tabela_campo": "nivel_intensidade"},
                    {"json_path": "dia_semana", "tabela_campo": "dia_semana"}
                ]
            ),
            "exercicios": TabelaMapping(
                tabela="Fato_ExercicioSessao",
                campos=[
                    {"json_path": "exercicio_id", "tabela_campo": "exercicio_id"},
                    {"json_path": "sessao_id", "tabela_campo": "sessao_id"},
                    {"json_path": "nome", "tabela_campo": "nome"},
                    {"json_path": "ordem", "tabela_campo": "ordem"},
                    {"json_path": "series", "tabela_campo": "series"},
                    {"json_path": "repeticoes", "tabela_campo": "repeticoes"},
                    {"json_path": "percentual_rm", "tabela_campo": "percentual_rm"},
                    {"json_path": "tempo_descanso", "tabela_campo": "tempo_descanso_segundos"},
                    {"json_path": "metodo", "tabela_campo": "metodo_treinamento"}
                ]
            ),
            "adaptacoes_humor": TabelaMapping(
                tabela="Fato_AdaptacaoTreinamento",
                campos=[
                    {"json_path": "adaptacao_id", "tabela_campo": "adaptacao_id"},
                    {"json_path": "sessao_original_id", "tabela_campo": "sessao_original_id"},
                    {"json_path": "tipo", "tabela_campo": "tipo", "valor_fixo": "humor"},
                    {"json_path": "nivel", "tabela_campo": "nivel"},
                    {"json_path": "duracao_ajustada", "tabela_campo": "duracao_ajustada"},
                    {"json_path": "nivel_intensidade_ajustado", "tabela_campo": "nivel_intensidade_ajustado"},
                    {"json_path": "ajustes", "tabela_campo": "ajustes_aplicados", "is_json": True}
                ]
            ),
            "adaptacoes_tempo": TabelaMapping(
                tabela="Fato_AdaptacaoTreinamento",
                campos=[
                    {"json_path": "adaptacao_id", "tabela_campo": "adaptacao_id"},
                    {"json_path": "sessao_original_id", "tabela_campo": "sessao_original_id"},
                    {"json_path": "tipo", "tabela_campo": "tipo", "valor_fixo": "tempo"},
                    {"json_path": "nivel", "tabela_campo": "nivel"},
                    {"json_path": "duracao_alvo", "tabela_campo": "duracao_ajustada"},
                    {"json_path": "estrategia", "tabela_campo": "estrategia"},
                    {"json_path": "exercicios_priorizados", "tabela_campo": "exercicios_priorizados", "is_json": True},
                    {"json_path": "exercicios_removidos", "tabela_campo": "exercicios_removidos", "is_json": True}
                ]
            )
        }
        
        self.logger.debug(f"Criados {len(mapeamento)} mapeamentos de tabelas")
        return mapeamento
    
    @WrapperLogger.log_function()
    def processar_plano(self, plano_adaptado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa o plano adaptado para distribuição no banco de dados.
        
        Args:
            plano_adaptado (Dict): Plano completo com adaptações
            
        Returns:
            Dict: Resultado do processamento
        """
        self.logger.info(f"Iniciando processamento do plano: {plano_adaptado.get('treinamento_id', 'ID não encontrado')}")
        
        # Log informação básica do plano adaptado
        self._log_info_plano_adaptado(plano_adaptado)
        
        # Preparar o plano para o banco de dados
        self.logger.info("Preparando plano para o banco de dados")
        try:
            plano_db = self._preparar_plano_para_bd(plano_adaptado)
            self.logger.info("Plano preparado para o banco de dados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao preparar plano para o banco de dados: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Validar o plano
        self.logger.info("Validando plano para o banco de dados")
        try:
            plano_validado = self._validar_plano(plano_db)
            self.logger.info("Plano validado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao validar plano: {str(e)}")
            self.logger.warning("Continuando com o plano não validado")
            plano_validado = plano_db
        
        # Gerar os comandos SQL ou ORM
        self.logger.info("Gerando comandos para o banco de dados")
        try:
            comandos_db = self._gerar_comandos_db(plano_validado)
            self.logger.info(f"Gerados {len(comandos_db)} comandos para o banco de dados")
            self.logger.debug(f"Tipos de comandos: {self._contar_tipos_comandos(comandos_db)}")
        except Exception as e:
            self.logger.error(f"Erro ao gerar comandos para o banco de dados: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Executar os comandos se houver conexão
        self.logger.info("Executando comandos no banco de dados")
        try:
            resultado = self._executar_comandos_db(comandos_db)
            self.logger.info("Comandos executados com sucesso")
            self.logger.debug(f"Resultado da execução: {json.dumps(resultado)}")
        except Exception as e:
            self.logger.error(f"Erro ao executar comandos no banco de dados: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        return resultado
    
    def _log_info_plano_adaptado(self, plano: Dict[str, Any]) -> None:
        """Registra informações básicas do plano adaptado para depuração"""
        try:
            # Informações básicas do plano
            treinamento_id = plano.get("treinamento_id", "Não especificado")
            usuario = plano.get("usuario", {})
            usuario_id = usuario.get("id", "Não especificado")
            usuario_nome = usuario.get("nome", "Não especificado")
            
            self.logger.info(f"Plano ID: {treinamento_id}")
            self.logger.info(f"Usuário: {usuario_nome} (ID: {usuario_id})")
            
            # Estatísticas de adaptações
            adaptacoes = plano.get("adaptacoes", {})
            
            # Contar adaptações de humor
            humor_adaptacoes = adaptacoes.get("humor", {})
            total_humor = sum(len(adaptacoes_nivel) for nivel, adaptacoes_nivel in humor_adaptacoes.items())
            
            # Contar adaptações de tempo
            tempo_adaptacoes = adaptacoes.get("tempo_disponivel", {})
            total_tempo = sum(len(adaptacoes_nivel) for nivel, adaptacoes_nivel in tempo_adaptacoes.items())
            
            self.logger.info(f"Total de adaptações: {total_humor + total_tempo}")
            self.logger.info(f"Adaptações de humor: {total_humor}")
            self.logger.info(f"Adaptações de tempo: {total_tempo}")
        except Exception as e:
            self.logger.warning(f"Erro ao registrar informações do plano adaptado: {str(e)}")
    
    def _contar_tipos_comandos(self, comandos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Conta os tipos de comandos por tabela"""
        contagem = {}
        for comando in comandos:
            tabela = comando.get("tabela", "desconhecida")
            if tabela not in contagem:
                contagem[tabela] = 0
            contagem[tabela] += 1
        return contagem
    
    @WrapperLogger.log_function()
    def _preparar_plano_para_bd(self, plano_adaptado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara o plano adaptado para o formato do banco de dados.
        
        Args:
            plano_adaptado (Dict): Plano com adaptações
            
        Returns:
            Dict: Plano formatado para o banco de dados
        """
        self.logger.info("Criando estrutura do plano para o banco de dados")
        
        # Criar a estrutura básica
        plano_db = {
            "treinamento_id": plano_adaptado.get("treinamento_id", ""),
            "operacao": "INSERT",
            "timestamp": datetime.datetime.now().isoformat(),
            "dados": {
                "plano_principal": plano_adaptado.get("plano_principal", {}),
                "adaptacoes": plano_adaptado.get("adaptacoes", {})
            },
            "mapeamento_tabelas": self._mapeamento_tabelas_para_json(),
            "validacao": {
                "regras": self._gerar_regras_validacao(),
                "mensagens_erro": []
            },
            "controle_versao": {
                "versao_anterior": plano_adaptado.get("versao", ""),
                "modificacoes": []
            }
        }
        
        # Validar campos obrigatórios
        self.logger.debug("Validando campos obrigatórios do plano")
        self._validar_campos_obrigatorios(plano_db)
        
        self.logger.debug(f"Plano para BD criado com ID: {plano_db['treinamento_id']}")
        return plano_db
    
    @WrapperLogger.log_function()
    def _mapeamento_tabelas_para_json(self) -> Dict[str, Dict[str, Any]]:
        """
        Converte o mapeamento de tabelas para JSON.
        
        Returns:
            Dict: Mapeamento em formato JSON
        """
        self.logger.info("Convertendo mapeamento de tabelas para formato JSON")
        mapeamento_json = {}
        
        for nome_tabela, mapeamento in self.mapeamento_tabelas.items():
            mapeamento_json[nome_tabela] = {
                "tabela": mapeamento.tabela,
                "campos": mapeamento.campos
            }
        
        self.logger.debug(f"Convertidos {len(mapeamento_json)} mapeamentos para JSON")
        return mapeamento_json
    
    @WrapperLogger.log_function()
    def _gerar_regras_validacao(self) -> List[Dict[str, Any]]:
        """
        Gera regras de validação para o plano.
        
        Returns:
            List: Regras de validação
        """
        self.logger.info("Gerando regras de validação para o plano")
        regras = [
            {"campo": "dados.plano_principal.duracao_semanas", "validacao": "numero_positivo"},
            {"campo": "dados.plano_principal.frequencia_semanal", "validacao": "entre_1_e_7"},
            {"campo": "dados.plano_principal.nome", "validacao": "nao_vazio"},
            {"campo": "treinamento_id", "validacao": "unico"}
        ]
        self.logger.debug(f"Geradas {len(regras)} regras de validação")
        return regras
    
    @WrapperLogger.log_function()
    def _validar_campos_obrigatorios(self, plano: Dict[str, Any]) -> None:
        """
        Valida campos obrigatórios e preenche valores padrão quando necessário.
        
        Args:
            plano (Dict): Plano a ser validado
        """
        self.logger.info("Validando e preenchendo campos obrigatórios")
        campos_preenchidos = []
        
        # Validar treinamento_id
        if not plano.get("treinamento_id"):
            plano["treinamento_id"] = str(uuid.uuid4())
            self.logger.warning("treinamento_id não encontrado, gerado novo ID")
            campos_preenchidos.append("treinamento_id")
        
        # Validar timestamp
        if not plano.get("timestamp"):
            plano["timestamp"] = datetime.datetime.now().isoformat()
            self.logger.debug("timestamp não encontrado, gerado novo timestamp")
            campos_preenchidos.append("timestamp")
        
        # Validar plano principal
        plano_principal = plano.get("dados", {}).get("plano_principal", {})
        if not plano_principal.get("nome"):
            plano_principal["nome"] = "Plano de Treinamento Padrão"
            self.logger.warning("Nome do plano não encontrado, usando nome padrão")
            campos_preenchidos.append("dados.plano_principal.nome")
        
        # Outras validações
        if not plano_principal.get("duracao_semanas"):
            plano_principal["duracao_semanas"] = 12
            self.logger.warning("duracao_semanas não encontrada, definida como 12")
            campos_preenchidos.append("dados.plano_principal.duracao_semanas")
            
        if not plano_principal.get("frequencia_semanal"):
            plano_principal["frequencia_semanal"] = 3
            self.logger.warning("frequencia_semanal não encontrada, definida como 3")
            campos_preenchidos.append("dados.plano_principal.frequencia_semanal")
        
        if campos_preenchidos:
            self.logger.info(f"Campos preenchidos automaticamente: {', '.join(campos_preenchidos)}")
        else:
            self.logger.info("Todos os campos obrigatórios já estavam preenchidos")
    
    @WrapperLogger.log_function()
    def _validar_plano(self, plano: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida o plano para o banco de dados contra o schema esperado.
        
        Args:
            plano (Dict): Plano para o banco de dados
            
        Returns:
            Dict: Plano validado
        """
        self.logger.info("Validando plano contra schema JSON")
        mensagens_erro = []
        
        # Validar schema
        try:
            jsonschema.validate(instance=plano, schema=self.schema)
            self.logger.info("Plano validado com sucesso contra o schema")
        except jsonschema.exceptions.ValidationError as e:
            erro_msg = f"Erro de validação: {str(e)}"
            self.logger.error(erro_msg)
            mensagens_erro.append(erro_msg)
        
        # Validar regras de negócio
        self.logger.info("Validando regras de negócio")
        for regra in plano["validacao"]["regras"]:
            campo = regra["campo"]
            validacao = regra["validacao"]
            
            # Obter valor do campo
            valor = self._obter_valor_campo(plano, campo)
            
            # Validar campo conforme regra
            if not self._validar_regra(valor, validacao):
                erro_msg = f"Campo '{campo}' falhou na validação: {validacao}"
                self.logger.error(erro_msg)
                mensagens_erro.append(erro_msg)
            else:
                self.logger.debug(f"Campo '{campo}' passou na validação: {validacao}")
        
        # Atualizar mensagens de erro
        plano["validacao"]["mensagens_erro"] = mensagens_erro
        
        # Se houver erros, tentar corrigir automaticamente quando possível
        if mensagens_erro:
            self.logger.warning(f"Encontrados {len(mensagens_erro)} erros de validação")
            self.logger.info("Tentando corrigir erros automaticamente")
            
            if self._tentar_corrigir_erros(plano, mensagens_erro):
                self.logger.info("Correções aplicadas, validando novamente")
                # Validar novamente após correções
                return self._validar_plano(plano)
            else:
                self.logger.warning("Não foi possível corrigir todos os erros")
        else:
            self.logger.info("Plano validado com sucesso, sem erros encontrados")
        
        return plano
    
    @WrapperLogger.log_function()
    def _obter_valor_campo(self, obj: Dict[str, Any], campo_path: str) -> Any:
        """
        Obtém o valor de um campo a partir de um caminho de acesso.
        
        Args:
            obj (Dict): Objeto a ser acessado
            campo_path (str): Caminho do campo (ex: "dados.usuario.id")
            
        Returns:
            Any: Valor do campo ou None se não encontrado
        """
        self.logger.debug(f"Obtendo valor do campo: {campo_path}")
        partes = campo_path.split('.')
        valor = obj
        
        for parte in partes:
            if isinstance(valor, dict) and parte in valor:
                valor = valor[parte]
            else:
                self.logger.debug(f"Parte '{parte}' não encontrada no caminho '{campo_path}'")
                return None
        
        self.logger.debug(f"Valor obtido para campo '{campo_path}': {valor}")
        return valor
    
    @WrapperLogger.log_function()
    def _validar_regra(self, valor: Any, validacao: str) -> bool:
        """
        Valida um valor com base na regra especificada.
        
        Args:
            valor (Any): Valor a ser validado
            validacao (str): Tipo de validação
            
        Returns:
            bool: True se a validação passou, False caso contrário
        """
        self.logger.debug(f"Validando regra '{validacao}' para valor: {valor}")
        
        if validacao == "numero_positivo":
            resultado = isinstance(valor, (int, float)) and valor > 0
            self.logger.debug(f"Validação 'numero_positivo': {resultado}")
            return resultado
        
        elif validacao == "entre_1_e_7":
            resultado = isinstance(valor, (int, float)) and 1 <= valor <= 7
            self.logger.debug(f"Validação 'entre_1_e_7': {resultado}")
            return resultado
        
        elif validacao == "nao_vazio":
            resultado = valor is not None and (not isinstance(valor, str) or valor.strip() != "")
            self.logger.debug(f"Validação 'nao_vazio': {resultado}")
            return resultado
        
        elif validacao == "unico":
            # Para validação de unicidade, teria que consultar o banco de dados
            # Neste caso simplificado, apenas assume que é válido
            self.logger.debug("Validação 'unico': True (simulada)")
            return True
        
        # Regra desconhecida
        self.logger.warning(f"Regra de validação desconhecida: {validacao}")
        return False
    
    @WrapperLogger.log_function()
    def _tentar_corrigir_erros(self, plano: Dict[str, Any], mensagens_erro: List[str]) -> bool:
        """
        Tenta corrigir erros automaticamente.
        
        Args:
            plano (Dict): Plano com erros
            mensagens_erro (List): Lista de mensagens de erro
            
        Returns:
            bool: True se alguma correção foi aplicada, False caso contrário
        """
        self.logger.info(f"Tentando corrigir {len(mensagens_erro)} erros")
        correcao_aplicada = False
        
        # Aplicar correções para erros comuns
        for erro in mensagens_erro:
            self.logger.debug(f"Analisando erro: {erro}")
            
            if "duracao_semanas" in erro and "numero_positivo" in erro:
                # Corrigir duração de semanas inválida
                self.logger.info("Corrigindo duração de semanas inválida")
                plano["dados"]["plano_principal"]["duracao_semanas"] = 12
                correcao_aplicada = True
            
            elif "frequencia_semanal" in erro and "entre_1_e_7" in erro:
                # Corrigir frequência semanal inválida
                self.logger.info("Corrigindo frequência semanal inválida")
                plano["dados"]["plano_principal"]["frequencia_semanal"] = 3
                correcao_aplicada = True
            
            elif "nome" in erro and "nao_vazio" in erro:
                # Corrigir nome vazio
                self.logger.info("Corrigindo nome vazio")
                plano["dados"]["plano_principal"]["nome"] = "Plano de Treinamento Corrigido"
                correcao_aplicada = True
            
            # Adicionar outras correções conforme necessário
        
        if correcao_aplicada:
            self.logger.info("Correções aplicadas com sucesso")
        else:
            self.logger.warning("Não foi possível aplicar correções para os erros encontrados")
        
        return correcao_aplicada
    
    @WrapperLogger.log_function()
    def _gerar_comandos_db(self, plano: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gera comandos para inserção/atualização no banco de dados.
        
        Args:
            plano (Dict): Plano validado
            
        Returns:
            List: Lista de comandos para o banco de dados
        """
        self.logger.info("Gerando comandos para o banco de dados")
        comandos = []
        
        # Extrair dados principais
        treinamento_id = plano.get("treinamento_id", "")
        plano_principal = plano.get("dados", {}).get("plano_principal", {})
        adaptacoes = plano.get("dados", {}).get("adaptacoes", {})
        
        self.logger.debug(f"Processando plano com ID: {treinamento_id}")
        
        # Gerar comando para treinamento
        self.logger.debug("Gerando comando para tabela Fato_Treinamento")
        comandos.append({
            "tabela": "Fato_Treinamento",
            "operacao": plano.get("operacao", "INSERT"),
            "dados": self._extrair_dados_por_mapeamento(plano, "treinamento"),
            "where": {"treinamento_id": treinamento_id}
        })
        
        # Gerar comandos para ciclos
        self.logger.info(f"Processando ciclos do plano")
        ciclos_count = 0
        microciclos_count = 0
        sessoes_count = 0
        exercicios_count = 0
        
        for ciclo in plano_principal.get("ciclos", []):
            ciclo_id = ciclo.get("ciclo_id", "")
            if not ciclo_id:
                ciclo_id = str(uuid.uuid4())
                ciclo["ciclo_id"] = ciclo_id
                self.logger.warning(f"Gerado novo ciclo_id: {ciclo_id}")
                
            self.logger.debug(f"Processando ciclo: {ciclo_id}")
            ciclo_dados = {**ciclo, "treinamento_id": treinamento_id}
            
            comandos.append({
                "tabela": "Fato_CicloTreinamento",
                "operacao": "INSERT",
                "dados": self._extrair_dados_por_mapeamento(ciclo_dados, "ciclos"),
                "where": {"ciclo_id": ciclo_id}
            })
            ciclos_count += 1
            
            # Gerar comandos para microciclos
            for microciclo in ciclo.get("microciclos", []):
                microciclo_id = microciclo.get("microciclo_id", str(uuid.uuid4()))
                if "microciclo_id" not in microciclo:
                    microciclo["microciclo_id"] = microciclo_id
                    self.logger.debug(f"Gerado novo microciclo_id: {microciclo_id}")
                    
                self.logger.debug(f"Processando microciclo: {microciclo_id}, semana: {microciclo.get('semana', 'N/A')}")
                microciclo_dados = {**microciclo, "microciclo_id": microciclo_id, "ciclo_id": ciclo_id}
                
                comandos.append({
                    "tabela": "Fato_MicrocicloSemanal",
                    "operacao": "INSERT",
                    "dados": self._extrair_dados_por_mapeamento(microciclo_dados, "microciclos"),
                    "where": {"microciclo_id": microciclo_id}
                })
                microciclos_count += 1
                
                # Gerar comandos para sessões
                for sessao in microciclo.get("sessoes", []):
                    sessao_id = sessao.get("sessao_id", "")
                    if not sessao_id:
                        sessao_id = str(uuid.uuid4())
                        sessao["sessao_id"] = sessao_id
                        self.logger.warning(f"Gerado novo sessao_id: {sessao_id}")
                        
                    self.logger.debug(f"Processando sessão: {sessao_id}, nome: {sessao.get('nome', 'N/A')}")
                    sessao_dados = {**sessao, "microciclo_id": microciclo_id}
                    
                    comandos.append({
                        "tabela": "Fato_SessaoTreinamento",
                        "operacao": "INSERT",
                        "dados": self._extrair_dados_por_mapeamento(sessao_dados, "sessoes"),
                        "where": {"sessao_id": sessao_id}
                    })
                    sessoes_count += 1
                    
                    # Gerar comandos para exercícios
                    for exercicio in sessao.get("exercicios", []):
                        exercicio_id = exercicio.get("exercicio_id", "")
                        if not exercicio_id:
                            exercicio_id = str(uuid.uuid4())
                            exercicio["exercicio_id"] = exercicio_id
                            self.logger.debug(f"Gerado novo exercicio_id: {exercicio_id}")
                            
                        self.logger.debug(f"Processando exercício: {exercicio_id}, nome: {exercicio.get('nome', 'N/A')}")
                        exercicio_dados = {**exercicio, "sessao_id": sessao_id}
                        
                        comandos.append({
                            "tabela": "Fato_ExercicioSessao",
                            "operacao": "INSERT",
                            "dados": self._extrair_dados_por_mapeamento(exercicio_dados, "exercicios"),
                            "where": {"exercicio_id": exercicio_id}
                        })
                        exercicios_count += 1
        
        self.logger.info(f"Processados: {ciclos_count} ciclos, {microciclos_count} microciclos, {sessoes_count} sessões, {exercicios_count} exercícios")
        
        # Gerar comandos para adaptações de humor
        self.logger.info("Processando adaptações de humor")
        adaptacoes_humor_count = 0
        
        for nivel, adaptacoes_nivel in adaptacoes.get("humor", {}).items():
            self.logger.debug(f"Processando adaptações de humor para nível: {nivel}")
            
            for adaptacao in adaptacoes_nivel:
                adaptacao_id = adaptacao.get("adaptacao_id", "")
                if not adaptacao_id:
                    adaptacao_id = str(uuid.uuid4())
                    adaptacao["adaptacao_id"] = adaptacao_id
                    self.logger.warning(f"Gerado novo adaptacao_id: {adaptacao_id}")
                
                self.logger.debug(f"Processando adaptação de humor: {adaptacao_id}")
                adaptacao_dados = {**adaptacao, "nivel": nivel}
                
                comandos.append({
                    "tabela": "Fato_AdaptacaoTreinamento",
                    "operacao": "INSERT",
                    "dados": self._extrair_dados_por_mapeamento(adaptacao_dados, "adaptacoes_humor"),
                    "where": {"adaptacao_id": adaptacao_id}
                })
                adaptacoes_humor_count += 1
        
        self.logger.info(f"Processadas {adaptacoes_humor_count} adaptações de humor")
        
        # Gerar comandos para adaptações de tempo
        self.logger.info("Processando adaptações de tempo")
        adaptacoes_tempo_count = 0
        
        for nivel, adaptacoes_nivel in adaptacoes.get("tempo_disponivel", {}).items():
            self.logger.debug(f"Processando adaptações de tempo para nível: {nivel}")
            
            for adaptacao in adaptacoes_nivel:
                adaptacao_id = adaptacao.get("adaptacao_id", "")
                if not adaptacao_id:
                    adaptacao_id = str(uuid.uuid4())
                    adaptacao["adaptacao_id"] = adaptacao_id
                    self.logger.warning(f"Gerado novo adaptacao_id: {adaptacao_id}")
                
                self.logger.debug(f"Processando adaptação de tempo: {adaptacao_id}")
                adaptacao_dados = {**adaptacao, "nivel": nivel}
                
                comandos.append({
                    "tabela": "Fato_AdaptacaoTreinamento",
                    "operacao": "INSERT",
                    "dados": self._extrair_dados_por_mapeamento(adaptacao_dados, "adaptacoes_tempo"),
                    "where": {"adaptacao_id": adaptacao_id}
                })
                adaptacoes_tempo_count += 1
        
        self.logger.info(f"Processadas {adaptacoes_tempo_count} adaptações de tempo")
        self.logger.info(f"Total de comandos gerados: {len(comandos)}")
        
        return comandos
    
    @WrapperLogger.log_function()
    def _extrair_dados_por_mapeamento(self, dados: Dict[str, Any], tipo_mapeamento: str) -> Dict[str, Any]:
        """
        Extrai dados com base no mapeamento de campos.
        
        Args:
            dados (Dict): Dados originais
            tipo_mapeamento (str): Tipo de mapeamento a ser usado
            
        Returns:
            Dict: Dados extraídos conforme mapeamento
        """
        self.logger.debug(f"Extraindo dados usando mapeamento: {tipo_mapeamento}")
        resultado = {}
        
        if tipo_mapeamento not in self.mapeamento_tabelas:
            self.logger.warning(f"Tipo de mapeamento não encontrado: {tipo_mapeamento}")
            return resultado
        
        mapeamento = self.mapeamento_tabelas[tipo_mapeamento]
        
        for campo in mapeamento.campos:
            json_path = campo.get("json_path", "")
            tabela_campo = campo.get("tabela_campo", "")
            is_json = campo.get("is_json", False)
            valor_fixo = campo.get("valor_fixo", None)
            
            # Se tem valor fixo, usar esse valor
            if valor_fixo is not None:
                valor = valor_fixo
                self.logger.debug(f"Usando valor fixo para campo {tabela_campo}: {valor}")
            # Caso contrário, extrair o valor dos dados
            else:
                # Para campos com json_path, extrair por caminho
                if "." in json_path:
                    valor = self._obter_valor_campo(dados, json_path)
                # Para campos diretos, acessar diretamente
                else:
                    valor = dados.get(json_path)
            
            # Converter para JSON se necessário
            if is_json and valor is not None:
                try:
                    valor = json.dumps(valor)
                    self.logger.debug(f"Convertido para JSON: campo {tabela_campo}")
                except Exception as e:
                    self.logger.error(f"Erro ao converter para JSON o campo {tabela_campo}: {str(e)}")
                    valor = "{}"
            
            resultado[tabela_campo] = valor
        
        campos_extraidos = len(resultado)
        self.logger.debug(f"Extraídos {campos_extraidos} campos para {tipo_mapeamento}")
        return resultado
    
    @WrapperLogger.log_function()
    def _executar_comandos_db(self, comandos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executa os comandos no banco de dados.
        
        Args:
            comandos (List): Lista de comandos a serem executados
            
        Returns:
            Dict: Resultado da execução
        """
        # Se não tiver conexão com o banco, apenas retorna os comandos
        if not self.conexao_db:
            self.logger.info("Sem conexão com o banco de dados, retornando comandos para simulação")
            return {
                "status": "simulated",
                "mensagem": "Comandos gerados para simulação",
                "comandos": comandos
            }
        
        # Em um cenário real, aqui seriam executados os comandos no banco de dados
        # Usando a conexão self.conexao_db
        self.logger.info(f"Simulando execução de {len(comandos)} comandos no banco de dados")
        
        # Log de estatísticas de comandos por tabela
        estatisticas = {}
        for comando in comandos:
            tabela = comando.get("tabela", "desconhecida")
            if tabela not in estatisticas:
                estatisticas[tabela] = 0
            estatisticas[tabela] += 1
        
        for tabela, contagem in estatisticas.items():
            self.logger.info(f"Tabela {tabela}: {contagem} comandos")
        
        return {
            "status": "success",
            "mensagem": f"Executados {len(comandos)} comandos no banco de dados",
            "comandos_executados": len(comandos),
            "estatisticas": estatisticas
        }
    
    @WrapperLogger.log_function()
    def conectar_bd(self, config: Dict[str, Any]) -> None:
        """
        Estabelece conexão com o banco de dados.
        
        Args:
            config (Dict): Configuração de conexão
        """
        self.logger.info("Tentando estabelecer conexão com o banco de dados")
        
        # Validar configuração mínima
        campos_obrigatorios = ["host", "porta", "usuario", "database"]
        campos_ausentes = [campo for campo in campos_obrigatorios if campo not in config]
        
        if campos_ausentes:
            self.logger.error(f"Configuração de BD incompleta. Campos ausentes: {', '.join(campos_ausentes)}")
            raise ValueError(f"Configuração de BD incompleta. Campos ausentes: {', '.join(campos_ausentes)}")
        
        # Em um cenário real, esta função estabeleceria a conexão com o banco
        # usando os parâmetros de configuração
        self.logger.info(f"Simulando conexão com BD em {config.get('host')}:{config.get('porta')}")
        self.logger.debug(f"Database: {config.get('database')}, Usuário: {config.get('usuario')}")
        
        self.conexao_db = {
            "status": "connected",
            "config": {k: v if k != "senha" else "***REDACTED***" for k, v in config.items()}
        }
        
        self.logger.info("Conexão com o banco de dados estabelecida com sucesso")
    
    @WrapperLogger.log_function()
    def desconectar_bd(self) -> None:
        """Encerra a conexão com o banco de dados."""
        if not self.conexao_db:
            self.logger.warning("Tentativa de desconexão sem conexão ativa")
            return
            
        self.logger.info("Encerrando conexão com o banco de dados")
        # Em um cenário real, esta função encerraria a conexão
        self.conexao_db = None
        self.logger.info("Conexão com o banco de dados encerrada com sucesso")