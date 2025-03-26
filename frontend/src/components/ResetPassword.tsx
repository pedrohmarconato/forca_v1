import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ResetPassword = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { updatePassword } = useAuth();
  
  const [formData, setFormData] = useState({
    password: '',
    passwordConfirm: ''
  });
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Verifica se chegou aqui a partir de um link de redefinição de senha
    if (!location.hash) {
      // Se não tiver hash na URL, provavelmente não veio do email de reset
      navigate('/login');
    }
  }, [location, navigate]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData({
      ...formData,
      [id]: value
    });
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    // Validar senhas
    if (formData.password !== formData.passwordConfirm) {
      setError('As senhas não coincidem.');
      return;
    }
    
    if (formData.password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres.');
      return;
    }
    
    setLoading(true);
    
    try {
      const { data, error } = await updatePassword(formData.password);
      
      if (error) {
        throw error;
      }
      
      setSuccess('Senha redefinida com sucesso!');
      
      // Redireciona após um breve período
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      
    } catch (err: any) {
      console.error('Erro ao redefinir senha:', err);
      setError(err.message || 'Erro ao redefinir a senha. Tente novamente ou solicite um novo link.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A]">
      <div className="bg-black/40 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-lg w-full max-w-md">
        <h1 className="text-2xl font-bold text-white mb-6 text-center">Redefinir Senha</h1>
        
        {error && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-500/50 rounded-lg text-white text-sm">
            {error}
          </div>
        )}
        
        {success && (
          <div className="mb-4 p-3 bg-green-900/50 border border-green-500/50 rounded-lg text-white text-sm">
            {success}
          </div>
        )}
        
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-white/70">Nova Senha</label>
            <input
              id="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className="mt-1 block w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:outline-none focus:border-[#EBFF00] focus:bg-white/10 text-white"
              placeholder="••••••••"
              required
            />
          </div>
          
          <div>
            <label htmlFor="passwordConfirm" className="block text-sm font-medium text-white/70">Confirmar Nova Senha</label>
            <input
              id="passwordConfirm"
              type="password"
              value={formData.passwordConfirm}
              onChange={handleChange}
              className="mt-1 block w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:outline-none focus:border-[#EBFF00] focus:bg-white/10 text-white"
              placeholder="••••••••"
              required
            />
          </div>
          
          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-base font-medium text-black bg-[#EBFF00] hover:bg-[#EBFF00]/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Processando...' : 'Redefinir senha'}
            </button>
          </div>
        </form>
        
        <div className="mt-4 text-center">
          <Link to="/login" className="text-[#EBFF00] hover:text-[#EBFF00]/90 text-sm">
            Voltar para o login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;