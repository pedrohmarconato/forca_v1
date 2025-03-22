"""
Testes para o Distribuidor BD com integração Supabase.

Este módulo testa as funcionalidades do DistribuidorBD, incluindo:
- Conexão com Supabase
- Modo de simulação
- Execução de comandos
- Comportamento de fallback
"""

import unittest
import json
import os
from unittest.mock import patch, MagicMock

# Importar módulos a serem testados
from ..wrappers.distribuidor_treinos import DistribuidorBD
from ..wrappers.supabase_client import SupabaseWrapper


class TestDistribuidorBD(unittest.TestCase):
    """Testes para o DistribuidorBD com integração Supabase."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        # Configuração de teste para Supabase
        self.config_db = {
            "url": "https://test-supabase-url.com",
            "api_key": "test-api-key",
            "timeout": 5
        }
    
    def test_inicializacao_modo_simulacao(self):
        """Testa a inicialização em modo de simulação."""
        distribuidor = DistribuidorBD(self.config_db, modo_simulacao=True)
        
        # Verificar se o modo de simulação está ativo
        self.assertTrue(distribuidor.modo_simulacao)
        self.assertIsNone(distribuidor.supabase_client)
        
        # Verificar que as estruturas básicas foram inicializadas
        self.assertIsNotNone(distribuidor.mapeamento_tabelas)
        self.assertIsNotNone(distribuidor.schema)
        self.assertIsNotNone(distribuidor.metricas)
    
    @patch('supabase.create_client')
    def test_inicializacao_modo_real(self, mock_create_client):
        """Testa a inicialização com conexão real."""
        # Configurar mock para evitar conexão real durante testes
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        # Inicializar em modo real
        with patch.object(SupabaseWrapper, '__init__', return_value=None) as mock_init:
            with patch.object(SupabaseWrapper, 'client', MagicMock()):
                distribuidor = DistribuidorBD(self.config_db, modo_simulacao=False)
                
                # Verificar que tentou inicializar a conexão
                self.assertFalse(distribuidor.modo_simulacao)
    
    @patch('supabase.create_client')
    def test_execucao_comandos_simulacao(self, mock_create_client):
        """Testa a execução de comandos em modo simulação."""
        distribuidor = DistribuidorBD(self.config_db, modo_simulacao=True)
        
        # Criar comandos de teste
        comandos = [
            {
                "tabela": "Fato_Treinamento",
                "operacao": "INSERT",
                "dados": {"nome": "Teste", "usuario_id": "123"}
            },
            {
                "tabela": "Fato_CicloTreinamento",
                "operacao": "INSERT",
                "dados": {"ciclo_id": "456", "treinamento_id": "789"}
            }
        ]
        
        # Executar comandos em modo simulação
        resultado = distribuidor._executar_comandos_db(comandos)
        
        # Verificar resultado
        self.assertEqual(resultado["status"], "simulated")
        self.assertEqual(resultado["comandos_executados"], 2)
        self.assertIn("Fato_Treinamento", resultado["estatisticas"])
        self.assertIn("Fato_CicloTreinamento", resultado["estatisticas"])
    
    @patch.object(SupabaseWrapper, 'insert_data')
    def test_execucao_comandos_real(self, mock_insert_data):
        """Testa a execução de comandos em modo real."""
        # Configurar mock para simulação de sucesso
        mock_insert_data.return_value = {"status": "success", "data": [{"id": "1"}], "count": 1}
        
        # Inicializar em modo real com conexão simulada
        with patch.object(DistribuidorBD, '_verificar_conexao', return_value=True):
            with patch.object(DistribuidorBD, '_inicializar_conexao', return_value=None):
                distribuidor = DistribuidorBD(self.config_db, modo_simulacao=False)
                distribuidor.supabase_client = MagicMock()
                distribuidor.supabase_client.insert_data = mock_insert_data
                distribuidor.conexao_db = {"status": "connected"}
                
                # Criar comandos de teste
                comandos = [
                    {
                        "tabela": "Fato_Treinamento",
                        "operacao": "INSERT",
                        "dados": {"nome": "Teste", "usuario_id": "123"}
                    }
                ]
                
                # Executar comandos
                resultado = distribuidor._executar_comandos_db(comandos)
                
                # Verificar que insert_data foi chamado
                mock_insert_data.assert_called_once()
                self.assertEqual(resultado["status"], "success")
                self.assertEqual(resultado["comandos_executados"], 1)
    
    @patch.object(SupabaseWrapper, 'insert_data')
    def test_execucao_comandos_com_retry(self, mock_insert_data):
        """Testa o mecanismo de retry para operações de BD."""
        # Configurar mock para simular uma falha seguida de sucesso
        mock_insert_data.side_effect = [
            {"status": "error", "message": "Falha temporária"},  # Primeira chamada falha
            {"status": "success", "data": [{"id": "1"}], "count": 1}  # Segunda chamada sucesso
        ]
        
        # Inicializar em modo real com conexão simulada
        with patch.object(DistribuidorBD, '_verificar_conexao', return_value=True):
            with patch.object(DistribuidorBD, '_inicializar_conexao', return_value=None):
                distribuidor = DistribuidorBD(self.config_db, modo_simulacao=False)
                distribuidor.supabase_client = MagicMock()
                distribuidor.supabase_client.insert_data = mock_insert_data
                distribuidor.conexao_db = {"status": "connected"}
                
                # Criar comandos de teste
                comandos = [
                    {
                        "tabela": "Fato_Treinamento",
                        "operacao": "INSERT",
                        "dados": {"nome": "Teste", "usuario_id": "123"}
                    }
                ]
                
                # Executar comandos com retry - usamos sleep_mock para evitar atrasos nos testes
                with patch('time.sleep', return_value=None):  # Bypass sleep
                    resultado = distribuidor._executar_comandos_db(comandos)
                
                # Verificar que insert_data foi chamado duas vezes (retry após falha)
                self.assertEqual(mock_insert_data.call_count, 2)
                self.assertEqual(resultado["status"], "success")
                self.assertEqual(resultado["comandos_executados"], 1)
    
    def test_fallback_para_simulacao(self):
        """Testa o fallback automático para simulação quando a conexão falha."""
        # Forçar falha na inicialização da conexão
        with patch.object(DistribuidorBD, '_inicializar_conexao', side_effect=ValueError("Falha forçada")):
            distribuidor = DistribuidorBD(self.config_db, modo_simulacao=False)
            
            # Verificar que entrou em modo de simulação como fallback
            self.assertIsNone(distribuidor.supabase_client)
            
            # Criar comandos de teste
            comandos = [
                {
                    "tabela": "Fato_Treinamento",
                    "operacao": "INSERT",
                    "dados": {"nome": "Teste", "usuario_id": "123"}
                }
            ]
            
            # Executar comandos - deve usar simulação
            resultado = distribuidor._executar_comandos_db(comandos)
            
            # Verificar resultado
            self.assertEqual(resultado["status"], "simulated")
            self.assertIn("comandos", resultado)


if __name__ == '__main__':
    unittest.main()