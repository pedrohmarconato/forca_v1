import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Contexto de Autenticação
import { AuthProvider } from './context/AuthContext.tsx';

// Componentes
import Login from './components/Login.tsx';
import Register from './components/Register.tsx';
import ForgotPassword from './components/ForgotPassword.tsx';
import ResetPassword from './components/ResetPassword.tsx';
import Questionario from './components/Questionario';
import Home from './components/home/Home.tsx';
import Settings from './components/Settings.tsx';
import ProtectedRoute from './components/ProtectedRoute.tsx';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App">
          <Routes>
            {/* Rotas públicas */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            
            {/* Rotas protegidas */}
            <Route 
              path="/home" 
              element={
                <ProtectedRoute>
                  <Home />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/questionario" 
              element={
                <ProtectedRoute>
                  <Questionario />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              } 
            />
            
            {/* Redirecionamento para home */}
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="*" element={<Navigate to="/home" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;