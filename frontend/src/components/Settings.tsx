import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, LogOut, HelpCircle, Database, User, Bell, Moon, Shield } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import SupabaseDiagnostic from './SupabaseDiagnostic';

const Settings: React.FC = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState<string | null>(null);
  
  const handleSignOut = async () => {
    try {
      await signOut();
      navigate('/login');
    } catch (error) {
      console.error('Erro ao sair:', error);
    }
  };
  
  const handleBack = () => {
    if (activeSection) {
      setActiveSection(null);
    } else {
      navigate('/home');
    }
  };
  
  // Renderizar seção de configurações de conexão
  const renderConnectionSettings = () => (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-white mb-4">Diagnóstico de Conexão</h2>
      <SupabaseDiagnostic />
    </div>
  );
  
  // Renderizar seção de configurações de conta
  const renderAccountSettings = () => (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-white mb-4">Configurações da Conta</h2>
      
      <div className="space-y-4">
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-white">Email</h3>
              <p className="text-white/60 text-sm">{user?.email}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-white">Nome de usuário</h3>
              <p className="text-white/60 text-sm">{user?.username || 'Não definido'}</p>
            </div>
            <button 
              className="px-3 py-1.5 rounded-lg bg-white/10 text-white text-sm hover:bg-white/20 transition-colors"
            >
              Editar
            </button>
          </div>
        </div>
        
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl p-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-white">Senha</h3>
              <p className="text-white/60 text-sm">••••••••</p>
            </div>
            <button 
              onClick={() => navigate('/reset-password')}
              className="px-3 py-1.5 rounded-lg bg-white/10 text-white text-sm hover:bg-white/20 transition-colors"
            >
              Alterar
            </button>
          </div>
        </div>
        
        <button
          onClick={handleSignOut}
          className="w-full mt-4 flex items-center justify-center space-x-2 p-3 rounded-xl bg-red-900/20 text-red-400 border border-red-500/30 hover:bg-red-900/40 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span>Sair da conta</span>
        </button>
      </div>
    </div>
  );
  
  // Renderizar lista principal de configurações
  const renderMainSettings = () => (
    <>
      <div className="grid grid-cols-1 gap-4">
        <button
          onClick={() => setActiveSection('account')}
          className="flex items-center justify-between p-5 bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl text-white hover:bg-black/50 transition-colors"
        >
          <div className="flex items-center">
            <User className="w-5 h-5 mr-3 text-[#EBFF00]" />
            <span>Conta</span>
          </div>
          <ArrowLeft className="w-4 h-4 transform rotate-180 text-white/60" />
        </button>
        
        <button
          onClick={() => setActiveSection('notifications')}
          className="flex items-center justify-between p-5 bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl text-white hover:bg-black/50 transition-colors"
        >
          <div className="flex items-center">
            <Bell className="w-5 h-5 mr-3 text-[#EBFF00]" />
            <span>Notificações</span>
          </div>
          <ArrowLeft className="w-4 h-4 transform rotate-180 text-white/60" />
        </button>
        
        <button
          onClick={() => setActiveSection('appearance')}
          className="flex items-center justify-between p-5 bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl text-white hover:bg-black/50 transition-colors"
        >
          <div className="flex items-center">
            <Moon className="w-5 h-5 mr-3 text-[#EBFF00]" />
            <span>Aparência</span>
          </div>
          <ArrowLeft className="w-4 h-4 transform rotate-180 text-white/60" />
        </button>
        
        <button
          onClick={() => setActiveSection('privacy')}
          className="flex items-center justify-between p-5 bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl text-white hover:bg-black/50 transition-colors"
        >
          <div className="flex items-center">
            <Shield className="w-5 h-5 mr-3 text-[#EBFF00]" />
            <span>Privacidade</span>
          </div>
          <ArrowLeft className="w-4 h-4 transform rotate-180 text-white/60" />
        </button>
        
        <button
          onClick={() => setActiveSection('connection')}
          className="flex items-center justify-between p-5 bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl text-white hover:bg-black/50 transition-colors"
        >
          <div className="flex items-center">
            <Database className="w-5 h-5 mr-3 text-[#EBFF00]" />
            <span>Conexão</span>
          </div>
          <ArrowLeft className="w-4 h-4 transform rotate-180 text-white/60" />
        </button>
        
        <button
          onClick={() => setActiveSection('help')}
          className="flex items-center justify-between p-5 bg-black/40 backdrop-blur-xl border border-white/10 rounded-xl text-white hover:bg-black/50 transition-colors"
        >
          <div className="flex items-center">
            <HelpCircle className="w-5 h-5 mr-3 text-[#EBFF00]" />
            <span>Ajuda</span>
          </div>
          <ArrowLeft className="w-4 h-4 transform rotate-180 text-white/60" />
        </button>
      </div>
      
      <div className="mt-8 text-center">
        <p className="text-white/40 text-sm">Versão 1.0.0</p>
        <p className="text-white/40 text-xs mt-1">FORCA App © {new Date().getFullYear()}</p>
      </div>
    </>
  );
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0A0A0A] to-[#1A1A1A] text-white">
      {/* Header */}
      <header className="p-4 flex items-center">
        <button 
          onClick={handleBack}
          className="w-10 h-10 rounded-full flex items-center justify-center bg-black/40 
                     backdrop-blur-sm border border-white/10 text-white"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-lg font-bold ml-4">
          {activeSection ? 
            activeSection.charAt(0).toUpperCase() + activeSection.slice(1) : 
            'Configurações'}
        </h1>
      </header>
      
      {/* Main Content */}
      <main className="p-4 pb-32">
        {activeSection === 'account' && renderAccountSettings()}
        {activeSection === 'connection' && renderConnectionSettings()}
        {activeSection === null && renderMainSettings()}
      </main>
    </div>
  );
};

export default Settings;