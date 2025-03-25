import React from 'react';
import { Link } from 'react-router-dom';

const ResetPassword = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900">
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-2xl font-bold text-white mb-6 text-center">Redefinir Senha</h1>
        
        <form className="space-y-6">
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-300">Nova Senha</label>
            <input
              id="password"
              type="password"
              className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white"
              placeholder="••••••••"
            />
          </div>
          
          <div>
            <label htmlFor="passwordConfirm" className="block text-sm font-medium text-gray-300">Confirmar Nova Senha</label>
            <input
              id="passwordConfirm"
              type="password"
              className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white"
              placeholder="••••••••"
            />
          </div>
          
          <div>
            <button
              type="submit"
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-black bg-yellow-400 hover:bg-yellow-500"
            >
              Redefinir senha
            </button>
          </div>
        </form>
        
        <div className="mt-4 text-center">
          <Link to="/login" className="text-sm text-yellow-400 hover:text-yellow-300">
            Voltar para o login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;