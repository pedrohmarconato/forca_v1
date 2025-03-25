import React, { useState } from 'react';
import { Calendar, ChevronLeft, ChevronRight, Info } from 'lucide-react';

export type Day = {
  date: Date;
  isToday: boolean;
  status?: 'completed' | 'partial' | 'missed' | 'scheduled';
  sleepQuality?: number; // 0-100%
};

const generateDayData = (): Day[] => {
  const today = new Date();
  const days: Day[] = [];
  
  // Generate 14 days (previous week + current week + upcoming days)
  for (let i = -7; i < 7; i++) {
    const date = new Date();
    date.setDate(today.getDate() + i);
    
    // Generate random status for demo purposes
    const statuses = ['completed', 'partial', 'missed', 'scheduled'] as const;
    const randomStatus = i < 0 
      ? statuses[Math.floor(Math.random() * 3)] // Past days can't be scheduled
      : statuses[Math.floor(Math.random() * 4)];
    
    days.push({
      date,
      isToday: i === 0,
      status: randomStatus,
      sleepQuality: Math.floor(Math.random() * 101), // Random 0-100%
    });
  }
  
  return days;
};

const formatDayName = (date: Date): string => {
  const days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'];
  return days[date.getDay()];
};

const getStatusColor = (status: Day['status']) => {
  switch (status) {
    case 'completed': return 'bg-green-500';
    case 'partial': return 'bg-yellow-500';
    case 'missed': return 'bg-red-500';
    case 'scheduled': return 'bg-blue-500';
    default: return 'bg-gray-300';
  }
};

interface DaySelectorProps {
  onSelectDay: (day: Day) => void;
}

const DaySelector: React.FC<DaySelectorProps> = ({ onSelectDay }) => {
  const [days] = useState<Day[]>(generateDayData());
  const [selectedDay, setSelectedDay] = useState<Day | null>(days.find(day => day.isToday) || null);
  const [currentIndex, setCurrentIndex] = useState(7); // Start with today in view
  const [showModal, setShowModal] = useState(false);
  
  const visibleDays = days.slice(currentIndex - 3, currentIndex + 4);
  
  const handleSelectDay = (day: Day) => {
    setSelectedDay(day);
    onSelectDay(day);
  };
  
  const scrollLeft = () => {
    if (currentIndex > 3) {
      setCurrentIndex(currentIndex - 1);
    }
  };
  
  const scrollRight = () => {
    if (currentIndex < days.length - 4) {
      setCurrentIndex(currentIndex + 1);
    }
  };
  
  const toggleModal = () => {
    setShowModal(!showModal);
  };
  
  return (
    <div className="relative">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <Calendar className="w-5 h-5 text-[#EBFF00]" />
          <h2 className="text-white font-medium">Histórico de treinos</h2>
        </div>
        <button
          onClick={toggleModal}
          className="text-white/60 hover:text-white transition-colors"
          aria-label="Informações do histórico"
        >
          <Info className="w-5 h-5" />
        </button>
      </div>
      
      <div className="relative flex items-center">
        <button
          onClick={scrollLeft}
          className="absolute left-0 z-10 p-1 rounded-full bg-black/40 backdrop-blur-sm border border-white/10
                   text-white/70 hover:text-white hover:border-white/30 transition-all -ml-2"
          aria-label="Scroll left"
          disabled={currentIndex <= 3}
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        
        <div className="flex overflow-hidden relative w-full">
          <div className="w-full flex space-x-2 transition-transform duration-300 ease-out">
            {visibleDays.map((day, index) => {
              const isSelected = selectedDay && 
                selectedDay.date.toDateString() === day.date.toDateString();
              
              return (
                <button
                  key={day.date.toISOString()}
                  onClick={() => handleSelectDay(day)}
                  className={`flex-1 flex flex-col items-center justify-center py-2 rounded-xl
                             border transition-all ${isSelected
                    ? 'bg-black/60 backdrop-blur-sm border-[#EBFF00]/70 shadow-[0_0_15px_rgba(235,255,0,0.2)]'
                    : 'bg-white/5 border-white/10 hover:border-white/30'
                  }`}
                >
                  <span className={`text-xs ${day.isToday ? 'text-[#EBFF00]' : 'text-white/70'}`}>
                    {formatDayName(day.date)}
                  </span>
                  <span className={`text-lg font-semibold ${day.isToday ? 'text-[#EBFF00]' : 'text-white'}`}>
                    {day.date.getDate()}
                  </span>
                  <div className="mt-1 w-2 h-2 rounded-full" style={{
                    backgroundColor: day.status ? getStatusColor(day.status).replace('bg-', '') : 'transparent'
                  }} />
                </button>
              );
            })}
          </div>
        </div>
        
        <button
          onClick={scrollRight}
          className="absolute right-0 z-10 p-1 rounded-full bg-black/40 backdrop-blur-sm border border-white/10
                   text-white/70 hover:text-white hover:border-white/30 transition-all -mr-2"
          aria-label="Scroll right"
          disabled={currentIndex >= days.length - 4}
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
      
      {/* Info Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70">
          <div className="bg-[#0F0F0F] border border-white/10 rounded-2xl p-6 max-w-md w-full max-h-[80vh] overflow-y-auto
                        shadow-[0_0_30px_rgba(0,0,0,0.8)] backdrop-blur-sm animate-[fadeIn_0.3s_ease-out]">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-white">Legenda</h3>
              <button
                onClick={toggleModal}
                className="text-white/60 hover:text-white transition-colors"
                aria-label="Fechar modal"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 rounded-full bg-green-500" />
                <span className="text-white">Treino completo</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 rounded-full bg-yellow-500" />
                <span className="text-white">Treino parcial</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 rounded-full bg-red-500" />
                <span className="text-white">Treino perdido</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 rounded-full bg-blue-500" />
                <span className="text-white">Treino agendado</span>
              </div>
            </div>
            
            <button
              onClick={toggleModal}
              className="mt-6 w-full py-3 rounded-xl bg-[#EBFF00] text-black font-medium
                       hover:shadow-[0_0_20px_rgba(235,255,0,0.3)] transition-all"
            >
              Entendi
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DaySelector;