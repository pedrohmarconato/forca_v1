import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Dumbbell, ChevronDown, Heart, StretchVertical as Stretch } from 'lucide-react';
import { userProfileApi } from '../utils/api.js';
import { useAuth } from '../context/AuthContext.tsx';

function Questionario() {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [formData, setFormData] = useState({
    nome: user?.username || '',
    genero: '',
    dataNascimento: {
      dia: '1',
      mes: '1',
      ano: '1990'
    },
    peso: '',
    altura: '',
    temLesoes: false,
    lesoes: [],
    descricaoLesao: '',
    experienciaTreino: 'iniciante',
    tempoTreino: 0,
    objetivo: '',
    diasTreino: [],
    tempoTreinoDiario: 30,
    preferenciaCardio: false,
    preferenciaAlongamento: false
  });
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');

  const diasSemana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'];
  const objetivos = ['Hipertrofia', 'Emagrecimento', 'Força', 'Resistência', 'Condicionamento Geral'];
  const tempoOpcoes = [30, 45, 60, 90];
  const tiposLesoes = [
    'Lesão no Joelho',
    'Lesão no Ombro',
    'Lesão nas Costas',
    'Lesão no Tornozelo',
    'Lesão no Punho',
    'Lesão no Quadril',
    'Tendinite'
  ];

  const dias = Array.from({ length: 31 }, (_, i) => (i + 1).toString().padStart(2, '0'));
  const meses = Array.from({ length: 12 }, (_, i) => (i + 1).toString().padStart(2, '0'));
  const anoAtual = new Date().getFullYear();
  const anos = Array.from({ length: 100 }, (_, i) => (anoAtual - i).toString());

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // Verificar se o usuário está autenticado
      if (!user) {
        throw new Error('Você precisa estar conectado para enviar o questionário');
      }
      
      // Verificar campos obrigatórios
      if (formData.diasTreino.length === 0) {
        throw new Error('Selecione pelo menos um dia de treino');
      }
      
      if (!formData.objetivo) {
        throw new Error('Selecione um objetivo de treino');
      }
      
      // Enviar dados para a API
      await userProfileApi.submitQuestionnaireData(formData);
      
      // Exibir mensagem de sucesso
      setSuccess('Questionário enviado com sucesso! Seu plano de treino está sendo gerado.');
      
      // Redirecionar para a página inicial após 2 segundos
      setTimeout(() => {
        navigate('/');
      }, 2000);
      
    } catch (err) {
      console.error('Erro ao enviar questionário:', err);
      setError(err.message || 'Ocorreu um erro ao enviar o questionário. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleDiaTreinoChange = (dia) => {
    setFormData(prev => ({
      ...prev,
      diasTreino: prev.diasTreino.includes(dia)
        ? prev.diasTreino.filter(d => d !== dia)
        : [...prev.diasTreino, dia]
    }));
  };

  const handleLesaoChange = (lesao) => {
    setFormData(prev => ({
      ...prev,
      lesoes: prev.lesoes.includes(lesao)
        ? prev.lesoes.filter(l => l !== lesao)
        : [...prev.lesoes, lesao]
    }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] relative">
      {/* Decorative Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-white/20 rounded-full blur-[100px] -translate-x-1/2 -translate-y-1/2" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-[#EBFF00]/10 rounded-full blur-[100px] translate-x-1/2 translate-y-1/2" />
      </div>

      <div className="w-full max-w-2xl p-8 rounded-2xl shadow-xl relative overflow-hidden backdrop-blur-sm my-8">
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
              <p className="text-white text-sm font-medium italic -mt-2 drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]">
                Treinamento inteligente
              </p>
            </div>
            <p className="text-white mt-6 text-lg drop-shadow-[0_0_10px_rgba(255,255,255,0.6)]">
              Vamos criar seu treino personalizado! Responda o questionário abaixo para que possamos desenvolver o melhor programa para você.
            </p>
          </div>

          {/* Error and Success Messages */}
          {error && (
            <div className="mb-6 p-3 bg-red-900/50 border border-red-500/50 rounded-xl text-white text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-6 p-3 bg-green-900/50 border border-green-500/50 rounded-xl text-white text-sm">
              {success}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="relative group">
                <select
                  value={formData.genero}
                  onChange={(e) => setFormData({...formData, genero: e.target.value})}
                  className="w-full px-4 py-3 rounded-xl bg-white/5 text-white placeholder-white/40 border border-white/10 focus:outline-none focus:border-white/30 focus:bg-white/10 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-all backdrop-blur-sm appearance-none hover:border-white/40"
                >
                  <option value="" className="bg-[#020202]">Selecione seu gênero</option>
                  <option value="masculino" className="bg-[#020202]">Masculino</option>
                  <option value="feminino" className="bg-[#020202]">Feminino</option>
                  <option value="outro" className="bg-[#020202]">Outro</option>
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/50 pointer-events-none transition-transform group-focus-within:text-white group-focus-within:drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
              </div>

              <div className="relative">
                <label className="block text-white text-sm mb-2 drop-shadow-[0_0_8px_rgba(255,255,255,0.6)]">
                  Data de Nascimento
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <select
                    value={formData.dataNascimento.dia}
                    onChange={(e) => setFormData({
                      ...formData,
                      dataNascimento: { ...formData.dataNascimento, dia: e.target.value }
                    })}
                    className="w-full px-2 py-3 rounded-xl bg-white/5 text-white placeholder-white/40 border border-white/10 focus:outline-none focus:border-white/30 focus:bg-white/10 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-all backdrop-blur-sm appearance-none hover:border-white/40"
                  >
                    {dias.map(dia => (
                      <option key={dia} value={dia} className="bg-[#020202]">{dia}</option>
                    ))}
                  </select>
                  <select
                    value={formData.dataNascimento.mes}
                    onChange={(e) => setFormData({
                      ...formData,
                      dataNascimento: { ...formData.dataNascimento, mes: e.target.value }
                    })}
                    className="w-full px-2 py-3 rounded-xl bg-white/5 text-white placeholder-white/40 border border-white/10 focus:outline-none focus:border-white/30 focus:bg-white/10 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-all backdrop-blur-sm appearance-none hover:border-white/40"
                  >
                    {meses.map(mes => (
                      <option key={mes} value={mes} className="bg-[#020202]">{mes}</option>
                    ))}
                  </select>
                  <select
                    value={formData.dataNascimento.ano}
                    onChange={(e) => setFormData({
                      ...formData,
                      dataNascimento: { ...formData.dataNascimento, ano: e.target.value }
                    })}
                    className="w-full px-2 py-3 rounded-xl bg-white/5 text-white placeholder-white/40 border border-white/10 focus:outline-none focus:border-white/30 focus:bg-white/10 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-all backdrop-blur-sm appearance-none hover:border-white/40"
                  >
                    {anos.map(ano => (
                      <option key={ano} value={ano} className="bg-[#020202]">{ano}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="relative">
                <input
                  type="text"
                  inputMode="decimal"
                  pattern="[0-9]*[.,]?[0-9]*"
                  value={formData.peso}
                  onChange={(e) => {
                    const value = e.target.value.replace(',', '.');
                    if (/^\d*\.?\d*$/.test(value)) {
                      setFormData({...formData, peso: value});
                    }
                  }}
                  placeholder="Peso (kg)"
                  className="w-full px-4 py-3 rounded-xl bg-white/5 text-white placeholder-white/40 border border-white/10 focus:outline-none focus:border-white/30 focus:bg-white/10 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-all backdrop-blur-sm hover:border-white/40"
                />
                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-white/50">kg</span>
              </div>

              <div className="relative">
                <input
                  type="text"
                  inputMode="decimal"
                  pattern="[0-9]*"
                  value={formData.altura}
                  onChange={(e) => {
                    if (/^\d*$/.test(e.target.value)) {
                      setFormData({...formData, altura: e.target.value});
                    }
                  }}
                  placeholder="Altura (cm)"
                  className="w-full px-4 py-3 rounded-xl bg-white/5 text-white placeholder-white/40 border border-white/10 focus:outline-none focus:border-white/30 focus:bg-white/10 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-all backdrop-blur-sm hover:border-white/40"
                />
                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-white/50">cm</span>
              </div>
            </div>

            <div className="space-y-4">
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.temLesoes}
                  onChange={(e) => setFormData({...formData, temLesoes: e.target.checked})}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-white/5 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#EBFF00]"></div>
                <span className="ml-3 text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.6)]">Possui alguma lesão?</span>
              </label>

              {formData.temLesoes && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-2">
                    {tiposLesoes.map((lesao) => (
                      <button
                        key={lesao}
                        type="button"
                        onClick={() => handleLesaoChange(lesao)}
                        className={`px-4 py-3 rounded-xl border transition-all text-sm ${
                          formData.lesoes.includes(lesao)
                            ? 'bg-[#EBFF00] text-black border-transparent'
                            : 'border-white/20 text-white hover:border-white/40'
                        }`}
                      >
                        {lesao}
                      </button>
                    ))}
                  </div>
                  <textarea
                    value={formData.descricaoLesao}
                    onChange={(e) => setFormData({...formData, descricaoLesao: e.target.value})}
                    placeholder="Descreva mais detalhes sobre suas lesões..."
                    className="w-full px-4 py-3 rounded-xl bg-white/5 text-white placeholder-white/40 border border-white/10 focus:outline-none focus:border-white/30 focus:bg-white/10 focus:shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-all backdrop-blur-sm resize-none hover:border-white/40"
                    rows={3}
                  />
                </div>
              )}
            </div>

            <div>
              <label className="block text-white text-sm mb-4 drop-shadow-[0_0_8px_rgba(255,255,255,0.6)]">
                Experiência em treino
              </label>
              <div className="grid grid-cols-3 gap-3">
                {['Iniciante', 'Intermediário', 'Avançado'].map((nivel) => (
                  <button
                    key={nivel}
                    type="button"
                    onClick={() => setFormData({...formData, experienciaTreino: nivel.toLowerCase()})}
                    className={`px-4 py-3 rounded-xl border transition-all ${
                      formData.experienciaTreino === nivel.toLowerCase()
                        ? 'bg-[#EBFF00] text-black border-transparent'
                        : 'border-white/20 text-white hover:border-white/40'
                    }`}
                  >
                    {nivel}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-white text-sm mb-2 drop-shadow-[0_0_8px_rgba(255,255,255,0.6)]">
                Tempo de treino (anos)
              </label>
              <div className="relative pt-6">
                <input
                  type="range"
                  min="0"
                  max="20"
                  value={formData.tempoTreino}
                  onChange={(e) => setFormData({...formData, tempoTreino: parseInt(e.target.value)})}
                  className="w-full h-2 bg-white/5 rounded-lg appearance-none cursor-pointer accent-white"
                />
                <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 text-white font-medium drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]">
                  {formData.tempoTreino} {formData.tempoTreino === 1 ? 'ano' : 'anos'}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-white text-sm mb-4 drop-shadow-[0_0_8px_rgba(255,255,255,0.6)]">
                Objetivo
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {objetivos.map((objetivo) => (
                  <button
                    key={objetivo}
                    type="button"
                    onClick={() => setFormData({...formData, objetivo})}
                    className={`px-4 py-3 rounded-xl border transition-all ${
                      formData.objetivo === objetivo
                        ? 'bg-[#EBFF00] text-black border-transparent'
                        : 'border-white/20 text-white hover:border-white/40'
                    }`}
                  >
                    {objetivo}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-white text-sm mb-4 drop-shadow-[0_0_8px_rgba(255,255,255,0.6)]">
                Dias de treino
              </label>
              <div className="grid grid-cols-7 gap-2">
                {diasSemana.map((dia) => (
                  <button
                    key={dia}
                    type="button"
                    onClick={() => handleDiaTreinoChange(dia)}
                    className={`aspect-square rounded-xl border flex items-center justify-center transition-all text-sm ${
                      formData.diasTreino.includes(dia)
                        ? 'bg-[#EBFF00] text-black border-transparent'
                        : 'border-white/20 text-white hover:border-white/40'
                    }`}
                  >
                    {dia}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-white text-sm mb-4 drop-shadow-[0_0_8px_rgba(255,255,255,0.6)]">
                Tempo por treino
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {tempoOpcoes.map((tempo) => (
                  <button
                    key={tempo}
                    type="button"
                    onClick={() => setFormData({...formData, tempoTreinoDiario: tempo})}
                    className={`px-4 py-3 rounded-xl border transition-all ${
                      formData.tempoTreinoDiario === tempo
                        ? 'bg-[#EBFF00] text-black border-transparent'
                        : 'border-white/20 text-white hover:border-white/40'
                    }`}
                  >
                    {tempo} min
                  </button>
                ))}
              </div>
            </div>

            {/* Cardio and Stretching Questions */}
            <div className="space-y-6">
              <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/20 backdrop-blur-sm hover:border-white/40 transition-all">
                <div className="flex items-center space-x-3">
                  <Heart className="w-6 h-6 text-[#EBFF00]" />
                  <span className="text-white">Incluir cardio no treino?</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.preferenciaCardio}
                    onChange={(e) => setFormData({...formData, preferenciaCardio: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-white/5 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#EBFF00]"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/20 backdrop-blur-sm hover:border-white/40 transition-all">
                <div className="flex items-center space-x-3">
                  <Stretch className="w-6 h-6 text-[#EBFF00]" />
                  <span className="text-white">Incluir alongamento no treino?</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.preferenciaAlongamento}
                    onChange={(e) => setFormData({...formData, preferenciaAlongamento: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-white/5 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#EBFF00]"></div>
                </label>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#EBFF00] text-black font-semibold py-3 rounded-xl flex items-center justify-center space-x-2 hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] transition-all mt-8 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{loading ? 'Enviando...' : 'Criar Meu Treino'}</span>
              <Dumbbell className="w-5 h-5" />
            </button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-white/40 text-xs">Fabricado no Brasil</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Questionario;