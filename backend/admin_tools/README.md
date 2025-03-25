# Ferramentas Administrativas FORCA_V1

Este diretório contém scripts e ferramentas administrativas para o sistema FORCA_V1. Estes scripts são utilizados para tarefas específicas de administração e não são parte do fluxo normal da aplicação.

## Estrutura

- **Banco de Dados**
  - `create_indices.sql`: Script SQL para criar tabelas, índices e relações
  - `schema_update.sql`: Script SQL para atualizações do esquema
  - `verify_schema.py`: Script Python para verificar a integridade do esquema
  - `data_migration.py`: Ferramentas para migração de dados
  - `db_manager.py`: Interface Python para operações comuns de banco de dados
  - `supabase_init.py`: Script de inicialização do Supabase (uso administrativo)
  - `README_BANCO.md`: Documentação detalhada sobre o modelo de dados

- **Desenvolvimento**
  - `dev_tools/`: Ferramentas de desenvolvimento e testes
  - `archives/`: Arquivos antigos e históricos

## Uso do Banco de Dados

**IMPORTANTE**: A aplicação principal foi configurada para NÃO tentar criar tabelas automaticamente. O administrador deve executar os scripts manualmente quando necessário.

### Criação manual do banco de dados

1. Acesse o console do Supabase (https://app.supabase.io)
2. Vá para o SQL Editor
3. Execute o conteúdo do arquivo `create_indices.sql`
4. Verifique se todas as tabelas foram criadas corretamente

### Verificação do banco de dados

```bash
# Verificar o estado atual do banco de dados
python verify_schema.py --check
```

## Notas Importantes

- NÃO execute `supabase_init.py` com a flag `--reset` em ambiente de produção sem backup prévio
- Todos os scripts devem ser executados em um ambiente controlado por um administrador
- Consulte `README_BANCO.md` para detalhes sobre a estrutura das tabelas