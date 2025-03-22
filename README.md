# Projeto FORCA_V1

Sistema de geração e adaptação de planos de treinamento utilizando inteligência artificial.

## Estrutura do Projeto

O projeto está organizado nas seguintes pastas:

### backend/
Contém todos os componentes do backend da aplicação:
- `api/`: API REST para comunicação com o frontend
- `wrappers/`: Módulos de integração e wrappers para processamento de dados
- `database/`: Componentes de acesso ao banco de dados e scripts de inicialização
- `utils/`: Utilitários como logger, configuração e resolução de caminhos
- `json/`: Arquivos JSON para configuração dos wrappers
- `prompt/`: Templates de prompts utilizados pelos wrappers
- `schemas/`: Esquemas JSON para validação de dados
- `tests/`: Testes automatizados

### frontend/
Contém a aplicação React para interface do usuário:
- `src/`: Código fonte da aplicação
  - `assets/`: Imagens, ícones e outros recursos estáticos
  - `components/`: Componentes React reutilizáveis
  - `context/`: Contextos React para gerenciamento de estado
  - `hooks/`: Hooks React customizados
  - `navigation/`: Componentes de navegação
  - `screens/`: Telas/páginas da aplicação
  - `store/`: Gerenciamento de estado (Redux/Context)
  - `styles/`: Estilos globais e temas
  - `utils/`: Funções utilitárias compartilhadas

### docs/
Documentação do projeto:
- `BACKEND_README.md`: Documentação específica do backend

## Configuração Inicial

### Requisitos
- Python 3.8+
- Node.js 14+
- Conta Supabase (para armazenamento de dados)
- Conta Anthropic Claude (para geração de planos)

### Instalação de Dependências

```bash
# Instalar dependências do backend
pip install -r requirements.txt

# Instalar dependências do frontend
cd frontend
npm install
```

### Configuração do Ambiente

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

### Inicialização do Banco de Dados

Para configurar o banco de dados Supabase:

```bash
# Verificar conexão com Supabase
python backend/database/db_manager.py testconn

# Verificar estado atual do banco de dados
python backend/database/db_manager.py check

# Inicializar tabelas no banco de dados
python backend/database/db_manager.py init
```

## Como executar

### Backend
```bash
cd backend/api
python app.py
```

### Frontend
```bash
cd frontend
npm start
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