# Recursos de Desenvolvimento

Este diretório contém arquivos e recursos utilizados durante o desenvolvimento do projeto FORCA_V1, mas que não são essenciais para a execução do código principal em produção.

## Estrutura de Diretórios

### `/api_examples`
Contém exemplos de saídas JSON geradas pelas APIs e wrappers do sistema, úteis para testes e desenvolvimento:
- `plano_principal_output.json` - Exemplo de saída do wrapper do Treinador Especialista
- `plano_adaptado_output.json` - Exemplo de saída do Sistema de Adaptação
- `resultado_pipeline.json` - Exemplo de resultado completo do pipeline de processamento

### `/database_utils`
Utilitários relacionados ao banco de dados e migração de dados:
- `data_migration.py` - Script para migração de dados entre ambientes
- `db_manager.py` - Utilitário para gerenciamento de banco de dados
- `supabase_init.py` - Script de inicialização e configuração do Supabase

### `/tests`
Testes automatizados e scripts de teste:
- `test_distribuidor_bd.py` - Testes para o módulo de distribuição e armazenamento

### `/schemas`
Esquemas JSON utilizados para validação de dados nos vários componentes do sistema:
- `schema_wrapper1.json` - Esquema para validação da saída do Treinador Especialista
- `schema_wrapper2.json` - Esquema para validação da saída do Sistema de Adaptação
- `schema_wrapper3.json` - Esquema para validação da saída do Distribuidor de Treinos

### `/prompts`
Prompts e templates utilizados pelos wrappers para comunicação com o Claude:
- Templates de prompts para cada componente do sistema

### `/docs`
Documentação adicional e notas do projeto.

## Considerações para Desenvolvimento

Estes recursos são mantidos fora do código principal para facilitar a manutenção e reduzir a complexidade do código de produção, mas são essenciais para o desenvolvimento contínuo do projeto.

Para incluir novos recursos de desenvolvimento:

1. Adicione-os ao diretório apropriado dentro de `/dev_resources`
2. Atualize este README.md com informações sobre os novos recursos
3. Se necessário, atualize referências nos arquivos principais

Note que este diretório é ignorado pelo Git (.gitignore) para evitar poluir o repositório com arquivos de teste e desenvolvimento.