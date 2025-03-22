#!/usr/bin/env python3
# Script de Migração de Dados para Supabase #

import sys
import os
import json
import time
import traceback
import argparse
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Adicionar o diretório pai ao path para permitir importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar utilitários e wrappers
from utils.config import get_supabase_config
from utils.logger import WrapperLogger
from utils.path_resolver import find_file, load_file_with_fallback
from wrappers.supabase_client import SupabaseWrapper
from wrappers.distribuidor_treinos import DistribuidorBD

# Inicializar logger
logger = WrapperLogger("DataMigration")

class DataMigrator:
    """
    Classe para migração de dados do modo de simulação para o Supabase.
    """
    
    def __init__(self, config: Optional[Dict[str, str]] = None, dados_dir: Optional[str] = None):
        """
        Inicializa o migrador de dados.
        
        Args:
            config (Dict, optional): Configuração personalizada do Supabase
            dados_dir (str, optional): Diretório contendo os arquivos de dados
        """
        logger.info("Inicializando DataMigrator")
        
        # Configuração
        self.config = config or get_supabase_config()
        
        # Diretório de dados
        self.dados_dir = dados_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data"
        )
        logger.info(f"Usando diretório de dados: {self.dados_dir}")
        
        # Criar diretório de dados se não existir
        if not os.path.exists(self.dados_dir):
            logger.info(f"Criando diretório de dados: {self.dados_dir}")
            os.makedirs(self.dados_dir)
        
        # Inicializar distribuidor em modo real
        try:
            logger.info("Inicializando DistribuidorBD...")
            self.distribuidor = DistribuidorBD(modo_simulacao=False)
            
            # Verificar se conexão foi estabelecida
            if not self.distribuidor.supabase_client:
                logger.error("Falha ao inicializar cliente Supabase no DistribuidorBD")
                raise ValueError("DistribuidorBD não conseguiu estabelecer conexão com Supabase")
                
            logger.info("DistribuidorBD inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar DistribuidorBD: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def listar_arquivos_planos(self) -> List[str]:
        """
        Lista todos os arquivos de planos no diretório de dados.
        
        Returns:
            List[str]: Lista de caminhos para arquivos de planos
        """
        logger.info(f"Listando arquivos de planos em: {self.dados_dir}")
        
        # Padrões de arquivos de planos
        padroes = [
            "**/plano_*.json",
            "**/treinamento_*.json",
            "**/adaptado_*.json"
        ]
        
        arquivos = []
        for padrao in padroes:
            caminho_padrao = os.path.join(self.dados_dir, padrao)
            arquivos_padrao = glob.glob(caminho_padrao, recursive=True)
            arquivos.extend(arquivos_padrao)
        
        logger.info(f"Encontrados {len(arquivos)} arquivos de planos")
        return sorted(arquivos)
    
    def carregar_plano(self, arquivo_path: str) -> Dict[str, Any]:
        """
        Carrega um plano de treinamento de um arquivo JSON.
        
        Args:
            arquivo_path (str): Caminho para o arquivo
            
        Returns:
            Dict: Dados do plano ou dicionário vazio em caso de erro
        """
        logger.info(f"Carregando plano: {arquivo_path}")
        
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                logger.info(f"Plano carregado com sucesso: {len(json.dumps(dados))} caracteres")
                return dados
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {arquivo_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Erro ao carregar plano: {str(e)}")
            return {}
    
    def migrar_plano(self, plano: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migra um plano para o banco de dados usando o DistribuidorBD.
        
        Args:
            plano (Dict): Dados do plano a ser migrado
            
        Returns:
            Dict: Resultado da migração
        """
        treinamento_id = plano.get("treinamento_id", "")
        logger.info(f"Migrando plano ID: {treinamento_id}")
        
        try:
            # Processar plano usando o DistribuidorBD
            resultado = self.distribuidor.processar_plano(plano)
            
            logger.info(f"Plano migrado com sucesso: {resultado.get('status', 'unknown')}")
            return resultado
        except Exception as e:
            logger.error(f"Erro ao migrar plano: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "mensagem": str(e),
                "treinamento_id": treinamento_id
            }
    
    def migrar_todos_planos(self) -> Dict[str, Any]:
        """
        Migra todos os planos encontrados no diretório de dados.
        
        Returns:
            Dict: Resumo dos resultados da migração
        """
        logger.info("Iniciando migração de todos os planos")
        
        arquivos = self.listar_arquivos_planos()
        
        if not arquivos:
            logger.warning("Nenhum arquivo de plano encontrado para migração")
            return {
                "status": "warning",
                "mensagem": "Nenhum arquivo de plano encontrado",
                "planos_processados": 0,
                "sucesso": 0,
                "falha": 0
            }
        
        # Resultados
        resultados = {
            "planos_processados": 0,
            "sucesso": 0,
            "falha": 0,
            "tempo_total": 0,
            "detalhes": []
        }
        
        tempo_inicio = time.time()
        
        for arquivo in arquivos:
            logger.info(f"Processando arquivo: {os.path.basename(arquivo)}")
            
            # Carregar plano
            plano = self.carregar_plano(arquivo)
            
            if not plano:
                logger.warning(f"Falha ao carregar plano: {arquivo}")
                resultados["falha"] += 1
                resultados["detalhes"].append({
                    "arquivo": arquivo,
                    "status": "error",
                    "mensagem": "Falha ao carregar plano"
                })
                continue
            
            # Migrar plano
            tempo_inicio_plano = time.time()
            resultado_migracao = self.migrar_plano(plano)
            tempo_plano = time.time() - tempo_inicio_plano
            
            resultados["planos_processados"] += 1
            
            # Registrar resultado
            if resultado_migracao.get("status") in ["success", "simulated", "partial_success"]:
                resultados["sucesso"] += 1
            else:
                resultados["falha"] += 1
            
            resultados["detalhes"].append({
                "arquivo": arquivo,
                "treinamento_id": plano.get("treinamento_id", ""),
                "status": resultado_migracao.get("status", "unknown"),
                "tempo": tempo_plano,
                "comandos_executados": resultado_migracao.get("comandos_executados", 0),
                "comandos_falha": resultado_migracao.get("comandos_falha", 0)
            })
        
        # Calcular tempo total
        resultados["tempo_total"] = time.time() - tempo_inicio
        
        # Definir status geral
        if resultados["falha"] == 0 and resultados["sucesso"] > 0:
            resultados["status"] = "success"
            resultados["mensagem"] = f"Todos os {resultados['sucesso']} planos foram migrados com sucesso"
        elif resultados["sucesso"] > 0:
            resultados["status"] = "partial_success"
            resultados["mensagem"] = f"{resultados['sucesso']} planos migrados com sucesso, {resultados['falha']} falhas"
        else:
            resultados["status"] = "error"
            resultados["mensagem"] = f"Falha ao migrar todos os {resultados['falha']} planos"
        
        logger.info(f"Migração concluída: {resultados['status']}")
        logger.info(f"Planos processados: {resultados['planos_processados']}")
        logger.info(f"Sucesso: {resultados['sucesso']}")
        logger.info(f"Falha: {resultados['falha']}")
        logger.info(f"Tempo total: {resultados['tempo_total']:.2f} segundos")
        
        return resultados
    
    def salvar_plano_simulado(self, plano: Dict[str, Any]) -> str:
        """
        Salva um plano simulado no diretório de dados.
        
        Args:
            plano (Dict): Dados do plano a ser salvo
            
        Returns:
            str: Caminho do arquivo salvo
        """
        treinamento_id = plano.get("treinamento_id", "")
        if not treinamento_id:
            # Gerar ID aleatório se não existir
            import uuid
            treinamento_id = str(uuid.uuid4())
            plano["treinamento_id"] = treinamento_id
        
        # Criar diretório para o ID se não existir
        diretorio_plano = os.path.join(self.dados_dir, treinamento_id)
        if not os.path.exists(diretorio_plano):
            os.makedirs(diretorio_plano)
        
        # Gerar nome de arquivo
        timestamp = plano.get("timestamp", time.strftime("%Y%m%d%H%M%S"))
        tipo = "adaptado" if "adaptacoes" in plano else "plano"
        arquivo_nome = f"{tipo}_{treinamento_id}_{timestamp}.json"
        arquivo_path = os.path.join(diretorio_plano, arquivo_nome)
        
        logger.info(f"Salvando plano em: {arquivo_path}")
        
        try:
            with open(arquivo_path, 'w', encoding='utf-8') as f:
                json.dump(plano, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Plano salvo com sucesso: {arquivo_path}")
            return arquivo_path
        except Exception as e:
            logger.error(f"Erro ao salvar plano: {str(e)}")
            return ""

def main():
    """Função principal para execução do script."""
    parser = argparse.ArgumentParser(description='Migração de dados para Supabase')
    parser.add_argument('--dir', help='Diretório contendo os arquivos de dados', default=None)
    parser.add_argument('--file', help='Migrar apenas um arquivo específico')
    args = parser.parse_args()
    
    logger.info("Iniciando script de migração de dados")
    
    try:
        # Inicializar migrador
        migrador = DataMigrator(dados_dir=args.dir)
        
        if args.file:
            # Migrar apenas um arquivo
            logger.info(f"Migrando arquivo específico: {args.file}")
            
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
            else:
                print("\n--- Migração Falhou ---")
                print(f"Status: {resultado.get('status', 'unknown')}")
                print(f"Mensagem: {resultado.get('mensagem', 'Erro desconhecido')}")
            
        else:
            # Migrar todos os planos
            print("\nIniciando migração de todos os planos...")
            resultado = migrador.migrar_todos_planos()
            
            print("\n--- Resumo da Migração ---")
            print(f"Status: {resultado.get('status', 'unknown')}")
            print(f"Planos processados: {resultado.get('planos_processados', 0)}")
            print(f"Sucesso: {resultado.get('sucesso', 0)}")
            print(f"Falha: {resultado.get('falha', 0)}")
            print(f"Tempo total: {resultado.get('tempo_total', 0):.2f} segundos")
            
            if resultado.get("detalhes"):
                # Listar detalhes de falhas
                falhas = [d for d in resultado.get("detalhes", []) if d.get("status") not in ["success", "simulated", "partial_success"]]
                
                if falhas:
                    print("\nDetalhes das falhas:")
                    for falha in falhas:
                        print(f"  - Arquivo: {os.path.basename(falha.get('arquivo', ''))}")
                        print(f"    Status: {falha.get('status', 'unknown')}")
                        print(f"    ID: {falha.get('treinamento_id', '')}")
                        print()
    
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"\nErro: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())