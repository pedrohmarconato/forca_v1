/**
 * API para comunicação com o backend
 */
import { supabase } from './supabase';

// Base URL da API - ajuste conforme seu ambiente
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Função para realizar requisições à API
 * 
 * @param {string} endpoint - Endpoint da API
 * @param {Object} options - Opções da requisição
 * @returns {Promise<Object>} - Resposta da API
 */
export const apiRequest = async (endpoint, options = {}) => {
  try {
    // Obter token de autenticação atual
    const { data: sessionData } = await supabase.auth.getSession();
    
    const token = sessionData?.session?.access_token;
    
    // Configurar headers
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    // Se houver token, adiciona ao header Authorization
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Realizar requisição
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
    
    // Se resposta não for ok, lança erro
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.message || `Erro ${response.status}: ${response.statusText}`);
    }
    
    // Retornar dados JSON
    return await response.json();
  } catch (error) {
    console.error('Erro na API:', error);
    throw error;
  }
};

/**
 * Métodos específicos da API
 */

// API de perfil de usuário
export const userProfileApi = {
  // Obter perfil do usuário
  getProfile: async () => {
    const { data, error } = await supabase
      .from('user_profiles')
      .select('*')
      .single();
      
    if (error) throw error;
    return data;
  },
  
  // Atualizar perfil do usuário
  updateProfile: async (profileData) => {
    const { data, error } = await supabase
      .from('user_profiles')
      .update(profileData)
      .eq('id', (await supabase.auth.getUser()).data.user.id)
      .select();
      
    if (error) throw error;
    return data;
  },
  
  // Enviar dados do questionário
  submitQuestionnaireData: async (formData) => {
    const userId = (await supabase.auth.getUser()).data.user.id;
    
    // Preparar dados para inserção
    const profileData = {
      nome_completo: formData.nome || 'Usuário',
      data_nascimento: `${formData.dataNascimento.ano}-${formData.dataNascimento.mes}-${formData.dataNascimento.dia}`,
      genero: formData.genero || null,
      peso: parseFloat(formData.peso) || null,
      altura: parseInt(formData.altura) || null,
      nivel: formData.experienciaTreino || 'iniciante',
      historico_treino: `${formData.tempoTreino} anos de experiência`,
      objetivos: formData.objetivo ? [{ nome: formData.objetivo, prioridade: 1 }] : [],
      lesoes: formData.temLesoes ? formData.lesoes.map(lesao => ({
        regiao: lesao.toLowerCase().replace("lesão no ", "").replace("lesão nas ", ""),
        gravidade: "moderada", 
        observacoes: formData.descricaoLesao || ""
      })) : [],
      restricoes: formData.temLesoes ? [{ 
        nome: formData.lesoes.join(", "), 
        gravidade: "moderada" 
      }] : []
    };
    
    // Atualizar perfil do usuário
    const result = await supabase
      .from('user_profiles')
      .update(profileData)
      .eq('id', userId)
      .select();
    
    if (result.error) throw result.error;
    
    // Enviar dados para a API para gerar o plano de treino
    return await apiRequest('/gerar-plano', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        questionario: {
          ...formData,
          disponibilidade_semanal: formData.diasTreino.length,
          cardio: formData.preferenciaCardio ? 'sim' : 'não',
          alongamento: formData.preferenciaAlongamento ? 'sim' : 'não'
        }
      })
    });
  }
};

// API de dados de treinos
export const trainingApi = {
  // Obter planos de treino do usuário
  getTrainingPlans: async () => {
    const { data, error } = await supabase
      .from('training_plans')
      .select('*')
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    return data;
  },
  
  // Obter um plano de treino específico
  getTrainingPlan: async (planId) => {
    const { data, error } = await supabase
      .from('training_plans')
      .select('*')
      .eq('id', planId)
      .single();
    
    if (error) throw error;
    return data;
  },
  
  // Obter sessões de treino do usuário
  getTrainingSessions: async (filters = {}) => {
    let query = supabase
      .from('training_sessions')
      .select('*');
    
    // Aplicar filtros
    if (filters.startDate) {
      query = query.gte('date', filters.startDate);
    }
    if (filters.endDate) {
      query = query.lte('date', filters.endDate);
    }
    if (filters.status) {
      query = query.eq('status', filters.status);
    }
    
    // Ordenar por data (mais recente primeiro)
    query = query.order('date', { ascending: false });
    
    const { data, error } = await query;
    
    if (error) throw error;
    return data;
  },
  
  // Registrar uma sessão de treino
  recordTrainingSession: async (sessionData) => {
    const { data, error } = await supabase
      .from('training_sessions')
      .insert(sessionData)
      .select();
    
    if (error) throw error;
    return data;
  },
  
  // Obter adaptações de treino
  getTrainingAdaptations: async (originalSessionId) => {
    const { data, error } = await supabase
      .from('training_adaptations')
      .select('*')
      .eq('original_session_id', originalSessionId);
    
    if (error) throw error;
    return data;
  }
};

// API de dados de saúde
export const healthApi = {
  // Obter dados de sono do usuário
  getSleepData: async (startDate, endDate) => {
    const { data, error } = await supabase
      .from('sleep_data')
      .select('*')
      .gte('date', startDate)
      .lte('date', endDate)
      .order('date', { ascending: true });
    
    if (error) throw error;
    return data;
  },
  
  // Registrar dados de sono
  recordSleepData: async (sleepData) => {
    const { data, error } = await supabase
      .from('sleep_data')
      .insert(sleepData)
      .select();
    
    if (error) throw error;
    return data;
  },
  
  // Obter estatísticas do usuário
  getUserStats: async (date) => {
    const { data, error } = await supabase
      .from('user_stats')
      .select('*')
      .eq('date', date)
      .single();
    
    if (error && error.code !== 'PGRST116') { // PGRST116 - No results found
      throw error;
    }
    
    return data;
  },
  
  // Atualizar estatísticas do usuário
  updateUserStats: async (date, statsData) => {
    const userId = (await supabase.auth.getUser()).data.user.id;
    
    // Verificar se já existe registro para o dia
    const { data: existingData } = await supabase
      .from('user_stats')
      .select('id')
      .eq('user_id', userId)
      .eq('date', date)
      .single();
    
    if (existingData) {
      // Atualizar registro existente
      const { data, error } = await supabase
        .from('user_stats')
        .update(statsData)
        .eq('id', existingData.id)
        .select();
      
      if (error) throw error;
      return data;
    } else {
      // Criar novo registro
      const { data, error } = await supabase
        .from('user_stats')
        .insert({
          user_id: userId,
          date,
          ...statsData
        })
        .select();
      
      if (error) throw error;
      return data;
    }
  }
};

// Objeto para exportação
const api = {
  apiRequest,
  userProfileApi,
  trainingApi,
  healthApi
};

export default api;