import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * Componente ProtectedRoute
 * Verifica se o usuário está autenticado antes de renderizar os componentes filhos
 * Redireciona para a página de login se não estiver autenticado
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();
  
  // Exibir um indicador de carregamento enquanto verifica a autenticação
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A]">
        <div className="p-4 rounded-xl bg-black/40 backdrop-blur-xl border border-white/10 shadow-lg">
          <div className="flex flex-col items-center">
            <div className="w-8 h-8 border-2 border-[#EBFF00] border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="text-white/70">Verificando autenticação...</p>
          </div>
        </div>
      </div>
    );
  }
  
  // Se o usuário não estiver autenticado, redireciona para o login
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  // Se o usuário estiver autenticado, renderiza os componentes filhos
  return <>{children}</>;
};

export default ProtectedRoute;