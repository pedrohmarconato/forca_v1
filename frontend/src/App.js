import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Componentes
import Login from './components/Login.tsx';
import Register from './components/Register.tsx';
import ForgotPassword from './components/ForgotPassword.tsx';
import ResetPassword from './components/ResetPassword.tsx';
import Questionario from './components/Questionario';
import Home from './components/home/Home.tsx';

// Componente de rota protegida
const ProtectedRoute = ({ children }) => {
  // Implementar verificação de autenticação
  const isAuthenticated = localStorage.getItem('sb-session') !== null;
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          {/* Rotas públicas */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          
          {/* Home */}
          <Route path="/home" element={<Home />} />
          
          {/* Rotas protegidas */}
          <Route 
            path="/questionario" 
            element={
              <ProtectedRoute>
                <Questionario />
              </ProtectedRoute>
            } 
          />
          
          {/* Redirecionamento para login */}
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
