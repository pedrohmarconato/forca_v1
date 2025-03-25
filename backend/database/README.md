# Banco de Dados FORCA_V1

Este diretório contém os scripts e arquivos relacionados ao banco de dados do sistema FORCA_V1.

## Estrutura do Banco de Dados

O banco de dados segue um modelo de *star schema* (esquema estrela) com:

- **Tabelas de Dimensão** (`dim_*`): Armazenam entidades fundamentais e suas características
- **Tabelas de Fato** (`fato_*`): Armazenam eventos, transações e medições do sistema

### Organização Principal das Tabelas

1. **Dimensões de Usuário e Configuração**
   - `dim_usuario`: Cadastro de usuários
   - `dim_objetivo`: Objetivos de treinamento
   - `dim_restricao`: Restrições físicas e limitações

2. **Dimensões de Exercícios e Grupos Musculares**
   - `dim_grupomuscular`: Grupos musculares do corpo
   - `dim_exercicio`: Catálogo de exercícios

3. **Dimensões de Metodologia**
   - `dim_modeloperiodizacao`: Modelos de periodização
   - `dim_metodotreinamento`: Métodos de treinamento
   - `dim_tiposessao`: Tipos de sessão de treino
   - `dim_variaveltreinamento`: Variáveis manipuláveis do treinamento

4. **Dimensões de Adaptação**
   - `dim_humor`: Estados de humor para adaptação
   - `dim_tempodisponivel`: Categorias de tempo disponível

5. **Fatos de Planejamento de Treinamento**
   - `fato_treinamento`: Planos de treinamento
   - `fato_ciclotreinamento`: Ciclos dentro de um treinamento
   - `fato_microciclosemanal`: Semanas de treino
   - `fato_sessaotreinamento`: Sessões de treino
   - `fato_sessaogrupomusuclar`: Grupos musculares por sessão
   - `fato_exerciciossessao`: Exercícios por sessão

6. **Fatos de Adaptação e Personalização**
   - `fato_adaptacaotreinamento`: Adaptações de treinamento
   - `fato_usuarioobjetivo`: Objetivos por usuário
   - `fato_usuariorestricao`: Restrições por usuário

7. **Fatos de Registro e Progressão**
   - `fato_progressaoexercicio`: Progressão nos exercícios
   - `fato_substituicaoexercicio`: Substituições de exercícios
   - `fato_registrotreino`: Registro de treinos realizados
   - `fato_registroexercicio`: Detalhes dos exercícios realizados
   - `fato_metricaprogresso`: Métricas de progresso do usuário

## Scripts de Banco de Dados

- **`create_indices.sql`**: Script principal para criar todas as tabelas, índices e chaves estrangeiras
- **`schema_update.sql`**: Script para atualizar e corrigir o esquema de tabelas existentes
- **`supabase_init.py`**: Script Python para inicialização programática do banco de dados
- **`db_manager.py`**: Gerenciador de banco de dados para operações comuns
- **`data_migration.py`**: Script para migração de dados (quando necessário)

## Resolução de Problemas Comuns

### Erro: Coluna não encontrada

Se receber um erro como "column X does not exist":

1. Verifique se a tabela existe no banco de dados:
   ```sql
   SELECT * FROM information_schema.tables WHERE table_name = 'nome_da_tabela';
   ```

2. Verifique a estrutura atual da tabela:
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'nome_da_tabela'
   ORDER BY ordinal_position;
   ```

3. Adicione a coluna faltante:
   ```sql
   ALTER TABLE nome_da_tabela ADD COLUMN nome_coluna TIPO_DADOS;
   ```

### Erro: Constraint de Chave Estrangeira

Se ocorrer um erro ao adicionar chaves estrangeiras:

1. Verifique se a tabela e a coluna de referência existem:
   ```sql
   SELECT * FROM tabela_referenciada WHERE coluna_referenciada = 'algum_valor';
   ```

2. Adicione a constraint em uma etapa separada:
   ```sql
   ALTER TABLE tabela 
   ADD CONSTRAINT nome_constraint 
   FOREIGN KEY (coluna) REFERENCES tabela_referenciada(coluna_referenciada);
   ```

3. Se o erro persistir, tente usar o console de administração do Supabase para adicionar a constraint.

### Erro: Índices Duplicados

Se receber um erro sobre índices duplicados:

1. Remova o índice existente antes de criar um novo:
   ```sql
   DROP INDEX IF EXISTS nome_do_indice;
   ```

2. Crie o novo índice:
   ```sql
   CREATE INDEX nome_do_indice ON tabela (coluna);
   ```

## Instruções para Atualização do Esquema

Para atualizar ou corrigir o esquema do banco de dados:

1. Execute o script de verificação e atualização:
   ```sql
   -- No editor SQL do Supabase
   \i '/backend/database/schema_update.sql'
   ```

2. Verifique os logs para identificar problemas específicos

3. Resolva problemas individualmente se necessário, usando os comandos SQL apropriados

4. Para modificações mais complexas, considere usar o script `supabase_init.py` com a opção `--reset`

## Notas sobre o Supabase

O Supabase pode ter limitações ao executar certos comandos SQL via Editor SQL:

1. Executar scripts PL/pgSQL complexos (DO $$...$$) pode não mostrar todas as mensagens
2. Adicionar constraints de chave estrangeira pode falhar no Editor SQL, exigindo uso do console ou API
3. Recomenda-se dividir scripts grandes em partes menores quando executados via Editor SQL

## Backup e Restauração

Para backup e restauração completa do banco de dados:

1. Use as ferramentas de backup do Supabase no painel de controle
2. Para restauração parcial ou migração de dados, use o script `data_migration.py`

## Modelo de Dados Completo

Para visualizar o modelo de dados completo, consulte `Distribuidor para BD.txt`