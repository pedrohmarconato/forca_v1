import React from 'react';
import { Link } from 'react-router-dom';

const Register = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900">
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-2xl font-bold text-white mb-6 text-center">Cadastro</h1>
        
        <form className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-300">Usuário</label>
            <input
              id="username"
              type="text"
              className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white"
              placeholder="Seu nome de usuário"
            />
          </div>
          
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-300">Email</label>
            <input
              id="email"
              type="email"
              className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white"
              placeholder="seu@email.com"
            />
          </div>
          
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-300">Senha</label>
            <input
              id="password"
              type="password"
              className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white"
              placeholder="••••••••"
            />
          </div>
          
          <div>
            <label htmlFor="passwordConfirm" className="block text-sm font-medium text-gray-300">Confirmar Senha</label>
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
              Cadastrar
            </button>
          </div>
        </form>
        
        <div className="mt-4 text-center">
          <Link to="/login" className="text-sm text-yellow-400 hover:text-yellow-300">
            Já tem uma conta? Faça login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Register;