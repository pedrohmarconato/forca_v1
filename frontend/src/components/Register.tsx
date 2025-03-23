import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();
  const { signUp } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // Validar o formulário
    if (password !== confirmPassword) {
      setError('As senhas não coincidem');
      return;
    }
    
    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres');
      return;
    }

    setLoading(true);

    try {
      const { data, error } = await signUp(email, password, username);
      
      if (error) {
        throw new Error(error.message || 'Erro ao criar conta');
      }
      
      setSuccess(true);
      
      // Supabase já envia email de confirmação por padrão
      // Esperamos 3 segundos antes de redirecionar para a página de login
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-[#0A0A0A] to-[#1A1A1A] p-4 relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute top-[10%] left-[5%] w-64 h-64 rounded-full bg-[#EBFF00]/5 blur-[100px]" />
      <div className="absolute bottom-[10%] right-[5%] w-96 h-96 rounded-full bg-[#EBFF00]/5 blur-[100px]" />
      <div className="absolute top-[40%] right-[20%] w-48 h-48 rounded-full bg-white/5 blur-[80px]" />

      <div className="flex flex-1 items-center justify-center z-10">
        <div className="w-full max-w-md bg-black/40 backdrop-blur-sm border border-white/10 rounded-2xl p-8 shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
          {/* Logo and title */}
          <div className="flex flex-col items-center mb-8">
            <h1 className="text-[#EBFF00] text-3xl font-bold mb-1">FORCA</h1>
            <p className="text-white/70 italic text-sm">Crie sua conta</p>
          </div>

          {/* Success message */}
          {success && (
            <div className="mb-4 p-3 bg-green-500/20 border border-green-500/50 rounded-lg text-white text-sm">
              Conta criada com sucesso! Enviamos um email de confirmação. Redirecionando...
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-white text-sm">
              {error}
            </div>
          )}

          {/* Register form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="username" className="block text-white/80 text-sm font-medium">
                Nome de usuário
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={loading || success}
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl 
                text-white placeholder:text-white/40
                focus:outline-none focus:border-white/40 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)]
                hover:border-white/40 transition-all
                disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="Seu nome de usuário"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="block text-white/80 text-sm font-medium">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading || success}
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl 
                text-white placeholder:text-white/40
                focus:outline-none focus:border-white/40 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)]
                hover:border-white/40 transition-all
                disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="seu@email.com"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="block text-white/80 text-sm font-medium">
                Senha
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading || success}
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl 
                text-white placeholder:text-white/40
                focus:outline-none focus:border-white/40 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)]
                hover:border-white/40 transition-all
                disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="••••••••"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="block text-white/80 text-sm font-medium">
                Confirmar senha
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={loading || success}
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl 
                text-white placeholder:text-white/40
                focus:outline-none focus:border-white/40 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)]
                hover:border-white/40 transition-all
                disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading || success}
              className="w-full flex justify-center py-3 px-4 rounded-xl
              bg-[#EBFF00] text-black font-medium shadow-[0_0_15px_rgba(235,255,0,0.4)]
              hover:shadow-[0_0_20px_rgba(235,255,0,0.6)] hover:bg-[#f0ff4c]
              focus:outline-none focus:ring-2 focus:ring-[#EBFF00] focus:ring-offset-2 focus:ring-offset-black
              transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Cadastrando...' : 'Cadastrar'}
            </button>
          </form>

          {/* Login link */}
          <div className="mt-6 text-center">
            <p className="text-white/60 text-sm">
              Já tem uma conta?{' '}
              <Link to="/login" className="text-white hover:text-[#EBFF00] transition-colors">
                Faça login
              </Link>
            </p>
          </div>

          {/* Footer */}
          <div className="mt-10 pt-4 border-t border-white/10 text-center">
            <p className="text-white/40 text-xs">Fabricado no Brasil</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;