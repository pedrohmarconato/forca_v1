# FORCA - Frontend

Este é o frontend da aplicação FORCA, um sistema de treinamento inteligente que utiliza um design com glassmorphism em fundo escuro e elementos com destaque em amarelo neon.

## Autenticação com Supabase

O sistema utiliza o Supabase para autenticação e gerenciamento de usuários. Foram implementadas as seguintes funcionalidades:

- Login (email/senha)
- Cadastro de novos usuários
- Recuperação de senha via email
- Redefinição de senha

### Configuração do Supabase

Para configurar a integração com o Supabase:

1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edite o arquivo `.env` e adicione suas credenciais do Supabase:
   ```
   REACT_APP_SUPABASE_URL=sua_url_do_supabase
   REACT_APP_SUPABASE_ANON_KEY=sua_chave_anon_do_supabase
   ```

3. Certifique-se de que o serviço de autenticação está habilitado no seu projeto Supabase e que o provedor "Email" está ativado.

4. Configure o domínio de redirecionamento para recuperação de senha no Console do Supabase em:
   - Authentication > URL Configuration > Add a new redirect URL
   - Adicione: `http://localhost:3000/reset-password`

## Componentes de Autenticação

### Login
O componente de login permite que usuários existentes façam login no sistema.

### Register
O componente de cadastro permite que novos usuários criem uma conta.

### ForgotPassword
O componente de recuperação de senha envia um email com um link para redefinir a senha.

### ResetPassword
O componente de redefinição de senha permite que o usuário defina uma nova senha após clicar no link enviado por email.

## Rotas Protegidas

Foi implementado um sistema de rotas protegidas que verifica se o usuário está autenticado antes de permitir o acesso a determinadas páginas.

```jsx
<Route 
  path="/rota-protegida" 
  element={
    <ProtectedRoute>
      <SeuComponente />
    </ProtectedRoute>
  } 
/>
```

## Contexto de Autenticação

Um contexto de autenticação (`AuthContext`) foi criado para gerenciar o estado do usuário e fornecer métodos para login, logout, etc.

Para usar o contexto em seus componentes:

```jsx
import { useAuth } from '../context/AuthContext';

const SeuComponente = () => {
  const { user, signIn, signOut } = useAuth();
  
  // Use os métodos e o estado do usuário aqui
  
  return (
    // ...
  );
};
```

## Estilo Visual

Todos os componentes seguem o estilo visual definido para o projeto:

- Fundo: Gradiente escuro (from-[#0A0A0A] to-[#1A1A1A])
- Elementos decorativos: Círculos com blur para criar profundidade
- Container principal: Efeito glassmorphism com backdrop-blur e borda semi-transparente
- Campos de entrada: Semi-transparentes com bordas leves
- Botão principal: Cor amarelo neon (#EBFF00) com texto preto
- Efeitos hover/focus em todos os elementos interativos

## Scripts Disponíveis

No diretório do projeto, você pode executar:

### `npm start`

Executa o aplicativo no modo de desenvolvimento.\
Abra [http://localhost:3000](http://localhost:3000) para visualizá-lo no navegador.

A página será recarregada quando você fizer alterações.\
Você também pode ver erros de lint no console.

### `npm test`

Inicia o executor de teste no modo de observação interativa.\
Consulte a seção sobre [execução de testes](https://facebook.github.io/create-react-app/docs/running-tests) para obter mais informações.

### `npm run build`

Cria o aplicativo para produção na pasta `build`.\
Ele empacota corretamente o React no modo de produção e otimiza a compilação para obter o melhor desempenho.

A compilação é minificada e os nomes dos arquivos incluem os hashes.\
Seu aplicativo está pronto para ser implantado!
