# Projeto FORCA_V1

## Estrutura do Projeto

O projeto está organizado nas seguintes pastas:

### backend/
Contém todos os componentes do backend da aplicação:
- `api/`: API REST para comunicação com o frontend
- `wrappers/`: Módulos de integração e wrappers para processamento de dados
- `database/`: Componentes de acesso ao banco de dados
- `utils/`: Utilitários como o logger
- `json/`: Arquivos JSON para configuração dos wrappers
- `prompt/`: Templates de prompts utilizados pelos wrappers

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

## Como executar

### Backend
```bash
cd backend
# Instruções para executar o backend
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Tecnologias utilizadas

- **Backend**: Python
- **Frontend**: React
- **API**: Flask