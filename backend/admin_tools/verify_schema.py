#!/usr/bin/env python3
# Utilitário para verificação do esquema do banco de dados

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional, Tuple

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    # Tentar importar as dependências
    from backend.utils.logger import WrapperLogger
    from backend.utils.config import get_supabase_config
    from backend.wrappers.supabase_client import SupabaseWrapper
except ImportError as e:
    print(f"Erro ao importar dependências: {e}")
    print("Certifique-se de ter instalado todas as dependências necessárias:")
    print("  pip install -r backend/api/requirements.txt")
    sys.exit(1)

# Inicializar logger
logger = WrapperLogger("SchemaVerifier")

class SchemaVerifier:
    """
    Classe para verificar e diagnosticar problemas no esquema do banco de dados.
    """
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        Inicializa o verificador de esquema.
        
        Args:
            config: Configuração do Supabase (opcional)
        """
        logger.info("Inicializando verificador de esquema")
        
        # Configuração do Supabase
        self.config = config or get_supabase_config()
        
        # Conectar ao Supabase
        try:
            logger.info("Conectando ao Supabase...")
            self.supabase = SupabaseWrapper(
                url=self.config.get('url'),
                api_key=self.config.get('api_key')
            )
            logger.info("Conexão estabelecida com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar com Supabase: {str(e)}")
            raise
    
    def verify_table_exists(self, table_name: str) -> bool:
        """
        Verifica se uma tabela existe no banco de dados.
        
        Args:
            table_name: Nome da tabela a verificar
            
        Returns:
            True se a tabela existe, False caso contrário
        """
        logger.info(f"Verificando existência da tabela: {table_name}")
        
        try:
            # Tentar fazer uma consulta simples para verificar se a tabela existe
            result = self.supabase.client.from_('information_schema.tables') \
                .select('table_name') \
                .eq('table_name', table_name) \
                .execute()
            
            exists = len(result.data) > 0
            logger.info(f"Tabela {table_name}: {'Existe' if exists else 'Não existe'}")
            return exists
        except Exception as e:
            logger.error(f"Erro ao verificar tabela {table_name}: {str(e)}")
            return False
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Obtém todas as colunas de uma tabela.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Lista de dicionários com informações das colunas
        """
        logger.info(f"Obtendo colunas da tabela: {table_name}")
        
        try:
            # Consultar o information_schema para obter as colunas
            result = self.supabase.client.from_('information_schema.columns') \
                .select('column_name,data_type,is_nullable,column_default') \
                .eq('table_name', table_name) \
                .order('ordinal_position') \
                .execute()
            
            columns = result.data
            logger.info(f"Encontradas {len(columns)} colunas na tabela {table_name}")
            return columns
        except Exception as e:
            logger.error(f"Erro ao obter colunas da tabela {table_name}: {str(e)}")
            return []
    
    def get_table_indices(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Obtém todos os índices de uma tabela.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Lista de dicionários com informações dos índices
        """
        logger.info(f"Obtendo índices da tabela: {table_name}")
        
        try:
            # Consultar os índices usando uma função personalizada do Supabase
            # ou via RPC se disponível
            query = f"""
            SELECT
                i.relname as index_name,
                a.attname as column_name,
                ix.indisunique as is_unique
            FROM
                pg_class t,
                pg_class i,
                pg_index ix,
                pg_attribute a
            WHERE
                t.oid = ix.indrelid
                and i.oid = ix.indexrelid
                and a.attrelid = t.oid
                and a.attnum = ANY(ix.indkey)
                and t.relkind = 'r'
                and t.relname = '{table_name}'
            ORDER BY
                i.relname, a.attnum;
            """
            
            # Executar a consulta via RPC se possível (requer função personalizada)
            try:
                result = self.supabase.client.rpc('exec_sql', {'query': query}).execute()
                indices = result.data
            except Exception:
                # Se a função RPC não existir, retornar lista vazia
                # (limitação da API Supabase)
                logger.warning("Função RPC 'exec_sql' não disponível. Não é possível listar índices via API.")
                indices = []
            
            logger.info(f"Encontrados {len(indices)} índices na tabela {table_name}")
            return indices
        except Exception as e:
            logger.error(f"Erro ao obter índices da tabela {table_name}: {str(e)}")
            return []
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Obtém todas as chaves estrangeiras de uma tabela.
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Lista de dicionários com informações das FKs
        """
        logger.info(f"Obtendo chaves estrangeiras da tabela: {table_name}")
        
        try:
            # Consultar as chaves estrangeiras usando uma função personalizada
            # ou via RPC se disponível
            query = f"""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = '{table_name}';
            """
            
            # Executar a consulta via RPC se possível (requer função personalizada)
            try:
                result = self.supabase.client.rpc('exec_sql', {'query': query}).execute()
                foreign_keys = result.data
            except Exception:
                # Se a função RPC não existir, retornar lista vazia
                logger.warning("Função RPC 'exec_sql' não disponível. Não é possível listar FKs via API.")
                foreign_keys = []
            
            logger.info(f"Encontradas {len(foreign_keys)} chaves estrangeiras na tabela {table_name}")
            return foreign_keys
        except Exception as e:
            logger.error(f"Erro ao obter chaves estrangeiras da tabela {table_name}: {str(e)}")
            return []
    
    def verify_schema(self, tables: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Verifica todo o esquema do banco de dados ou um conjunto específico de tabelas.
        
        Args:
            tables: Lista opcional de tabelas para verificar. Se None, verifica todas.
            
        Returns:
            Relatório completo da verificação
        """
        logger.info("Iniciando verificação completa do esquema")
        
        # Lista padrão de tabelas a verificar
        all_tables = [
            # Dimensões
            'dim_usuario', 'dim_objetivo', 'dim_restricao', 'dim_grupomuscular',
            'dim_exercicio', 'dim_modeloperiodizacao', 'dim_metodotreinamento',
            'dim_tiposessao', 'dim_variaveltreinamento', 'dim_humor', 'dim_tempodisponivel',
            
            # Fatos
            'fato_treinamento', 'fato_ciclotreinamento', 'fato_microciclosemanal',
            'fato_sessaotreinamento', 'fato_sessaogrupomusuclar', 'fato_exerciciossessao',
            'fato_usuarioobjetivo', 'fato_usuariorestricao', 'fato_adaptacaotreinamento',
            'fato_aquecimentodesaquecimento', 'fato_exercicioaquecimento',
            'fato_progressaoexercicio', 'fato_substituicaoexercicio', 'fato_registrotreino',
            'fato_registroexercicio', 'fato_metricaprogresso'
        ]
        
        # Usar todas as tabelas ou apenas as especificadas
        tables_to_verify = tables or all_tables
        
        # Inicializar relatório
        report = {
            "status": "success",
            "tables_count": len(tables_to_verify),
            "tables_existing": 0,
            "tables_missing": 0,
            "tables": {}
        }
        
        # Verificar cada tabela
        for table_name in tables_to_verify:
            table_report = {"exists": False, "columns": [], "indices": [], "foreign_keys": []}
            
            # Verificar se a tabela existe
            if self.verify_table_exists(table_name):
                table_report["exists"] = True
                report["tables_existing"] += 1
                
                # Obter e incluir colunas
                table_report["columns"] = self.get_table_columns(table_name)
                
                # Obter e incluir índices (se possível)
                table_report["indices"] = self.get_table_indices(table_name)
                
                # Obter e incluir chaves estrangeiras (se possível)
                table_report["foreign_keys"] = self.get_foreign_keys(table_name)
            else:
                report["tables_missing"] += 1
            
            # Adicionar relatório da tabela ao relatório geral
            report["tables"][table_name] = table_report
        
        logger.info("Verificação de esquema concluída")
        logger.info(f"Tabelas encontradas: {report['tables_existing']}/{report['tables_count']}")
        logger.info(f"Tabelas faltantes: {report['tables_missing']}")
        
        return report
    
    def verify_specific_columns(self, table_name: str, expected_columns: List[str]) -> Dict[str, Any]:
        """
        Verifica se uma tabela contém colunas específicas.
        
        Args:
            table_name: Nome da tabela
            expected_columns: Lista de nomes de colunas esperadas
            
        Returns:
            Relatório sobre as colunas existentes e faltantes
        """
        logger.info(f"Verificando colunas específicas na tabela {table_name}")
        
        # Verificar se a tabela existe
        if not self.verify_table_exists(table_name):
            return {
                "status": "error",
                "message": f"Tabela {table_name} não existe",
                "exists": False,
                "columns_found": [],
                "columns_missing": expected_columns
            }
        
        # Obter colunas existentes
        existing_columns = self.get_table_columns(table_name)
        existing_column_names = [col['column_name'] for col in existing_columns]
        
        # Verificar quais colunas existem e quais estão faltando
        columns_found = []
        columns_missing = []
        
        for column in expected_columns:
            if column in existing_column_names:
                columns_found.append(column)
            else:
                columns_missing.append(column)
        
        # Montar relatório
        report = {
            "status": "success",
            "exists": True,
            "total_expected": len(expected_columns),
            "columns_found": columns_found,
            "columns_missing": columns_missing,
            "all_columns_exist": len(columns_missing) == 0
        }
        
        logger.info(f"Verificação concluída: {len(columns_found)} colunas encontradas, {len(columns_missing)} faltantes")
        return report
    
    def check_index_exists(self, table_name: str, index_name: str) -> bool:
        """
        Verifica se um índice específico existe.
        
        Args:
            table_name: Nome da tabela
            index_name: Nome do índice
            
        Returns:
            True se o índice existe, False caso contrário
        """
        logger.info(f"Verificando existência do índice {index_name} na tabela {table_name}")
        
        indices = self.get_table_indices(table_name)
        index_names = set(idx.get('index_name') for idx in indices)
        
        exists = index_name in index_names
        logger.info(f"Índice {index_name}: {'Existe' if exists else 'Não existe'}")
        return exists

def print_table_report(report: Dict[str, Any], table_name: str) -> None:
    """
    Imprime o relatório de uma tabela específica.
    
    Args:
        report: Relatório completo
        table_name: Nome da tabela a imprimir
    """
    table_info = report["tables"].get(table_name, {})
    
    print(f"\n===== TABELA: {table_name} =====")
    print(f"Existe: {'Sim' if table_info.get('exists', False) else 'Não'}")
    
    if table_info.get('exists', False):
        # Imprimir colunas
        print("\nCOLUNAS:")
        print("-" * 80)
        print(f"{'NOME':<30} {'TIPO':<25} {'NULLABLE':<10} {'DEFAULT':<15}")
        print("-" * 80)
        
        for column in table_info.get('columns', []):
            print(f"{column.get('column_name', ''):<30} "
                  f"{column.get('data_type', ''):<25} "
                  f"{column.get('is_nullable', ''):<10} "
                  f"{(column.get('column_default', '') or ''):<15}")
        
        # Imprimir índices
        indices = table_info.get('indices', [])
        if indices:
            print("\nÍNDICES:")
            print("-" * 60)
            print(f"{'NOME':<30} {'COLUNA':<20} {'UNIQUE':<10}")
            print("-" * 60)
            
            for index in indices:
                print(f"{index.get('index_name', ''):<30} "
                      f"{index.get('column_name', ''):<20} "
                      f"{'Sim' if index.get('is_unique') else 'Não':<10}")
        else:
            print("\nÍNDICES: Não disponíveis (requer função RPC 'exec_sql')")
        
        # Imprimir chaves estrangeiras
        foreign_keys = table_info.get('foreign_keys', [])
        if foreign_keys:
            print("\nCHAVES ESTRANGEIRAS:")
            print("-" * 80)
            print(f"{'NOME':<30} {'COLUNA':<20} {'REFERENCIA':<30}")
            print("-" * 80)
            
            for fk in foreign_keys:
                reference = f"{fk.get('foreign_table_name', '')}.{fk.get('foreign_column_name', '')}"
                print(f"{fk.get('constraint_name', ''):<30} "
                      f"{fk.get('column_name', ''):<20} "
                      f"{reference:<30}")
        else:
            print("\nCHAVES ESTRANGEIRAS: Não disponíveis (requer função RPC 'exec_sql')")

def print_columns_report(report: Dict[str, Any]) -> None:
    """
    Imprime o relatório de verificação de colunas específicas.
    
    Args:
        report: Relatório de verificação de colunas
    """
    print("\n===== VERIFICAÇÃO DE COLUNAS =====")
    print(f"Status: {report['status']}")
    print(f"Tabela existe: {'Sim' if report.get('exists', False) else 'Não'}")
    
    if report.get('exists', False):
        print(f"\nColunas esperadas: {report.get('total_expected', 0)}")
        print(f"Colunas encontradas: {len(report.get('columns_found', []))}")
        print(f"Colunas faltantes: {len(report.get('columns_missing', []))}")
        
        if report.get('columns_missing'):
            print("\nColunas faltantes:")
            for column in report.get('columns_missing', []):
                print(f"  - {column}")

def main():
    """Função principal para execução do script."""
    parser = argparse.ArgumentParser(description='Verificador de esquema de banco de dados')
    parser.add_argument('--table', '-t', help='Verificar apenas uma tabela específica')
    parser.add_argument('--all', '-a', action='store_true', help='Verificar todas as tabelas')
    parser.add_argument('--columns', '-c', help='Verificar colunas específicas (separadas por vírgula)')
    parser.add_argument('--output', '-o', help='Arquivo de saída para o relatório JSON')
    args = parser.parse_args()
    
    try:
        # Inicializar verificador
        verifier = SchemaVerifier()
        
        if args.table and args.columns:
            # Verificar colunas específicas em uma tabela
            columns = [col.strip() for col in args.columns.split(',')]
            report = verifier.verify_specific_columns(args.table, columns)
            print_columns_report(report)
        elif args.table:
            # Verificar uma tabela específica
            report = verifier.verify_schema([args.table])
            print_table_report(report, args.table)
        else:
            # Verificar todas as tabelas
            report = verifier.verify_schema()
            
            # Imprimir resumo geral
            print("\n===== RESUMO DA VERIFICAÇÃO =====")
            print(f"Total de tabelas verificadas: {report['tables_count']}")
            print(f"Tabelas existentes: {report['tables_existing']}")
            print(f"Tabelas faltantes: {report['tables_missing']}")
            
            if report['tables_missing'] > 0:
                print("\nTabelas faltantes:")
                for table_name, table_info in report['tables'].items():
                    if not table_info.get('exists', False):
                        print(f"  - {table_name}")
            
            # Imprimir detalhes da tabela fato_adaptacaotreinamento (foco do problema)
            if 'fato_adaptacaotreinamento' in report['tables']:
                print_table_report(report, 'fato_adaptacaotreinamento')
        
        # Salvar relatório em um arquivo se solicitado
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nRelatório salvo em: {args.output}")
        
        # Conselhos para resolver problemas
        if report.get('tables_missing', 0) > 0:
            print("\n===== CONSELHOS PARA RESOLVER PROBLEMAS =====")
            print("1. Para criar tabelas faltantes, execute o script create_indices.sql")
            print("2. Se houver problemas ao executar o script completo, separe-o em partes menores")
            print("3. Verifique as mensagens de erro no Console do Supabase durante a execução de scripts SQL")
        
        # Verificar problemas específicos na tabela fato_adaptacaotreinamento
        if ('fato_adaptacaotreinamento' in report.get('tables', {}) and 
            report['tables']['fato_adaptacaotreinamento'].get('exists', False)):
            
            table = report['tables']['fato_adaptacaotreinamento']
            
            # Verificar se a coluna usuario_id existe
            usuario_id_exists = any(col.get('column_name') == 'usuario_id' for col in table.get('columns', []))
            if not usuario_id_exists:
                print("\n===== PROBLEMA DETECTADO: Coluna 'usuario_id' faltando =====")
                print("Execute este comando SQL para adicionar a coluna:")
                print("ALTER TABLE fato_adaptacaotreinamento ADD COLUMN usuario_id UUID;")
            
            # Verificar se a coluna treinamento_id existe
            treinamento_id_exists = any(col.get('column_name') == 'treinamento_id' for col in table.get('columns', []))
            if not treinamento_id_exists:
                print("\n===== PROBLEMA DETECTADO: Coluna 'treinamento_id' faltando =====")
                print("Execute este comando SQL para adicionar a coluna:")
                print("ALTER TABLE fato_adaptacaotreinamento ADD COLUMN treinamento_id UUID;")
                
    except Exception as e:
        print(f"\nErro durante a verificação: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())