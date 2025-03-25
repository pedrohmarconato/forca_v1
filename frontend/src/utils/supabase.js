import { createClient } from '@supabase/supabase-js';

// Essas variáveis devem ser definidas no ambiente (.env) em produção
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://sua-url-do-projeto.supabase.co';
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'sua-chave-anonima';

// Cria o cliente do Supabase
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Funções de autenticação
export const signIn = async (email, password) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  return { data, error };
};

export const signUp = async (email, password, username) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        username,
      },
    },
  });
  return { data, error };
};

export const signOut = async () => {
  const { error } = await supabase.auth.signOut();
  return { error };
};

export const resetPassword = async (email) => {
  const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/reset-password`,
  });
  return { data, error };
};

export const updatePassword = async (newPassword) => {
  const { data, error } = await supabase.auth.updateUser({
    password: newPassword,
  });
  return { data, error };
};

export const getCurrentUser = async () => {
  const { data, error } = await supabase.auth.getUser();
  return { data, error };
};

export const getSession = async () => {
  const { data, error } = await supabase.auth.getSession();
  return { data, error };
};