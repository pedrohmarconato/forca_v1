# Integration Script with Logs #

import json
import os
import time
import traceback
from wrapper1 import TreinadorEspecialista 
from wrapper2 import SistemaAdaptacao
from wrapper3 import DistribuidorBD
from logger import WrapperLogger

def run_training_pipeline(api_key, user_data, db_config=None):
    """
    Execute the complete training pipeline using all three wrappers.
    
    Args:
        api_key (str): Claude API key
        user_data (dict): User data for generating the training plan
        db_config (dict, optional): Database configuration
        
    Returns:
        dict: Result of the pipeline execution
    """
    # Configure logger
    logger = WrapperLogger("IntegrationScript")
    logger.info("="*50)
    logger.info("INICIANDO PIPELINE DE TREINAMENTO")
    logger.info("="*50)
    
    inicio_pipeline = time.time()
    
    # Initialize all wrappers
    logger.info("Inicializando wrappers")
    try:
        treinador = TreinadorEspecialista(api_key)
        logger.info("Wrapper 1 (Treinador Especialista) inicializado com sucesso")
        
        adaptador = SistemaAdaptacao()
        logger.info("Wrapper 2 (Sistema de Adaptação) inicializado com sucesso")
        
        distribuidor = DistribuidorBD(db_config)
        logger.info("Wrapper 3 (Distribuidor BD) inicializado com sucesso")
    except Exception as e:
        logger.critical(f"Erro ao inicializar wrappers: {str(e)}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"Erro ao inicializar wrappers: {str(e)}"
        }
    
    try:
        # Step 1: Generate training plan using Wrapper 1 (Treinador Especialista)
        logger.info("-"*50)
        logger.info("ETAPA 1: Gerando plano de treinamento principal")
        inicio_etapa1 = time.time()
        
        plano_principal = treinador.criar_plano_treinamento(user_data)
        
        tempo_etapa1 = time.time() - inicio_etapa1
        logger.info(f"Plano principal gerado com sucesso em {tempo_etapa1:.2f} segundos")
        
        # Optional: Save main plan to file for debugging
        try:
            with open("plano_principal_output.json", "w", encoding="utf-8") as f:
                json.dump(plano_principal, f, indent=2, ensure_ascii=False)
                logger.info("Plano principal salvo em arquivo: plano_principal_output.json")
        except Exception as e:
            logger.warning(f"Não foi possível salvar o plano principal em arquivo: {str(e)}")
        
        # Step 2: Create adaptations using Wrapper 2 (Sistema de Adaptação)
        logger.info("-"*50)
        logger.info("ETAPA 2: Criando adaptações do treinamento")
        inicio_etapa2 = time.time()
        
        plano_adaptado = adaptador.processar_plano(plano_principal)
        
        tempo_etapa2 = time.time() - inicio_etapa2
        logger.info(f"Adaptações criadas com sucesso em {tempo_etapa2:.2f} segundos")
        
        # Optional: Save adapted plan to file for debugging
        try:
            with open("plano_adaptado_output.json", "w", encoding="utf-8") as f:
                json.dump(plano_adaptado, f, indent=2, ensure_ascii=False)
                logger.info("Plano adaptado salvo em arquivo: plano_adaptado_output.json")
        except Exception as e:
            logger.warning(f"Não foi possível salvar o plano adaptado em arquivo: {str(e)}")
        
        # Step 3: Distribute to database using Wrapper 3 (Distribuidor BD)
        logger.info("-"*50)
        logger.info("ETAPA 3: Mapeando dados para o banco de dados")
        inicio_etapa3 = time.time()
        
        # Connect to database if configuration is provided
        if db_config:
            logger.info("Configuração de banco de dados fornecida, conectando ao BD")
            try:
                distribuidor.conectar_bd(db_config)
                logger.info("Conexão estabelecida com o banco de dados")
            except Exception as e:
                logger.error(f"Erro ao conectar com o banco de dados: {str(e)}")
                logger.warning("Continuando sem conexão com o banco (modo simulação)")
        else:
            logger.info("Nenhuma configuração de BD fornecida, prosseguindo em modo de simulação")
        
        # Process the adapted plan
        resultado = distribuidor.processar_plano(plano_adaptado)
        
        # Disconnect from database if connected
        if db_config and distribuidor.conexao_db:
            logger.info("Desconectando do banco de dados")
            distribuidor.desconectar_bd()
            logger.info("Desconectado do banco de dados com sucesso")
        
        tempo_etapa3 = time.time() - inicio_etapa3
        logger.info(f"Dados mapeados para o banco de dados em {tempo_etapa3:.2f} segundos")
        
        tempo_total = time.time() - inicio_pipeline
        logger.info("="*50)
        logger.info(f"PIPELINE CONCLUÍDO COM SUCESSO em {tempo_total:.2f} segundos")
        logger.info(f"Etapa 1 (Plano Principal): {tempo_etapa1:.2f}s ({(tempo_etapa1/tempo_total)*100:.1f}%)")
        logger.info(f"Etapa 2 (Adaptações): {tempo_etapa2:.2f}s ({(tempo_etapa2/tempo_total)*100:.1f}%)")
        logger.info(f"Etapa 3 (Banco de Dados): {tempo_etapa3:.2f}s ({(tempo_etapa3/tempo_total)*100:.1f}%)")
        logger.info("="*50)
        
        return {
            "status": "success",
            "steps_completed": 3,
            "resultado_db": resultado,
            "tempo_execucao": {
                "total": tempo_total,
                "etapa1": tempo_etapa1,
                "etapa2": tempo_etapa2,
                "etapa3": tempo_etapa3
            }
        }
    
    except Exception as e:
        logger.critical(f"Erro no pipeline: {str(e)}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

# Example usage
if __name__ == "__main__":
    logger = WrapperLogger("Main")
    logger.info("Iniciando script de integração")
    
    # Claude API key (get from environment variable for security)
    api_key = os.environ.get("CLAUDE_API_KEY", "your_api_key_here")
    if api_key == "your_api_key_here":
        logger.warning("Nenhuma API_KEY encontrada, usando valor padrão (não funcionará)")
    
    logger.info("Preparando dados do usuário para exemplo")
    # Example user data
    user_data = {
        "id": "user123",
        "nome": "João Silva",
        "idade": 30,
        "data_nascimento": "1993-05-15",
        "peso": 75,
        "altura": 175,
        "genero": "masculino",
        "nivel": "intermediário",
        "historico_treino": "3 anos de musculação",
        "tempo_treino": 60,  # tempo disponível por sessão em minutos
        "objetivos": [
            {"nome": "Hipertrofia", "prioridade": 1},
            {"nome": "Força", "prioridade": 2}
        ],
        "restricoes": [
            {"nome": "Dor no joelho", "gravidade": "moderada"}
        ],
        "lesoes": [
            {"regiao": "joelho", "gravidade": "moderada", "observacoes": "Menisco"}
        ],
        "disponibilidade_semanal": 4,
        "dias_disponiveis": ["segunda", "terça", "quinta", "sexta"],
        "cardio": "sim",
        "alongamento": "sim",
        "conversa_chat": "Gostaria de focar mais em membros superiores"
    }
    
    logger.info("Preparando configuração do banco de dados para exemplo")
    # Example database configuration
    db_config = {
        "host": "localhost",
        "porta": 5432,
        "usuario": "app_user",
        "senha": "app_password",
        "database": "training_app_db"
    }
    
    logger.info("Executando pipeline de treinamento")
    # Run the pipeline
    try:
        result = run_training_pipeline(api_key, user_data, db_config)
        logger.info(f"Resultado do pipeline: {result['status']}")
        
        # Save result to file
        try:
            with open("resultado_pipeline.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                logger.info("Resultado salvo em arquivo: resultado_pipeline.json")
        except Exception as e:
            logger.warning(f"Não foi possível salvar o resultado em arquivo: {str(e)}")
            
    except Exception as e:
        logger.critical(f"Erro ao executar pipeline: {str(e)}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
    
    logger.info("Script de integração concluído")