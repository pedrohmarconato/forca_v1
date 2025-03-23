#!/usr/bin/env python3
# DB Manager - Ferramenta CLI para gerenciamento do banco de dados Supabase #

import sys
import os
import argparse
import traceback
from typing import Dict, Any, List, Optional, Tuple

# Adicionar o diretório pai ao path para permitir importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar utilitários e módulos
from utils.logger import WrapperLogger
from utils.config import get_supabase_config
from database.supabase_init import SupabaseInitializer
from database.data_migration import DataMigrator

# Inicializar logger
logger = WrapperLogger("DBManager")

def inicializar_db(args):
    """
    Comando para inicializar o banco de dados.
    
    Args:
        args: Argumentos de linha de comando
    """
    print("\n=== Inicialização do Banco de Dados ===\n")
    
    try:
        # Criar inicializador
        inicializador = SupabaseInitializer()
        
        # Verificar tabelas existentes
        verificacao = inicializador.verificar_tabelas()
        
        if verificacao.get("status") != "success":
            print(f"Erro ao verificar tabelas: {verificacao.get('mensagem', 'Erro desconhecido')}")
            return 1
        
        # Verificar se todas as tabelas já existem
        if verificacao.get("completo") and not args.force:
            print("Todas as tabelas necessárias já existem.")
            print("Use --force para recriar tabelas faltantes.")
            return 0
        
        # Inicializar banco de dados
        print("Inicializando banco de dados...")
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
                    
        return 0 if sucesso else 1
    
    except Exception as e:
        print(f"\nErro: {str(e)}")
        logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        logger.error(traceback.format_exc())
        return 1

def resetar_db(args):
    """
    Comando para resetar o banco de dados.
    
    Args:
        args: Argumentos de linha de comando
    """
    print("\n=== Reset do Banco de Dados ===\n")
    print("ATENÇÃO: Esta operação irá REMOVER TODAS as tabelas e dados existentes.")
    
    if not args.yes:
        confirmacao = input("Digite 'sim' para confirmar: ")
        
        if confirmacao.lower() != "sim":
            print("Operação cancelada pelo usuário.")
            return 0
    
    try:
        # Criar inicializador
        inicializador = SupabaseInitializer()
        
        # Resetar banco de dados
        print("Resetando banco de dados...")
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
                    
        return 0 if sucesso else 1
    
    except Exception as e:
        print(f"\nErro: {str(e)}")
        logger.error(f"Erro ao resetar banco de dados: {str(e)}")
        logger.error(traceback.format_exc())
        return 1

def verificar_db(args):
    """
    Comando para verificar o estado do banco de dados.
    
    Args:
        args: Argumentos de linha de comando
    """
    print("\n=== Verificação do Banco de Dados ===\n")
    
    try:
        # Criar inicializador
        inicializador = SupabaseInitializer()
        
        # Verificar tabelas existentes
        print("Verificando tabelas...")
        verificacao = inicializador.verificar_tabelas()
        
        if verificacao.get("status") == "success":
            print("\n--- Verificação Concluída ---")
            print(f"Tabelas existentes: {len(verificacao.get('tabelas_existentes', []))}")
            print(f"Tabelas necessárias: {len(verificacao.get('tabelas_necessarias', []))}")
            print(f"Tabelas faltantes: {len(verificacao.get('tabelas_faltantes', []))}")
            
            if verificacao.get("completo"):
                print("\nStatus: COMPLETO - Todas as tabelas necessárias existem")
            else:
                print("\nStatus: INCOMPLETO - Faltam tabelas")
                
                if verificacao.get("tabelas_faltantes"):
                    print("\nTabelas faltantes:")
                    for tabela in verificacao.get("tabelas_faltantes", []):
                        print(f"  - {tabela}")
                        
            if args.verbose and verificacao.get("tabelas_existentes"):
                print("\nTabelas existentes:")
                for tabela in verificacao.get("tabelas_existentes", []):
                    print(f"  - {tabela}")
                    
            return 0
        else:
            print("\n--- Erro na Verificação ---")
            print(f"Mensagem: {verificacao.get('mensagem', 'Erro desconhecido')}")
            return 1
    
    except Exception as e:
        print(f"\nErro: {str(e)}")
        logger.error(f"Erro ao verificar banco de dados: {str(e)}")
        logger.error(traceback.format_exc())
        return 1

