# FORCA_V1 - Documentação do Backend

## Visão Geral

O backend do FORCA_V1 é responsável por:
1. Geração de planos de treinamento personalizados utilizando a API Claude
2. Adaptação de planos com base nas condições do usuário
3. Armazenamento e gerenciamento de dados no Supabase
4. Disponibilização de APIs para o frontend

## Arquitetura

O backend segue uma arquitetura modular com os seguintes componentes principais:

### 1. Wrappers

Os wrappers são responsáveis pela comunicação com APIs externas e processamento de dados:

- **Treinador Especialista (treinador_especialista.py)**: Gera planos de treinamento iniciais utilizando a API Claude
- **Sistema de Adaptação (sistema_adaptacao_treino.py)**: Adapta planos existentes com base no humor e tempo disponível
- **Distribuidor BD (distribuidor_treinos.py)**: Armazena e recupera dados do Supabase
- **Claude Client (claude_client.py)**: Wrapper para API Claude
- **Supabase Client (supabase_client.py)**: Wrapper para API Supabase

### 2. Utilitários

- **Logger (logger.py)**: Sistema centralizado de logging com decorators
- **Config (config.py)**: Gerenciamento de configurações e variáveis de ambiente
- **Path Resolver (path_resolver.py)**: Utilitário para resolução dinâmica de caminhos de arquivos

### 3. API

- **App Flask (app.py)**: Endpoints REST para integração com o frontend

### 4. Banco de Dados

- **Scripts de Inicialização**: Ferramentas para configurar e migrar dados para o Supabase
- **Modelo de Dados**: Definição das tabelas e relacionamentos no Supabase

## Ferramentas de Banco de Dados

### DB Manager (db_manager.py)

Interface de linha de comando para gerenciar o banco de dados Supabase:

```bash
# Testar conexão com Supabase
python backend/database/db_manager.py testconn

# Verificar estado do banco de dados
python backend/database/db_manager.py check

# Inicializar banco de dados (criar tabelas)
python backend/database/db_manager.py init

# Resetar banco de dados (remover e recriar tabelas)
python backend/database/db_manager.py reset

# Migrar dados para o banco de dados
python backend/database/db_manager.py migrate
```

### Inicialização de Tabelas (supabase_init.py)

Script para criação das tabelas no Supabase baseadas no mapeamento do DistribuidorBD.

### Migração de Dados (data_migration.py)

Script para migração de dados do modo simulação para o Supabase.

## Fluxo de Dados

1. **Entrada de Dados**: Informações do usuário e requisitos de treinamento
2. **Geração do Plano**: Treinador Especialista gera um plano detalhado
3. **Adaptação**: Sistema de Adaptação modifica o plano conforme necessário
4. **Persistência**: Distribuidor BD armazena os dados no Supabase
5. **Disponibilização**: API disponibiliza os dados para o frontend

## Integração com Supabase

O sistema utiliza o Supabase como banco de dados e armazenamento. As principais tabelas são:

- `Fato_Treinamento`: Planos de treinamento completos
- `Fato_CicloTreinamento`: Ciclos de treinamento
- `Fato_MicrocicloSemanal`: Microciclos semanais
- `Fato_SessaoTreinamento`: Sessões individuais
- `Fato_ExercicioSessao`: Exercícios específicos
- `Fato_AdaptacaoTreinamento`: Adaptações de humor e tempo disponível

## Integração com Claude

O sistema utiliza a API Claude para geração de conteúdo:

- **Geração de Planos**: Utiliza prompts otimizados para criar planos personalizados
- **Adaptação de Sessões**: Modifica sessões existentes com base em novos parâmetros
- **Análise de Feedback**: Processa feedback do usuário para melhorar futuros planos

## Modo de Simulação

Todos os componentes podem operar em modo de simulação, permitindo desenvolvimento e testes sem dependências externas:

- **Simulação de BD**: Permite operar sem conexão real com o Supabase
- **Simulação de IA**: Utiliza respostas pré-definidas ao invés de chamar a API Claude

## Arquivos de Configuração

- **.env**: Variáveis de ambiente (API keys, URLs, etc.)
- **schemas/*.json**: Schemas para validação de dados
- **json/*.txt**: Templates JSON para os wrappers
- **prompt/*.txt**: Templates de prompts para a API Claude

## Testes

Os testes unitários e de integração estão na pasta `tests/`:

```bash
# Executar todos os testes
python -m pytest backend/tests/

# Executar teste específico
python -m pytest backend/tests/test_distribuidor_bd.py
```

## Prompt do Treinador Especialista

```
Você é um treinador de elite especializado em musculação e desempenho físico, com décadas de experiência treinando os maiores atletas do fisiculturismo mundial e de diversos outros esportes. 
Sua abordagem científica e personalizada levou centenas de clientes a atingirem seu máximo potencial físico.

Sua Expertise

Avaliação e Planejamento

- Utilize o 1RM (Uma Repetição Máxima)(em % de 1RM) como base fundamental para prescrição de cargas
- Desenvolva planos de treinamento com visão de longo prazo, estabelecendo metas trimestrais (ciclos de 12 semanas)
- Analise profundamente o histórico de lesões do usuário para adaptar exercícios e prevenir recidivas
- Considere fatores entregues como input como pilares da lógica de treinamento

Métodos de Treinamento

    Treinamento tradicional (séries e repetições)
    Treinamento de alta intensidade (HIIT)
    Treinamento em circuito
    Treinamento pliométrico
    Treinamento de força máxima
    Treinamento de potência
    Treinamento de hipertrofia
    Treinamento de resistência muscular
    Treinamento isométrico
    Treinamento excêntrico acentuado
    Treinamento até a falha muscular
    Métodos de intensificação (drop-sets, rest-pause, giant sets, supersets)
    Métodos de recuperação ativa

Periodizações

    Periodização linear (clássica)
    Periodização ondulatória diária
    Periodização ondulatória semanal
    Periodização em blocos
    Periodização conjugada (método Westside)
    Periodização por acumulação/intensificação
    Periodização reversa
    Periodização não-linear
    Periodização por indicadores de desempenho
    Microciclos, mesociclos e macrociclos estruturados

Exercícios

    Exercícios compostos multiarticulares (agachamentos, levantamentos terra, supinos, etc.)
    Exercícios de isolamento para grupos musculares específicos
    Exercícios com peso corporal e calistenia avançada
    Exercícios com implementos especializados (kettlebells, clubes, medicine balls)
    Exercícios de estabilização e core
    Exercícios com bandas elásticas e correntes
    Exercícios de mobilidade e amplitude de movimento
    Exercícios pliométricos e balísticos
    Exercícios corretivos e preventivos
    Variações específicas para cada grupo muscular (pelo menos 10 variações para cada)
    Progressões de exercícios para diferentes níveis de habilidade
```