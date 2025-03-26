import React, { createContext, useState, useEffect, useContext } from 'react';
import { supabase } from '../utils/supabase';
import { Session, User } from '@supabase/supabase-js';

// Tipo para o contexto de autenticação
interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signUp: (email: string, password: string) => Promise<{ error: any; data: any }>;
  signIn: (email: string, password: string) => Promise<{ error: any; data: any }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: any; data: any }>;
  updatePassword: (newPassword: string) => Promise<{ error: any; data: any }>;
}

// Criação do contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Buscar sessão ao iniciar
    const getSession = async () => {
      setLoading(true);
      
      try {
        const { data, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('Erro ao obter sessão:', error.message);
        } else if (data?.session) {
          setSession(data.session);
          setUser(data.session.user);
        }
      } catch (error) {
        console.error('Erro inesperado ao obter sessão:', error);
      } finally {
        setLoading(false);
      }
    };
    
    getSession();
    
    // Configurar listener para mudanças na autenticação
    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (event, newSession) => {
        console.log(`Evento de autenticação: ${event}`);
        
        // Atualizar o estado conforme o evento
        setSession(newSession);
        setUser(newSession?.user ?? null);
        setLoading(false);
      }
    );
    
    // Limpar listener ao desmontar
    return () => {
      authListener?.subscription.unsubscribe();
    };
  }, []);
  
  // Cadastro de usuário
  const signUp = async (email: string, password: string) => {
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password
      });
      
      return { data, error };
    } finally {
      setLoading(false);
    }
  };
  
  // Login de usuário
  const signIn = async (email: string, password: string) => {
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      });
      
      return { data, error };
    } finally {
      setLoading(false);
    }
  };
  
  // Logout
  const signOut = async () => {
    setLoading(true);
    try {
      await supabase.auth.signOut();
    } finally {
      setLoading(false);
    }
  };
  
  // Enviar link de recuperação de senha
  const resetPassword = async (email: string) => {
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`
      });
      
      return { data, error };
    } finally {
      setLoading(false);
    }
  };
  
  // Atualizar senha
  const updatePassword = async (newPassword: string) => {
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.updateUser({
        password: newPassword
      });
      
      return { data, error };
    } finally {
      setLoading(false);
    }
  };
  
  const value = {
    user,
    session,
    loading,
    signUp,
    signIn,
    signOut,
    resetPassword,
    updatePassword
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook personalizado para usar o contexto
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  
  return context;
};

export default AuthContext;
