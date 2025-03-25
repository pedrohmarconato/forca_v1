# FORCA_V1 - Sistema de Geração e Adaptação de Treinos

Sistema de geração e adaptação de planos de treinamento utilizando inteligência artificial.

## Componentes Principais

### Backend

- **API RESTful**: Interface para interação com o frontend
- **Wrappers**:
  - **Treinador Especialista**: Gera planos de treinamento personalizados
  - **Sistema de Adaptação**: Adapta treinos baseado em condições variáveis
  - **Distribuidor BD**: Gerencia a persistência e distribuição dos dados

### Frontend

- **Interface React**: Componentes para interação do usuário
- **Sistema de Auth**: Autenticação e gerenciamento de usuários
- **Visualização de Treinos**: Apresentação dos planos de treino

## Configuração

### Requisitos

- Python 3.8+
- Node.js 14+
- Conta Supabase (para armazenamento de dados)
- Conta Anthropic Claude (para geração de planos)

### Instalação

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Configuração do .env

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
# API Claude
CLAUDE_API_KEY=sua-api-key-claude
CLAUDE_MODEL=claude-3-opus-20240229

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_API_KEY=sua-api-key
SUPABASE_SERVICE_KEY=sua-service-role-key

# Configurações do App
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Execução

```bash
# Backend
cd backend/api
python app.py

# Frontend
cd frontend
npm start
```

## Administração do Banco de Dados

Scripts administrativos para o banco de dados estão localizados em `backend/admin_tools/`. Estes scripts são utilizados para tarefas específicas de administração e não são parte do fluxo normal da aplicação.

A aplicação foi configurada para não tentar criar tabelas automaticamente. O administrador do sistema deve executar os scripts manualmente quando necessário.

## Estrutura do Projeto

```
FORCA_V1/
├── backend/
│   ├── api/             # API principal
│   ├── admin_tools/     # Scripts administrativos (BD)
│   ├── json/            # Configurações JSON para wrappers
│   ├── prompt/          # Prompts para IA
│   ├── schemas/         # Schemas essenciais
│   ├── utils/           # Utilitários (logger, config)
│   ├── wrappers/        # Componentes principais
│   ├── __init__.py
├── frontend/
│   ├── public/          # Arquivos estáticos
│   ├── src/             # Código React
│   ├── package.json
├── .env.example
├── README.md
```

## Funcionalidades

- Geração de planos de treinamento personalizados
- Adaptação de sessões com base no humor e tempo disponível
- Armazenamento e recuperação de planos via Supabase
- Análise de progresso e métricas de treinamento

## Tecnologias utilizadas

- **Backend**: Python, Claude API (Anthropic), Supabase
- **Frontend**: React, Tailwind CSS
- **API**: Flask
- **Banco de Dados**: PostgreSQL (via Supabase)