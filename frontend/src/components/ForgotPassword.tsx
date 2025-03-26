import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowRight } from 'lucide-react';

const ForgotPassword = () => {
  const { resetPassword } = useAuth();
  
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setLoading(true);
    
    try {
      const { data, error } = await resetPassword(email);
      
      if (error) {
        throw error;
      }
      
      setMessage('Instruções para redefinir sua senha foram enviadas para seu email.');
    } catch (err: any) {
      setError(err.message || 'Falha ao enviar email de redefinição. Tente novamente.');
      console.error('Erro ao solicitar redefinição de senha:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] relative">
      {/* Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-white/20 rounded-full blur-[100px] -translate-x-1/2 -translate-y-1/2" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-[#EBFF00]/10 rounded-full blur-[100px] translate-x-1/2 translate-y-1/2" />
      </div>

      <div className="w-full max-w-md p-8 rounded-2xl shadow-xl relative overflow-hidden backdrop-blur-sm">
        {/* Gradient Background */}
        <div className="absolute inset-0 bg-black/40 backdrop-blur-xl border border-white/10" />
        
        {/* Content Container */}
        <div className="relative z-10">
          {/* Logo and Header */}
          <div className="text-center mb-8">
            <div className="flex flex-col items-center">
              <img 
                src="/logo.png" 
                alt="Logo do App" 
                className="w-48 h-auto mb-0"
              />
              <p className="text-white text-sm font-medium italic -mt-2 drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]">Treinamento inteligente</p>
            </div>
            <p className="text-white/80 mt-4 drop-shadow-[0_0_8px_rgba(255,255,255,0.5)]">Recupere sua senha</p>
          </div>

          {/* Success Message */}
          {message && (
            <div className="mb-6 p-3 bg-green-900/50 border border-green-500/50 rounded-lg text-white text-sm">
              {message}
            </div>
          )}
          
          {/* Error Message */}
          {error && (
            <div className="mb-6 p-3 bg-red-900/50 border border-red-500/50 rounded-lg text-white text-sm">
              {error}
            </div>
          )}
        
          {/* Reset Password Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Endereço de e-mail"
                className="w-full px-4 py-3 rounded-xl bg-white/5 text-white placeholder-white/40 border border-white/10 focus:outline-none focus:border-white/30 focus:bg-white/10 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-all backdrop-blur-sm"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#EBFF00] text-black font-semibold py-3 rounded-xl flex items-center justify-center space-x-2 hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{loading ? 'Enviando...' : 'Enviar Instruções'}</span>
              {!loading && <ArrowRight className="w-5 h-5" />}
            </button>
          </form>

          {/* Back to Login Link */}
          <div className="mt-8 text-center">
            <p className="text-white/60">
              Lembrou sua senha?{' '}
              <Link to="/login" className="text-white font-semibold hover:text-[#EBFF00] transition-colors drop-shadow-[0_0_8px_rgba(255,255,255,0.5)]">
                Voltar para login
              </Link>
            </p>
          </div>

          {/* Fabricado no Brasil text */}
          <div className="mt-8 text-center">
            <p className="text-white/40 text-xs">Fabricado no Brasil</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;