def migrar_dados(args):
    """
    Comando para migrar dados para o banco de dados.
    
    Args:
        args: Argumentos de linha de comando
    """
    print("\n=== Migração de Dados ===\n")
    
    try:
        # Criar migrador
        migrador = DataMigrator(dados_dir=args.dir)
        
        if args.file:
            # Migrar apenas um arquivo
            print(f"Migrando arquivo: {args.file}")
            
            # Verificar se o arquivo existe
            if not os.path.exists(args.file):
                print(f"Erro: Arquivo não encontrado: {args.file}")
                return 1
            
            # Carregar e migrar o plano
            plano = migrador.carregar_plano(args.file)
            
            if not plano:
                print(f"Erro: Falha ao carregar plano do arquivo: {args.file}")
                return 1
            
            print(f"\nMigrando plano ID: {plano.get('treinamento_id', '')}")
            resultado = migrador.migrar_plano(plano)
            
            if resultado.get("status") in ["success", "simulated", "partial_success"]:
                print("\n--- Migração Concluída com Sucesso ---")
                if resultado.get("status") == "simulated":
                    print("Modo: Simulação (sem conexão real)")
                print(f"Comandos executados: {resultado.get('comandos_executados', 0)}")
                
                if resultado.get("estatisticas"):
                    print("\nEstatísticas por tabela:")
                    for tabela, contagem in resultado.get("estatisticas", {}).items():
                        print(f"  - {tabela}: {contagem}")
                        
                return 0
            else:
                print("\n--- Migração Falhou ---")
                print(f"Status: {resultado.get('status', 'unknown')}")
                print(f"Mensagem: {resultado.get('mensagem', 'Erro desconhecido')}")
                return 1
        
        else:
            # Migrar todos os planos
            print("Iniciando migração de todos os planos...")
            resultado = migrador.migrar_todos_planos()
            
            print("\n--- Resumo da Migração ---")
            print(f"Status: {resultado.get('status', 'unknown')}")
            print(f"Planos processados: {resultado.get('planos_processados', 0)}")
            print(f"Sucesso: {resultado.get('sucesso', 0)}")
            print(f"Falha: {resultado.get('falha', 0)}")
            print(f"Tempo total: {resultado.get('tempo_total', 0):.2f} segundos")
            
            if resultado.get("detalhes") and args.verbose:
                # Listar detalhes
                print("\nDetalhes por arquivo:")
                for detalhe in resultado.get("detalhes", []):
                    print(f"  - Arquivo: {os.path.basename(detalhe.get('arquivo', ''))}")
                    print(f"    Status: {detalhe.get('status', 'unknown')}")
                    print(f"    ID: {detalhe.get('treinamento_id', '')}")
                    print(f"    Tempo: {detalhe.get('tempo', 0):.2f} segundos")
                    print()
            
            # Listar detalhes de falhas mesmo sem verbose
            falhas = [d for d in resultado.get("detalhes", []) if d.get("status") not in ["success", "simulated", "partial_success"]]
            
            if falhas:
                print("\nDetalhes das falhas:")
                for falha in falhas:
                    print(f"  - Arquivo: {os.path.basename(falha.get('arquivo', ''))}")
                    print(f"    Status: {falha.get('status', 'unknown')}")
                    print(f"    ID: {falha.get('treinamento_id', '')}")
                    print()
            
            return 0 if resultado.get("status") in ["success", "partial_success"] else 1
    
    except Exception as e:
        print(f"\nErro: {str(e)}")
        logger.error(f"Erro ao migrar dados: {str(e)}")
        logger.error(traceback.format_exc())
        return 1

def testar_conexao(args):
    """
    Comando para testar a conexão com o banco de dados.
    
    Args:
        args: Argumentos de linha de comando
    """
    print("\n=== Teste de Conexão com Supabase ===\n")
    
    from wrappers.supabase_client import SupabaseWrapper
    
    try:
        # Obter configuração
        config = get_supabase_config()
        
        # Verificar configuração
        if not config.get('url') or not config.get('api_key'):
            print("Erro: URL ou API key da Supabase não configurados.")
            print("Verifique o arquivo .env ou as variáveis de ambiente.")
            return 1
        
        print(f"URL: {config.get('url')}")
        print(f"API Key: {'*' * len(config.get('api_key'))}")
        
        # Tentar conexão
        print("\nConectando à Supabase...")
        cliente = SupabaseWrapper(
            url=config.get('url'),
            api_key=config.get('api_key')
        )
        
        # Testar uma consulta simples
        print("Executando consulta de teste...")
        resultado = cliente.execute_rpc("exec_sql", {"command": "SELECT current_timestamp as now;"})
        
        if resultado.get("status") == "success":
            print("\n--- Conexão Estabelecida com Sucesso ---")
            data = resultado.get("data", [])
            if data and "now" in data[0]:
                print(f"Timestamp do servidor: {data[0]['now']}")
            return 0
        else:
            print("\n--- Falha na Consulta de Teste ---")
            print(f"Mensagem: {resultado.get('message', 'Erro desconhecido')}")
            return 1
    
    except Exception as e:
        print(f"\n--- Erro na Conexão ---")
        print(f"Erro: {str(e)}")
        logger.error(f"Erro ao testar conexão: {str(e)}")
        logger.error(traceback.format_exc())
        return 1

