#!/usr/bin/env python3
# Script de Inicialização das Tabelas no Supabase #

import sys
import os
import json
import time
import traceback
from typing import Dict, Any, List, Optional, Tuple

# Importar utilitários e wrappers
from backend.utils.config import get_supabase_config
from backend.utils.logger import WrapperLogger
from backend.wrappers.supabase_client import SupabaseWrapper
from backend.wrappers.distribuidor_treinos import DistribuidorBD, TabelaMapping

# Inicializar logger
logger = WrapperLogger("SupabaseInit")

class SupabaseInitializer:
    """
    Classe para inicialização da estrutura de tabelas no Supabase.
    Utiliza as definições de mapeamento do DistribuidorBD para criar as tabelas.
    """
    
    def __init__(self, config: Optional[Dict[str, str]] = None, force_reset: bool = False):
        """
        Inicializa o inicializador do Supabase.
        
        Args:
            config (Dict, optional): Configuração personalizada do Supabase
            force_reset (bool): Se True, recria as tabelas mesmo se já existirem
        """
        logger.info("Inicializando SupabaseInitializer")
        
        # Configuração do Supabase
        self.config = config or get_supabase_config()
        self.force_reset = force_reset
        
        # Obter mapeamento de tabelas do DistribuidorBD
        self.distribuidor = DistribuidorBD(modo_simulacao=True)
        self.mapeamento_tabelas = self.distribuidor.mapeamento_tabelas
        
        # Inicializar cliente Supabase
        logger.info("Conectando ao Supabase...")
        try:
            self.supabase = SupabaseWrapper(
                url=self.config.get('url'),
                api_key=self.config.get('api_key')
            )
            logger.info("Conexão com Supabase estabelecida com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar com Supabase: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _get_data_type(self, field_name: str) -> str:
        """
        Determina o tipo de dados SQL para um campo baseado em seu nome.
        
        Args:
            field_name (str): Nome do campo
            
        Returns:
            str: Tipo de dados SQL
        """
        # Campos de ID sempre são text (UUID)
        if field_name.endswith('_id'):
            return 'text'
        
        # Campos com sufixos específicos
        if any(field_name.endswith(suffix) for suffix in ['_json', '_aplicados']):
            return 'jsonb'
        
        if any(field_name.endswith(suffix) for suffix in ['_min', '_max', '_segundos', '_planejado']):
            return 'integer'
        
        if any(field_name.endswith(suffix) for suffix in ['_rm', '_intensidade']):
            return 'decimal(5,2)'
        
        if field_name.startswith('data_'):
            return 'timestamp with time zone'
        
        # Mapeamento por nome do campo
        field_types = {
            'nome': 'text',
            'descricao': 'text',
            'observacoes': 'text',
            'status': 'text',
            'tipo': 'text',
            'nivel': 'text',
            'foco': 'text',
            'estrategia': 'text',
            'metodo_treinamento': 'text',
            'ordem': 'integer',
            'semana': 'integer',
            'series': 'integer',
            'repeticoes': 'integer',
            'duracao_semanas': 'integer',
            'frequencia_semanal': 'integer',
            'duracao_minutos': 'integer',
            'duracao_ajustada': 'integer',
            'peso_sugerido': 'decimal(6,2)',
            'volume': 'decimal(6,2)',
            'intensidade': 'decimal(5,2)',
            'nivel_intensidade': 'decimal(5,2)',
            'nivel_intensidade_ajustado': 'decimal(5,2)',
            'dia_semana': 'integer',
            'tempo_descanso': 'integer',
            'tempo_descanso_segundos': 'integer',
            'exercicios_priorizados': 'jsonb',
            'exercicios_removidos': 'jsonb',
            'ajustes_aplicados': 'jsonb'
        }
        
        # Retorna o tipo mapeado ou text como padrão
        return field_types.get(field_name, 'text')
    
    def _gerar_sql_criar_tabela(self, tabela_nome: str, campos: List[Dict[str, str]]) -> str:
        """
        Gera o SQL para criar uma tabela.
        
        Args:
            tabela_nome (str): Nome da tabela
            campos (List[Dict]): Lista de campos da tabela
            
        Returns:
            str: SQL para criar a tabela
        """
        logger.info(f"Gerando SQL para criar tabela: {tabela_nome}")
        
        # Identificar campo de chave primária
        campos_unicos = set()
        for campo in campos:
            tabela_campo = campo.get('tabela_campo', '')
            campos_unicos.add(tabela_campo)
        
        # Definir chave primária baseada no nome da tabela
        chave_primaria = None
        for campo in campos_unicos:
            if campo.endswith('_id'):
                # Para Fato_Treinamento, a PK é treinamento_id, etc.
                id_especifico = tabela_nome.lower().replace('fato_', '') + '_id'
                if campo == id_especifico:
                    chave_primaria = campo
                    break
        
        # Se não encontrou chave específica, usa a primeira com _id
        if not chave_primaria:
            for campo in campos_unicos:
                if campo.endswith('_id'):
                    chave_primaria = campo
                    break
        
        # Construir SQL
        sql = f"CREATE TABLE IF NOT EXISTS {tabela_nome} (\n"
        
        # Adicionar campos
        colunas = []
        for campo in sorted(campos_unicos):
            tipo_dados = self._get_data_type(campo)
            
            # Se for a chave primária
            if campo == chave_primaria:
                colunas.append(f"    {campo} {tipo_dados} PRIMARY KEY")
            else:
                colunas.append(f"    {campo} {tipo_dados}")
        
        # Adicionar timestamps padrão
        colunas.append("    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
        colunas.append("    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")
        
        # Juntar todas as definições de colunas
        sql += ",\n".join(colunas)
        sql += "\n);"
        
        logger.debug(f"SQL gerado: {sql}")
        return sql

    def _gerar_sql_indices(self, tabela_nome: str, campos: List[Dict[str, str]]) -> List[str]:
        """
        Gera o SQL para criar índices na tabela.
        
        Args:
            tabela_nome (str): Nome da tabela
            campos (List[Dict]): Lista de campos da tabela
            
        Returns:
            List[str]: Lista de comandos SQL para criar índices
        """
        logger.info(f"Gerando SQL para índices da tabela: {tabela_nome}")
        
        indices = []
        
        # Adicionar índices para campos de chave estrangeira
        campos_unicos = set()
        for campo in campos:
            tabela_campo = campo.get('tabela_campo', '')
            campos_unicos.add(tabela_campo)
        
        for campo in campos_unicos:
            if campo.endswith('_id') and not campo == tabela_nome.lower().replace('fato_', '') + '_id':
                # É uma chave estrangeira (não é a PK da tabela)
                indice_nome = f"idx_{tabela_nome.lower()}_{campo}"
                sql = f"CREATE INDEX IF NOT EXISTS {indice_nome} ON {tabela_nome} ({campo});"
                indices.append(sql)
        
        # Índices adicionais por tabela
        if tabela_nome == "Fato_Treinamento":
            indices.append(f"CREATE INDEX IF NOT EXISTS idx_{tabela_nome.lower()}_usuario ON {tabela_nome} (usuario_id);")
        
        elif tabela_nome == "Fato_SessaoTreinamento":
            indices.append(f"CREATE INDEX IF NOT EXISTS idx_{tabela_nome.lower()}_microciclo ON {tabela_nome} (microciclo_id);")
            indices.append(f"CREATE INDEX IF NOT EXISTS idx_{tabela_nome.lower()}_tipo ON {tabela_nome} (tipo);")
        
        elif tabela_nome == "Fato_ExercicioSessao":
            indices.append(f"CREATE INDEX IF NOT EXISTS idx_{tabela_nome.lower()}_sessao ON {tabela_nome} (sessao_id);")
            indices.append(f"CREATE INDEX IF NOT EXISTS idx_{tabela_nome.lower()}_nome ON {tabela_nome} (nome);")
        
        elif tabela_nome == "Fato_AdaptacaoTreinamento":
            indices.append(f"CREATE INDEX IF NOT EXISTS idx_{tabela_nome.lower()}_sessao ON {tabela_nome} (sessao_original_id);")
            indices.append(f"CREATE INDEX IF NOT EXISTS idx_{tabela_nome.lower()}_tipo ON {tabela_nome} (tipo);")
            indices.append(f"CREATE INDEX IF NOT EXISTS idx_{tabela_nome.lower()}_nivel ON {tabela_nome} (nivel);")
        
        return indices
    
    def _gerar_sql_funcoes(self) -> List[str]:
        """
        Gera o SQL para criar funções e triggers necessários.
        
        Returns:
            List[str]: Lista de comandos SQL para criar funções e triggers
        """
        logger.info("Gerando SQL para funções e triggers")
        
        # Função para atualizar timestamps
        update_timestamp_function = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        return [update_timestamp_function]
    
    def _gerar_sql_triggers(self, tabelas: List[str]) -> List[str]:
        """
        Gera o SQL para criar triggers para atualização automática do updated_at.
        
        Args:
            tabelas (List[str]): Lista de nomes de tabelas
            
        Returns:
            List[str]: Lista de comandos SQL para criar triggers
        """
        logger.info("Gerando SQL para triggers de atualização de timestamp")
        
        triggers = []
        
        for tabela in tabelas:
            trigger_nome = f"trigger_{tabela.lower()}_update_timestamp"
            sql = f"""
            DROP TRIGGER IF EXISTS {trigger_nome} ON {tabela};
            CREATE TRIGGER {trigger_nome}
            BEFORE UPDATE ON {tabela}
            FOR EACH ROW
            EXECUTE PROCEDURE update_updated_at_column();
            """
            triggers.append(sql)
        
        return triggers
    
    def _executar_sql(self, sql: str) -> bool:
        """
        Executa um comando SQL no Supabase.
        
        Args:
            sql (str): Comando SQL a ser executado
            
        Returns:
            bool: True se executado com sucesso, False caso contrário
        """
        logger.debug(f"Executando SQL: {sql}")
        
        try:
            # Verificar se o comando é um CREATE TABLE
            if sql.strip().upper().startswith("CREATE TABLE"):
                # Extrair nome da tabela entre CREATE TABLE e (
                import re
                match = re.search(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)", sql, re.IGNORECASE)
                
                if match:
                    tabela_nome = match.group(1)
                    logger.info(f"Detectado comando CREATE TABLE para {tabela_nome}")
                    
                    # Extrair definição de colunas
                    # Este é um parser simplificado, não lida com todos os tipos SQL complexos
                    colunas_match = re.search(r"\(\s*(.*?)\s*\);", sql, re.DOTALL)
                    if colunas_match:
                        colunas_text = colunas_match.group(1)
                        colunas_defs = [col.strip() for col in colunas_text.split(",")]
                        
                        # Remover definições que não são colunas (como PRIMARY KEY constraints)
                        colunas_filtered = []
                        for col in colunas_defs:
                            if col and not col.upper().startswith("PRIMARY KEY") and not col.upper().startswith("FOREIGN KEY"):
                                col_name = col.split()[0]
                                colunas_filtered.append(col_name)
                        
                        if colunas_filtered:
                            logger.info(f"Colunas: {', '.join(colunas_filtered[:3])}...")
                            
                            # Criamos a tabela usando o Supabase API RLS se possível
                            try:
                                # Aqui usaríamos um enfoque diferente para criação de tabelas
                                # Sem a função RPC exec_sql, podemos ter que fazer um procedimento
                                # mais complexo com REST API para tabelas
                                logger.warning("Criação de tabela direta não suportada sem funções SQL personalizadas")
                                logger.warning("Por favor crie a tabela manualmente no console Supabase")
                                return False
                            except Exception as e:
                                logger.error(f"Erro ao criar tabela {tabela_nome}: {str(e)}")
                                return False
                    else:
                        logger.error("Não foi possível extrair definições de colunas")
                else:
                    logger.error("Não foi possível extrair nome da tabela")
            
            # Verificar se o comando é um CREATE INDEX
            elif sql.strip().upper().startswith("CREATE INDEX"):
                logger.warning("Criação de índice não suportada sem funções SQL personalizadas")
                logger.warning("Por favor crie o índice manualmente no console Supabase")
                return False
                
            # Verificar se é uma função ou trigger
            elif sql.strip().upper().startswith(("CREATE OR REPLACE FUNCTION", "CREATE FUNCTION", "CREATE TRIGGER")):
                logger.warning("Criação de função/trigger não suportada sem funções SQL personalizadas")
                logger.warning("Por favor crie a função/trigger manualmente no console Supabase")
                return False
                
            # Outros comandos SQL
            else:
                logger.warning("Execução de SQL personalizado não suportada sem função exec_sql")
                logger.warning("Por favor execute o comando manualmente no console Supabase")
                return False
                
            # Como não podemos executar o SQL diretamente sem a função exec_sql, 
            # retornamos False para comandos não suportados
            return False
                
        except Exception as e:
            logger.error(f"Exceção ao executar SQL: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def inicializar_database(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Inicializa o banco de dados criando todas as tabelas necessárias.
        
        Returns:
            Tuple[bool, Dict]: (sucesso, resultados detalhados)
        """
        logger.info("Iniciando inicialização do banco de dados")
        
        # Coletar comandos SQL
        comandos_sql = []
        tabelas_criadas = []
        resultados = {
            "tabelas_criadas": 0,
            "indices_criados": 0,
            "funcoes_criadas": 0,
            "triggers_criados": 0,
            "erros": [],
            "detalhes": {}
        }
        
        # 1. Criar funções
        logger.info("Gerando funções...")
        funcoes_sql = self._gerar_sql_funcoes()
        for sql in funcoes_sql:
            comandos_sql.append(("função", sql))
        
        # 2. Criar tabelas
        logger.info("Gerando tabelas...")
        tabelas_processadas = set()
        
        # Processar cada mapeamento de tabela
        for nome_mapeamento, mapeamento in self.mapeamento_tabelas.items():
            tabela_nome = mapeamento.tabela
            
            # Evitar processamento duplicado de tabelas
            if tabela_nome in tabelas_processadas:
                continue
            
            tabelas_processadas.add(tabela_nome)
            logger.info(f"Processando tabela: {tabela_nome}")
            
            # Gerar SQL de criação
            sql_criar = self._gerar_sql_criar_tabela(tabela_nome, mapeamento.campos)
            comandos_sql.append(("tabela", sql_criar))
            tabelas_criadas.append(tabela_nome)
            
            # Gerar SQL de índices
            indices_sql = self._gerar_sql_indices(tabela_nome, mapeamento.campos)
            for sql in indices_sql:
                comandos_sql.append(("índice", sql))
        
        # 3. Criar triggers
        logger.info("Gerando triggers...")
        triggers_sql = self._gerar_sql_triggers(tabelas_criadas)
        for sql in triggers_sql:
            comandos_sql.append(("trigger", sql))
        
        # Execução dos comandos SQL
        logger.info(f"Executando {len(comandos_sql)} comandos SQL")
        
        for tipo, sql in comandos_sql:
            logger.info(f"Executando {tipo}: {sql[:50]}...")
            
            if self._executar_sql(sql):
                # Atualizar contadores
                if tipo == "tabela":
                    resultados["tabelas_criadas"] += 1
                elif tipo == "índice":
                    resultados["indices_criados"] += 1
                elif tipo == "função":
                    resultados["funcoes_criadas"] += 1
                elif tipo == "trigger":
                    resultados["triggers_criados"] += 1
                
                # Registrar sucesso
                if tipo not in resultados["detalhes"]:
                    resultados["detalhes"][tipo] = {"sucesso": 0, "falha": 0}
                resultados["detalhes"][tipo]["sucesso"] += 1
            else:
                # Registrar falha
                if tipo not in resultados["detalhes"]:
                    resultados["detalhes"][tipo] = {"sucesso": 0, "falha": 0}
                resultados["detalhes"][tipo]["falha"] += 1
                
                # Adicionar erro
                resultados["erros"].append(f"Erro ao executar {tipo}: {sql[:100]}...")
                logger.error(f"Falha ao executar {tipo}")
        
        # Resumo da execução
        logger.info("Inicialização do banco de dados concluída")
        logger.info(f"Tabelas criadas: {resultados['tabelas_criadas']}")
        logger.info(f"Índices criados: {resultados['indices_criados']}")
        logger.info(f"Funções criadas: {resultados['funcoes_criadas']}")
        logger.info(f"Triggers criados: {resultados['triggers_criados']}")
        
        if resultados["erros"]:
            logger.warning(f"Ocorreram {len(resultados['erros'])} erros durante a inicialização")
        
        # Definir sucesso baseado na ausência de erros
        sucesso = len(resultados["erros"]) == 0
        return sucesso, resultados

    def verificar_tabelas(self) -> Dict[str, Any]:
        """
        Verifica quais tabelas já existem no banco de dados.
        
        Returns:
            Dict: Informações sobre as tabelas existentes
        """
        logger.info("Verificando tabelas existentes")
        
        try:
            # Simplificado: Assumir que as tabelas precisam ser criadas
            # Uma vez que o Supabase não permite facilmente verificar existência 
            # de tabelas sem funções SQL personalizadas
            tabelas_necessarias = set()
            for mapeamento in self.mapeamento_tabelas.values():
                tabelas_necessarias.add(mapeamento.tabela)
            
            # Tentativa de verificar a existência da tabela principal usando um SELECT
            tabelas_existentes = []
            tabela_teste = "Fato_Treinamento"  # Tabela principal para teste
            
            try:
                # Tentar selecionar com LIMIT 0 apenas para verificar se a tabela existe
                teste_sql = f"SELECT * FROM {tabela_teste} LIMIT 0;"
                resultado_teste = self.supabase.client.table(tabela_teste).select("*").limit(0).execute()
                
                # Se não lançou erro, a tabela existe
                if resultado_teste and 'data' in resultado_teste:
                    logger.info(f"Tabela {tabela_teste} existe")
                    tabelas_existentes.append(tabela_teste)
                
            except Exception as e:
                logger.info(f"Tabela {tabela_teste} não existe: {str(e)}")
                # Tabela não existe, continua com lista vazia
            
            # Determinar tabelas faltantes
            tabelas_faltantes = sorted(tabelas_necessarias - set(tabelas_existentes))
            completo = len(tabelas_faltantes) == 0
            
            return {
                "status": "success",
                "tabelas_existentes": tabelas_existentes,
                "tabelas_necessarias": sorted(tabelas_necessarias),
                "tabelas_faltantes": tabelas_faltantes,
                "completo": completo
            }
                
        except Exception as e:
            logger.error(f"Exceção ao verificar tabelas: {str(e)}")
            return {
                "status": "error",
                "mensagem": str(e)
            }
    
    def resetar_database(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Apaga todas as tabelas e recria o banco de dados.
        
        Returns:
            Tuple[bool, Dict]: (sucesso, resultados detalhados)
        """
        logger.warning("Iniciando RESET do banco de dados - TODOS OS DADOS SERÃO PERDIDOS")
        
        # Verificar tabelas existentes
        resultado_verificacao = self.verificar_tabelas()
        
        if resultado_verificacao.get("status") != "success":
            logger.error("Não foi possível verificar tabelas existentes")
            return False, {
                "status": "error",
                "mensagem": "Falha ao verificar tabelas existentes"
            }
        
        # Remover tabelas existentes
        tabelas_existentes = resultado_verificacao.get("tabelas_existentes", [])
        
        # Filtrar apenas tabelas do nosso sistema (Fato_*)
        tabelas_sistema = [tabela for tabela in tabelas_existentes if tabela.startswith("Fato_")]
        
        if not tabelas_sistema:
            logger.info("Nenhuma tabela do sistema encontrada para resetar")
        else:
            logger.warning(f"Removendo {len(tabelas_sistema)} tabelas")
            
            for tabela in tabelas_sistema:
                sql = f"DROP TABLE IF EXISTS {tabela} CASCADE;"
                logger.info(f"Removendo tabela: {tabela}")
                
                if not self._executar_sql(sql):
                    logger.error(f"Erro ao remover tabela {tabela}")
                    return False, {
                        "status": "error",
                        "mensagem": f"Erro ao remover tabela {tabela}"
                    }
        
        # Recriar as tabelas
        logger.info("Recriando tabelas")
        return self.inicializar_database()

def main():
    """Função principal para execução do script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Inicialização das tabelas no Supabase')
    parser.add_argument('--reset', action='store_true', help='Resetar banco de dados (remove todas as tabelas)')
    parser.add_argument('--check', action='store_true', help='Apenas verificar tabelas existentes')
    args = parser.parse_args()
    
    logger.info("Iniciando script de inicialização Supabase")
    
    try:
        # Inicializar
        inicializador = SupabaseInitializer()
        
        if args.check:
            # Apenas verificar tabelas
            resultado = inicializador.verificar_tabelas()
            
            if resultado.get("status") == "success":
                print("\n--- Verificação de Tabelas ---")
                print(f"Tabelas existentes: {len(resultado.get('tabelas_existentes', []))}")
                print(f"Tabelas necessárias: {len(resultado.get('tabelas_necessarias', []))}")
                print(f"Tabelas faltantes: {len(resultado.get('tabelas_faltantes', []))}")
                
                if resultado.get("completo"):
                    print("\nStatus: COMPLETO - Todas as tabelas necessárias existem")
                else:
                    print("\nStatus: INCOMPLETO - Faltam tabelas")
                    
                    if resultado.get("tabelas_faltantes"):
                        print("\nTabelas faltantes:")
                        for tabela in resultado.get("tabelas_faltantes", []):
                            print(f"  - {tabela}")
            else:
                print("\n--- Erro na Verificação ---")
                print(f"Mensagem: {resultado.get('mensagem')}")
            
        elif args.reset:
            # Resetar banco de dados
            confirmacao = input("ATENÇÃO: Você está prestes a APAGAR TODAS as tabelas e dados. Digite 'CONFIRMAR' para prosseguir: ")
            
            if confirmacao != "CONFIRMAR":
                print("Operação cancelada pelo usuário.")
                return
            
            print("\nRessetando banco de dados...")
            sucesso, resultado = inicializador.resetar_database()
            
            if sucesso:
                print("\n--- Reset Concluído com Sucesso ---")
                print(f"Tabelas criadas: {resultado['tabelas_criadas']}")
                print(f"Índices criados: {resultado['indices_criados']}")
                print(f"Funções criadas: {resultado['funcoes_criadas']}")
                print(f"Triggers criados: {resultado['triggers_criados']}")
            else:
                print("\n--- Reset Concluído com Erros ---")
                print(f"Erros: {len(resultado['erros'])}")
                
                if resultado['erros']:
                    print("\nPrimeiros erros:")
                    for erro in resultado['erros'][:3]:
                        print(f"  - {erro}")
                
        else:
            # Inicializar banco de dados
            verificacao = inicializador.verificar_tabelas()
            
            if verificacao.get("status") == "success" and verificacao.get("completo"):
                print("\nTodas as tabelas necessárias já existem. Use --reset para forçar a recriação.")
                return
            
            print("\nInicializando banco de dados...")
            sucesso, resultado = inicializador.inicializar_database()
            
            if sucesso:
                print("\n--- Inicialização Concluída com Sucesso ---")
                print(f"Tabelas criadas: {resultado['tabelas_criadas']}")
                print(f"Índices criados: {resultado['indices_criados']}")
                print(f"Funções criadas: {resultado['funcoes_criadas']}")
                print(f"Triggers criados: {resultado['triggers_criados']}")
            else:
                print("\n--- Inicialização Concluída com Erros ---")
                print(f"Erros: {len(resultado['erros'])}")
                
                if resultado['erros']:
                    print("\nPrimeiros erros:")
                    for erro in resultado['erros'][:3]:
                        print(f"  - {erro}")
    
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"\nErro: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())