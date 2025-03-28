import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BellRing, Search, User, Home as HomeIcon, Dumbbell, 
  Calendar, Settings, Moon, Sun, Heart, Trophy, Flame
} from 'lucide-react';
import DaySelector, { Day } from './DaySelector';
import SleepChart from './SleepChart';
import { useAuth } from '../../context/AuthContext';
import { healthApi, userProfileApi } from '../../utils/api';

const profileImageUrl = 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80';

// Formatar data para YYYY-MM-DD
const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [selectedDay, setSelectedDay] = useState<Day | null>(null);
  const [activeTab, setActiveTab] = useState('home');
  const [stats, setStats] = useState({
    heartRate: '--',
    calories: '--',
    streak: '--',
    sleep: '--',
    lastTraining: '--',
    userName: 'Usuário'
  });
  const [loading, setLoading] = useState(true);
  
  const handleSelectDay = (day: Day) => {
    setSelectedDay(day);
  };
  
  // Buscar estatísticas do usuário
  useEffect(() => {
    const fetchUserStats = async () => {
      setLoading(true);
      
      try {
        // Tentar obter perfil do usuário
        const profile = await userProfileApi.getProfile();
        
        // Buscar estatísticas do dia atual
        const today = formatDate(new Date());
        const userStats = await healthApi.getUserStats(today);
        
        // Atualizar estatísticas
        setStats({
          heartRate: userStats?.heart_rate_avg ? `${userStats.heart_rate_avg}` : '--',
          calories: userStats?.calories_burned ? `${userStats.calories_burned}` : '--',
          streak: userStats?.streak_days ? `${userStats.streak_days}` : '--',
          sleep: userStats?.sleep_hours ? `${userStats.sleep_hours}` : '--',
          lastTraining: userStats?.last_training_day || '--',
          userName: profile?.nome_completo || user?.username || 'Usuário'
        });
      } catch (err) {
        console.error('Erro ao buscar estatísticas do usuário:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUserStats();
  }, [user]);
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0A0A] to-[#1A1A1A] text-white">
      {/* Status Bar */}
      <div className="flex justify-between items-center p-4 bg-black/40 backdrop-blur-sm">
        <div className="flex items-center">
          <span className="text-sm font-medium">{new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm">85%</span>
        </div>
      </div>
      
      {/* Header */}
      <header className="p-4 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-[#EBFF00]">
            <img src={profileImageUrl} alt="Profile" className="w-full h-full object-cover" />
          </div>
          <div>
            <h1 className="font-bold">Olá, {stats.userName}</h1>
            <p className="text-white/60 text-xs">Último treino: {stats.lastTraining}</p>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <button 
            className="w-9 h-9 rounded-full flex items-center justify-center bg-black/40 backdrop-blur-sm
                     border border-white/10 text-white/70 hover:text-white transition-colors"
            aria-label="Search"
          >
            <Search className="w-5 h-5" />
          </button>
          <button 
            className="w-9 h-9 rounded-full flex items-center justify-center bg-black/40 backdrop-blur-sm
                     border border-white/10 text-white/70 hover:text-white transition-colors"
            aria-label="Notifications"
          >
            <BellRing className="w-5 h-5" />
          </button>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="p-4 space-y-6 pb-32">
        {/* Day Selector */}
        <DaySelector onSelectDay={handleSelectDay} />
        
        {/* Sleep Chart */}
        <SleepChart />
        
        {/* Stats Cards */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-4 flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center">
              <Heart className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-white/60 text-xs">Frequência Cardíaca</p>
              <p className="text-white text-xl font-bold">{stats.heartRate} bpm</p>
            </div>
          </div>
          
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-4 flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
              <Flame className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-white/60 text-xs">Calorias (hoje)</p>
              <p className="text-white text-xl font-bold">{stats.calories} kcal</p>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-4 flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center">
              <Trophy className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-white/60 text-xs">Sequência atual</p>
              <p className="text-white text-xl font-bold">{stats.streak} dias</p>
            </div>
          </div>
          
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-4 flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
              <Moon className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-white/60 text-xs">Sono (ontem)</p>
              <p className="text-white text-xl font-bold">{stats.sleep} h</p>
            </div>
          </div>
        </div>
      </main>
      
      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-black/80 backdrop-blur-xl border-t border-white/10 p-2">
        <div className="flex justify-around items-center">
          <button 
            onClick={() => setActiveTab('home')}
            className={`p-2 rounded-xl flex flex-col items-center space-y-1 transition-colors ${activeTab === 'home' ? 'text-[#EBFF00]' : 'text-white/60'}`}
          >
            <HomeIcon className="w-6 h-6" />
            <span className="text-xs">Home</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('workout')}
            className={`p-2 rounded-xl flex flex-col items-center space-y-1 transition-colors ${activeTab === 'workout' ? 'text-[#EBFF00]' : 'text-white/60'}`}
          >
            <Dumbbell className="w-6 h-6" />
            <span className="text-xs">Treinos</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('calendar')}
            className={`p-2 rounded-xl flex flex-col items-center space-y-1 transition-colors ${activeTab === 'calendar' ? 'text-[#EBFF00]' : 'text-white/60'}`}
          >
            <Calendar className="w-6 h-6" />
            <span className="text-xs">Agenda</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('profile')}
            className={`p-2 rounded-xl flex flex-col items-center space-y-1 transition-colors ${activeTab === 'profile' ? 'text-[#EBFF00]' : 'text-white/60'}`}
          >
            <User className="w-6 h-6" />
            <span className="text-xs">Perfil</span>
          </button>
          
          <button 
            onClick={() => navigate('/settings')}
            className={`p-2 rounded-xl flex flex-col items-center space-y-1 transition-colors ${activeTab === 'settings' ? 'text-[#EBFF00]' : 'text-white/60'}`}
          >
            <Settings className="w-6 h-6" />
            <span className="text-xs">Config</span>
          </button>
        </div>
      </nav>
      
      {/* FAB - Start Workout Button */}
      <button className="fixed bottom-24 right-4 w-14 h-14 rounded-full bg-[#EBFF00] flex items-center justify-center shadow-[0_0_20px_rgba(235,255,0,0.3)] hover:shadow-[0_0_30px_rgba(235,255,0,0.5)] transition-all">
        <Dumbbell className="w-7 h-7 text-black" />
      </button>
    </div>
  );
};

export default Home;