def inicializar_sistema(args):
    """
    Comando para inicializar todo o sistema FORCA.
    
    Args:
        args: Argumentos de linha de comando
    """
    print("\n=== Inicialização do Sistema FORCA ===\n")
    
    try:
        # Importar função de inicialização do sistema
        from integration_script import initialize_system
        
        print("Iniciando inicialização do sistema completo...")
        
        # Inicializar sistema
        resultado = initialize_system(init_db=True, force_reset=args.reset)
        
        # Exibir resumo do resultado
        status = resultado["status"]
        componentes = len(resultado["componentes"])
        erros = len(resultado["erros"])
        
        print(f"\nStatus da inicialização: {status.upper()}")
        print(f"Componentes inicializados: {componentes}")
        
        # Exibir detalhes de cada componente
        print("\nDetalhes por componente:")
        for nome, info in resultado["componentes"].items():
            status_comp = info.get("status", "unknown")
            status_icon = "✅" if status_comp == "success" else "❌"
            print(f"{status_icon} {nome}: {info.get('message', status_comp)}")
            
            # Exibir detalhes adicionais para banco de dados
            if nome == "banco_dados" and status_comp == "success" and "detalhes" in info:
                detalhes = info["detalhes"]
                print(f"   - Tabelas criadas: {detalhes.get('tabelas_criadas', 0)}")
                print(f"   - Índices criados: {detalhes.get('indices_criados', 0)}")
                print(f"   - Funções criadas: {detalhes.get('funcoes_criadas', 0)}")
                print(f"   - Triggers criados: {detalhes.get('triggers_criados', 0)}")
        
        # Exibir erros se houver
        if erros > 0:
            print(f"\nErros encontrados ({erros}):")
            for i, erro in enumerate(resultado["erros"][:3], 1):
                print(f"  {i}. {erro[:200]}...")
            if erros > 3:
                print(f"  ... e mais {erros - 3} erro(s)")
        
        # Retornar código de saída apropriado
        return 0 if status == "success" else 1
    
    except ImportError as e:
        print(f"\nErro ao importar módulo: {str(e)}")
        print("Verifique se o arquivo integration_script.py existe e está no diretório correto.")
        logger.error(f"Erro ao importar integration_script: {str(e)}")
        return 1
    except Exception as e:
        print(f"\nErro ao inicializar sistema: {str(e)}")
        logger.error(f"Erro ao inicializar sistema: {str(e)}")
        logger.error(traceback.format_exc())
        return 1

def main():
    """Função principal para execução do script."""
    parser = argparse.ArgumentParser(
        description='Gerenciador de banco de dados Supabase para o sistema FORCA_V1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  db_manager.py init                     # Inicializa o banco de dados
  db_manager.py check -v                 # Verifica o estado do banco com detalhes
  db_manager.py reset --yes              # Reseta o banco sem confirmação
  db_manager.py migrate                  # Migra todos os planos disponíveis
  db_manager.py migrate --file plano.json # Migra apenas um arquivo específico
  db_manager.py testconn                 # Testa a conexão com o Supabase
  db_manager.py init-system              # Inicializa todo o sistema FORCA (wrappers e banco)
  db_manager.py init-system --reset      # Inicializa o sistema com reset do banco
        """
    )
    
    subparsers = parser.add_subparsers(dest='comando', help='Comando a ser executado')
    
    # Comando init
    init_parser = subparsers.add_parser('init', help='Inicializa o banco de dados')
    init_parser.add_argument('--force', action='store_true', help='Força a inicialização mesmo se as tabelas já existirem')
    
    # Comando reset
    reset_parser = subparsers.add_parser('reset', help='Reseta o banco de dados (REMOVE TODOS OS DADOS)')
    reset_parser.add_argument('--yes', action='store_true', help='Prossegue sem confirmação')
    
    # Comando check
    check_parser = subparsers.add_parser('check', help='Verifica o estado do banco de dados')
    check_parser.add_argument('-v', '--verbose', action='store_true', help='Mostra informações detalhadas')
    
    # Comando migrate
    migrate_parser = subparsers.add_parser('migrate', help='Migra dados para o banco de dados')
    migrate_parser.add_argument('--dir', help='Diretório contendo os arquivos de dados')
    migrate_parser.add_argument('--file', help='Migra apenas um arquivo específico')
    migrate_parser.add_argument('-v', '--verbose', action='store_true', help='Mostra informações detalhadas')
    
    # Comando testconn
    testconn_parser = subparsers.add_parser('testconn', help='Testa a conexão com o Supabase')
    
    # Comando init-system
    init_system_parser = subparsers.add_parser('init-system', help='Inicializa todo o sistema FORCA (wrappers e banco de dados)')
    init_system_parser.add_argument('--reset', action='store_true', help='Força reset completo das tabelas do banco de dados')
    
    # Processar argumentos
    args = parser.parse_args()
    
    if args.comando == 'init':
        return inicializar_db(args)
    elif args.comando == 'reset':
        return resetar_db(args)
    elif args.comando == 'check':
        return verificar_db(args)
    elif args.comando == 'migrate':
        return migrar_dados(args)
    elif args.comando == 'testconn':
        return testar_conexao(args)
    elif args.comando == 'init-system':
        return inicializar_sistema(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())