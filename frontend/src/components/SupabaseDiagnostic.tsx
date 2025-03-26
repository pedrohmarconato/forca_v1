import React, { useState, useEffect } from 'react';
import { runAllChecks } from '../utils/verify-supabase';
import { useAuth } from '../context/AuthContext';

interface CheckResult {
  success: boolean;
  message: string;
  details: any;
}

interface DiagnosticResults {
  success: boolean;
  message: string;
  details: {
    connection: CheckResult;
    tables: CheckResult;
    user: CheckResult;
  };
}

const SupabaseDiagnostic: React.FC = () => {
  const { user } = useAuth();
  const [results, setResults] = useState<DiagnosticResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const runDiagnostics = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const checkResults = await runAllChecks();
        setResults(checkResults as DiagnosticResults);
      } catch (err: any) {
        setError(err.message || 'Erro desconhecido ao executar diagnóstico');
        console.error('Erro no diagnóstico:', err);
      } finally {
        setLoading(false);
      }
    };
    
    runDiagnostics();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl">
        <div className="w-8 h-8 border-2 border-[#EBFF00] border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="text-white">Verificando conexão com Supabase...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-900/50 border border-red-500/50 rounded-xl text-white">
        <h2 className="text-xl font-bold mb-2">Erro no diagnóstico</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl text-white">
      <h2 className="text-xl font-bold mb-4">Diagnóstico do Supabase</h2>
      
      <div className="space-y-4">
        {/* Status geral */}
        <div className={`p-4 rounded-lg ${results?.success ? 'bg-green-900/30 border border-green-500/50' : 'bg-red-900/30 border border-red-500/50'}`}>
          <div className="flex items-center">
            <div className={`w-4 h-4 rounded-full mr-2 ${results?.success ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="font-medium">{results?.message}</span>
          </div>
        </div>
        
        {/* Verificação de conexão */}
        <div className="border border-white/10 rounded-lg">
          <div className={`flex items-center justify-between p-3 ${results?.details.connection.success ? 'border-b border-green-500/30' : 'border-b border-red-500/30'}`}>
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-2 ${results?.details.connection.success ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="font-medium">Conexão com Supabase</span>
            </div>
            <span className={results?.details.connection.success ? 'text-green-400' : 'text-red-400'}>
              {results?.details.connection.success ? 'OK' : 'Falha'}
            </span>
          </div>
          <div className="p-3 text-sm text-white/70">
            {results?.details.connection.message}
          </div>
        </div>
        
        {/* Verificação de tabelas */}
        <div className="border border-white/10 rounded-lg">
          <div className={`flex items-center justify-between p-3 ${results?.details.tables.success ? 'border-b border-green-500/30' : 'border-b border-red-500/30'}`}>
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-2 ${results?.details.tables.success ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="font-medium">Tabelas requeridas</span>
            </div>
            <span className={results?.details.tables.success ? 'text-green-400' : 'text-red-400'}>
              {results?.details.tables.success ? 'OK' : 'Falha'}
            </span>
          </div>
          <div className="p-3 text-sm">
            <p className="mb-2 text-white/70">{results?.details.tables.message}</p>
            {results?.details.tables.details?.tables && (
              <div className="mt-2 grid grid-cols-2 gap-2">
                {Object.entries(results.details.tables.details.tables).map(([table, status]: [string, any]) => (
                  <div 
                    key={table}
                    className={`p-2 rounded text-xs ${status.exists ? 'bg-green-900/30' : 'bg-red-900/30'}`}
                  >
                    <div className="flex items-center">
                      <div className={`w-2 h-2 rounded-full mr-1 ${status.exists ? 'bg-green-500' : 'bg-red-500'}`}></div>
                      <span>{table}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Verificação de usuário */}
        <div className="border border-white/10 rounded-lg">
          <div className={`flex items-center justify-between p-3 ${user ? 'border-b border-green-500/30' : 'border-b border-yellow-500/30'}`}>
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-2 ${user ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
              <span className="font-medium">Usuário atual</span>
            </div>
            <span className={user ? 'text-green-400' : 'text-yellow-400'}>
              {user ? 'Autenticado' : 'Não autenticado'}
            </span>
          </div>
          <div className="p-3 text-sm text-white/70">
            {user ? (
              <div>
                <p>Email: {user.email}</p>
                <p>ID: {user.id.substring(0, 8)}...</p>
                <p className="mt-1">
                  Status do perfil: {' '}
                  <span className={results?.details.user.success ? 'text-green-400' : 'text-red-400'}>
                    {results?.details.user.success ? 'Perfil encontrado' : 'Perfil não encontrado'}
                  </span>
                </p>
              </div>
            ) : (
              <p>Nenhum usuário autenticado. Faça login para verificar o perfil.</p>
            )}
          </div>
        </div>
      </div>
      
      <div className="mt-6 text-center text-sm text-white/60">
        <p>
          Para solucionar problemas, consulte o arquivo SUPABASE_SETUP.md
        </p>
      </div>
    </div>
  );
};

export default SupabaseDiagnostic;