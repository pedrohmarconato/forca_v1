# Ferramentas de Banco de Dados para FORCA_V1

Este diretório contém as ferramentas para configuração, inicialização e migração de dados para o banco de dados Supabase utilizado pelo sistema FORCA_V1.

## Arquivos

- `db_manager.py` - Script principal de gerenciamento do banco de dados (CLI)
- `supabase_init.py` - Script de inicialização das tabelas no Supabase
- `data_migration.py` - Script de migração de dados do modo simulação para o Supabase
- `Distribuidor para BD.txt` - Especificação do modelo de dados

## Requisitos

Certifique-se de que todas as dependências necessárias estão instaladas:

```bash
pip install -r ../../requirements.txt
```

É necessário também configurar as variáveis de ambiente no arquivo `.env` na raiz do projeto:

```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_API_KEY=sua-api-key
SUPABASE_SERVICE_KEY=sua-service-role-key
```

## Uso

### Gerenciador de Banco de Dados (CLI)

O script `db_manager.py` oferece uma interface de linha de comando para gerenciar o banco de dados.

```bash
# Ver ajuda
python db_manager.py --help

# Testar conexão com Supabase
python db_manager.py testconn

# Verificar estado do banco de dados
python db_manager.py check
python db_manager.py check -v  # Modo detalhado

# Inicializar banco de dados (criar tabelas)
python db_manager.py init
python db_manager.py init --force  # Forçar mesmo que as tabelas existam

# Resetar banco de dados (remover e recriar tabelas)
python db_manager.py reset
python db_manager.py reset --yes  # Pular confirmação

# Migrar dados para o banco de dados
python db_manager.py migrate
python db_manager.py migrate --file caminho/para/plano.json  # Migrar um arquivo específico
python db_manager.py migrate --dir caminho/para/diretorio  # Especificar diretório de dados
python db_manager.py migrate -v  # Mostrar detalhes da migração
```

### Inicialização de Tabelas

Para executar diretamente o script de inicialização:

```bash
# Ver ajuda
python supabase_init.py --help

# Verificar tabelas existentes
python supabase_init.py --check

# Inicializar tabelas
python supabase_init.py

# Resetar banco de dados (CUIDADO: REMOVE TODOS OS DADOS)
python supabase_init.py --reset
```

### Migração de Dados

Para executar diretamente o script de migração:

```bash
# Ver ajuda
python data_migration.py --help

# Migrar todos os planos
python data_migration.py

# Migrar um arquivo específico
python data_migration.py --file caminho/para/plano.json

# Especificar diretório de dados
python data_migration.py --dir caminho/para/diretorio
```

## Modelo de Dados

O modelo de dados está definido no arquivo `Distribuidor para BD.txt` e implementado no módulo `wrappers/distribuidor_treinos.py`. As tabelas são criadas automaticamente com base no mapeamento definido no DistribuidorBD.

## Estrutura de Tabelas

As principais tabelas do sistema são:

- `Fato_Treinamento` - Armazena informações sobre os planos de treinamento
- `Fato_CicloTreinamento` - Armazena os ciclos de cada treinamento
- `Fato_MicrocicloSemanal` - Armazena os microciclos semanais
- `Fato_SessaoTreinamento` - Armazena as sessões de treinamento
- `Fato_ExercicioSessao` - Armazena os exercícios de cada sessão
- `Fato_AdaptacaoTreinamento` - Armazena as adaptações de treinamento (humor e tempo disponível)

## Resolução de Problemas

### Problemas de Conexão

Se encontrar problemas de conexão com o Supabase:

1. Verifique se as credenciais estão corretas no arquivo `.env`
2. Execute o teste de conexão: `python db_manager.py testconn`
3. Verifique se o endpoint da API do Supabase está acessível

### Erros na Criação de Tabelas

Se encontrar erros durante a criação de tabelas:

1. Verifique se você tem permissões de administrador no projeto Supabase
2. Verifique se já existem tabelas com os mesmos nomes (use `--reset` para remover)
3. Verifique os logs de erro para identificar problemas específicos

### Erros na Migração de Dados

Se encontrar erros durante a migração de dados:

1. Verifique se as tabelas foram criadas corretamente
2. Verifique se os arquivos JSON contêm dados válidos
3. Tente migrar arquivos individualmente para identificar problemas específicos