/**
 * Utilitário para verificar a conexão com o Supabase
 */
import { supabase } from './supabase';

/**
 * Verifica se a conexão com o Supabase está configurada e funcionando
 * @returns {Promise<{success: boolean, message: string, details: Object}>}
 */
export const verifySupabaseConnection = async () => {
  console.log('Verificando conexão com o Supabase...');
  
  try {
    // Verificar se as variáveis de ambiente estão definidas
    const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
    const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;
    
    if (!supabaseUrl || !supabaseAnonKey) {
      return {
        success: false,
        message: 'Configuração do Supabase incompleta. URL ou Anon Key não definidos',
        details: {
          hasUrl: !!supabaseUrl,
          hasAnonKey: !!supabaseAnonKey
        }
      };
    }
    
    // Tentar fazer uma consulta simples para verificar a conexão
    const { data, error, status } = await supabase.from('user_profiles').select('id').limit(1);
    
    if (error) {
      return {
        success: false,
        message: `Erro ao conectar com o Supabase: ${error.message}`,
        details: {
          error,
          status
        }
      };
    }
    
    // Conexão bem-sucedida
    return {
      success: true,
      message: 'Conexão com o Supabase estabelecida com sucesso',
      details: {
        status,
        data
      }
    };
    
  } catch (error) {
    return {
      success: false,
      message: `Erro ao verificar conexão: ${error.message}`,
      details: { error }
    };
  }
};

/**
 * Verifica se as tabelas necessárias existem no Supabase
 * @returns {Promise<{success: boolean, message: string, details: Object}>}
 */
export const verifyRequiredTables = async () => {
  console.log('Verificando tabelas no Supabase...');
  
  const requiredTables = [
    'user_profiles',
    'sleep_data',
    'training_sessions',
    'training_adaptations',
    'training_plans',
    'user_stats'
  ];
  
  try {
    const results = {};
    let allTablesExist = true;
    
    // Verificar cada tabela
    for (const table of requiredTables) {
      try {
        const { data, error } = await supabase.from(table).select('*').limit(1);
        
        if (error) {
          results[table] = { exists: false, error: error.message };
          allTablesExist = false;
        } else {
          results[table] = { exists: true };
        }
      } catch (err) {
        results[table] = { exists: false, error: err.message };
        allTablesExist = false;
      }
    }
    
    return {
      success: allTablesExist,
      message: allTablesExist
        ? 'Todas as tabelas necessárias existem no Supabase'
        : 'Algumas tabelas necessárias não foram encontradas',
      details: {
        tables: results
      }
    };
    
  } catch (error) {
    return {
      success: false,
      message: `Erro ao verificar tabelas: ${error.message}`,
      details: { error }
    };
  }
};

/**
 * Verifica se o usuário tem um perfil criado
 * @param {string} userId - ID do usuário
 * @returns {Promise<{success: boolean, message: string, details: Object}>}
 */
export const verifyUserProfile = async (userId) => {
  if (!userId) {
    return {
      success: false,
      message: 'ID do usuário não fornecido',
      details: {}
    };
  }
  
  try {
    const { data, error } = await supabase
      .from('user_profiles')
      .select('*')
      .eq('id', userId)
      .single();
    
    if (error) {
      return {
        success: false,
        message: `Perfil de usuário não encontrado: ${error.message}`,
        details: { error }
      };
    }
    
    return {
      success: true,
      message: 'Perfil de usuário encontrado',
      details: { profile: data }
    };
    
  } catch (error) {
    return {
      success: false,
      message: `Erro ao verificar perfil: ${error.message}`,
      details: { error }
    };
  }
};

/**
 * Executa todas as verificações
 * @returns {Promise<{success: boolean, message: string, details: Object}>}
 */
export const runAllChecks = async () => {
  console.log('Executando todas as verificações do Supabase...');
  
  // Verificar conexão
  const connectionCheck = await verifySupabaseConnection();
  if (!connectionCheck.success) {
    return {
      success: false,
      message: 'Falha na verificação de conexão com o Supabase',
      details: {
        connection: connectionCheck
      }
    };
  }
  
  // Verificar tabelas
  const tablesCheck = await verifyRequiredTables();
  
  // Verificar usuário atual (se houver)
  let userCheck = { success: false, message: 'Nenhum usuário autenticado' };
  const { data: { user } } = await supabase.auth.getUser();
  
  if (user) {
    userCheck = await verifyUserProfile(user.id);
  }
  
  // Resultado final
  const allSuccessful = connectionCheck.success && tablesCheck.success;
  
  return {
    success: allSuccessful,
    message: allSuccessful
      ? 'Todas as verificações concluídas com sucesso'
      : 'Algumas verificações falharam',
    details: {
      connection: connectionCheck,
      tables: tablesCheck,
      user: userCheck
    }
  };
};

// Exportar função de diagnóstico para uso em componentes
export default {
  verifySupabaseConnection,
  verifyRequiredTables,
  verifyUserProfile,
  runAllChecks
};