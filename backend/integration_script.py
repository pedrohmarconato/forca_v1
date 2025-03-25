#!/usr/bin/env python3
# Sistema de Orquestração dos Componentes FORCA #

import os
import sys
import argparse
import json
import traceback
from typing import Dict, Any, Optional, List, Tuple

# Importar wrappers do sistema
from backend.wrappers.treinador_especialista import TreinadorEspecialista
from backend.wrappers.sistema_adaptacao_treino import SistemaAdaptacao
from backend.wrappers.distribuidor_treinos import DistribuidorBD

# Importar utilitários e configurações
from backend.utils.logger import WrapperLogger
from backend.utils.config import get_claude_config, get_supabase_config, get_db_config

# Configurar logger
logger = WrapperLogger("IntegrationSystem")

def initialize_system() -> Dict[str, Any]:
    """
    Inicializa todos os componentes do sistema FORCA.
    
    Returns:
        Dict: Resultado da inicialização dos componentes
    """
    logger.info("Iniciando inicialização do sistema FORCA")
    resultado = {
        "status": "success",
        "componentes": {},
        "erros": []
    }
    
    try:
        # Inicializar TreinadorEspecialista
        logger.info("Inicializando TreinadorEspecialista...")
        try:
            claude_config = get_claude_config()
            treinador = TreinadorEspecialista(claude_config)
            resultado["componentes"]["treinador_especialista"] = {
                "status": "success",
                "message": "TreinadorEspecialista inicializado com sucesso"
            }
            logger.info("TreinadorEspecialista inicializado com sucesso")
        except Exception as e:
            error_msg = f"Erro ao inicializar TreinadorEspecialista: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            resultado["componentes"]["treinador_especialista"] = {
                "status": "error",
                "message": error_msg
            }
            resultado["erros"].append(error_msg)
        
        # Inicializar SistemaAdaptacao
        logger.info("Inicializando SistemaAdaptacao...")
        try:
            sistema_adaptacao = SistemaAdaptacao()
            resultado["componentes"]["sistema_adaptacao"] = {
                "status": "success",
                "message": "SistemaAdaptacao inicializado com sucesso"
            }
            logger.info("SistemaAdaptacao inicializado com sucesso")
        except Exception as e:
            error_msg = f"Erro ao inicializar SistemaAdaptacao: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            resultado["componentes"]["sistema_adaptacao"] = {
                "status": "error",
                "message": error_msg
            }
            resultado["erros"].append(error_msg)
        
        # Inicializar DistribuidorBD
        logger.info("Inicializando DistribuidorBD...")
        try:
            db_config = get_db_config()
            distribuidor = DistribuidorBD(config_db=db_config, check_tables=False)
            resultado["componentes"]["distribuidor_bd"] = {
                "status": "success",
                "message": "DistribuidorBD inicializado com sucesso"
            }
            logger.info("DistribuidorBD inicializado com sucesso")
        except Exception as e:
            error_msg = f"Erro ao inicializar DistribuidorBD: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            resultado["componentes"]["distribuidor_bd"] = {
                "status": "error",
                "message": error_msg
            }
            resultado["erros"].append(error_msg)
        
        # Determinar status geral
        if resultado["erros"]:
            resultado["status"] = "partial_success" if len(resultado["erros"]) < 3 else "error"
        
        logger.info(f"Inicialização do sistema concluída com status: {resultado['status']}")
        
        return resultado
    
    except Exception as e:
        logger.error(f"Erro fatal durante inicialização do sistema: {str(e)}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "fatal_error",
            "message": f"Erro fatal durante inicialização: {str(e)}",
            "componentes": resultado.get("componentes", {}),
            "erros": resultado.get("erros", []) + [f"Erro fatal: {str(e)}"]
        }

def main():
    """Função principal para execução via linha de comando."""
    parser = argparse.ArgumentParser(description='Sistema de Integração FORCA')
    
    # Opções de inicialização
    parser.add_argument('--init', action='store_true', help='Inicializar o sistema')
    
    # Opções de saída
    parser.add_argument('--output', type=str, help='Arquivo para salvar resultado da inicialização em formato JSON')
    parser.add_argument('--verbose', action='store_true', help='Exibir informações detalhadas durante a execução')
    
    args = parser.parse_args()
    
    # Se nenhum argumento for fornecido, mostrar ajuda
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    # Configurar nível de log com base em verbose
    if args.verbose:
        logger.set_level("DEBUG")
    
    # Inicializar sistema se solicitado
    if args.init:
        print("Inicializando sistema FORCA...")
        
        # Inicializar sistema
        resultado = initialize_system()
        
        # Exibir resultado resumido
        status = resultado["status"]
        erros = len(resultado["erros"])
        print(f"\nStatus da inicialização: {status.upper()}")
        print(f"Componentes inicializados: {len(resultado['componentes'])}")
        if erros > 0:
            print(f"Erros encontrados: {erros}")
            for i, erro in enumerate(resultado["erros"][:3], 1):
                print(f"  Erro {i}: {erro[:100]}...")
            if erros > 3:
                print(f"  ... e mais {erros - 3} erro(s)")
        
        # Salvar resultado em arquivo se solicitado
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(resultado, f, indent=2, ensure_ascii=False)
                print(f"\nResultado salvo em: {args.output}")
            except Exception as e:
                print(f"\nErro ao salvar resultado: {str(e)}")
        
        return 0 if status == "success" else 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())