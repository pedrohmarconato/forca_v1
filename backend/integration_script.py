# Integration Script #

import json
import os
from wrapper1 import TreinadorEspecialista 
from wrapper2 import SistemaAdaptacao
from wrapper3 import DistribuidorBD

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
    # Initialize all wrappers
    treinador = TreinadorEspecialista(api_key)
    adaptador = SistemaAdaptacao()
    distribuidor = DistribuidorBD(db_config)
    
    try:
        # Step 1: Generate training plan using Wrapper 1 (Treinador Especialista)
        print("Step 1: Generating main training plan...")
        plano_principal = treinador.criar_plano_treinamento(user_data)
        
        # Optional: Save main plan to file for debugging
        with open("plano_principal_output.json", "w", encoding="utf-8") as f:
            json.dump(plano_principal, f, indent=2, ensure_ascii=False)
        
        # Step 2: Create adaptations using Wrapper 2 (Sistema de Adaptação)
        print("Step 2: Creating training adaptations...")
        plano_adaptado = adaptador.processar_plano(plano_principal)
        
        # Optional: Save adapted plan to file for debugging
        with open("plano_adaptado_output.json", "w", encoding="utf-8") as f:
            json.dump(plano_adaptado, f, indent=2, ensure_ascii=False)
        
        # Step 3: Distribute to database using Wrapper 3 (Distribuidor BD)
        print("Step 3: Mapping data to database tables...")
        
        # Connect to database if configuration is provided
        if db_config:
            distribuidor.conectar_bd(db_config)
        
        # Process the adapted plan
        resultado = distribuidor.processar_plano(plano_adaptado)
        
        # Disconnect from database if connected
        if db_config:
            distribuidor.desconectar_bd()
        
        print("Pipeline completed successfully!")
        return {
            "status": "success",
            "steps_completed": 3,
            "resultado_db": resultado
        }
    
    except Exception as e:
        print(f"Error in pipeline: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# Example usage
if __name__ == "__main__":
    # Claude API key (get from environment variable for security)
    api_key = os.environ.get("CLAUDE_API_KEY", "your_api_key_here")
    
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
    
    # Example database configuration
    db_config = {
        "host": "localhost",
        "porta": 5432,
        "usuario": "app_user",
        "senha": "app_password",
        "database": "training_app_db"
    }
    
    # Run the pipeline
    result = run_training_pipeline(api_key, user_data, db_config)
    print(json.dumps(result, indent=2))