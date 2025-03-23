import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { 
  supabase, 
  signIn, 
  signUp, 
  signOut, 
  resetPassword, 
  updatePassword, 
  getSession, 
  getCurrentUser 
} from '../utils/supabase';

interface User {
  id: string;
  email: string;
  username?: string;
}

interface AuthContextProps {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ data: any; error: any }>;
  signUp: (email: string, password: string, username: string) => Promise<{ data: any; error: any }>;
  signOut: () => Promise<{ error: any }>;
  resetPassword: (email: string) => Promise<{ data: any; error: any }>;
  updatePassword: (newPassword: string) => Promise<{ data: any; error: any }>;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar se há uma sessão ativa quando o componente é montado
    const checkUser = async () => {
      try {
        setLoading(true);
        const { data: sessionData } = await getSession();
        
        if (sessionData?.session) {
          const { data: userData } = await getCurrentUser();
          
          if (userData?.user) {
            setUser({
              id: userData.user.id,
              email: userData.user.email || '',
              username: userData.user.user_metadata?.username
            });
          }
        }
      } catch (error) {
        console.error("Erro ao verificar usuário:", error);
      } finally {
        setLoading(false);
      }
    };

    checkUser();

    // Configurar listener para mudanças no estado de autenticação
    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (session && session.user) {
          setUser({
            id: session.user.id,
            email: session.user.email || '',
            username: session.user.user_metadata?.username
          });
        } else {
          setUser(null);
        }
        setLoading(false);
      }
    );

    return () => {
      authListener?.subscription.unsubscribe();
    };
  }, []);

  const value = {
    user,
    loading,
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextProps => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};