import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { ChevronLeft, ChevronRight, Info } from 'lucide-react';

// Generate mock sleep data
const generateSleepData = () => {
  const days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
  
  return days.map(day => {
    // Random total sleep between 5-9 hours
    const totalSleep = 5 + Math.random() * 4;
    
    // Split into deep, light and REM with some randomness
    const deepSleep = Math.round((totalSleep * (0.15 + Math.random() * 0.1)) * 10) / 10;
    const remSleep = Math.round((totalSleep * (0.2 + Math.random() * 0.1)) * 10) / 10;
    const lightSleep = Math.round((totalSleep - deepSleep - remSleep) * 10) / 10;
    
    return {
      day,
      deep: deepSleep,
      light: lightSleep,
      rem: remSleep,
      total: Math.round(totalSleep * 10) / 10
    };
  });
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    
    return (
      <div className="bg-black/80 backdrop-blur-sm border border-white/10 p-3 rounded-lg shadow-lg">
        <p className="text-white font-medium">{label}</p>
        <p className="text-[#EBFF00] font-bold">Total: {data.total}h</p>
        <div className="space-y-1 mt-1">
          <p className="text-blue-400 text-sm">Sono Profundo: {data.deep}h</p>
          <p className="text-green-400 text-sm">REM: {data.rem}h</p>
          <p className="text-purple-400 text-sm">Sono Leve: {data.light}h</p>
        </div>
      </div>
    );
  }

  return null;
};

const SleepChart: React.FC = () => {
  const [data] = React.useState(generateSleepData());
  const [showInfo, setShowInfo] = React.useState(false);
  
  const toggleInfo = () => {
    setShowInfo(!showInfo);
  };
  
  return (
    <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-white font-semibold">Qualidade do Sono</h2>
        <button 
          onClick={toggleInfo}
          className="text-white/60 hover:text-white transition-colors"
        >
          <Info className="w-4 h-4" />
        </button>
      </div>
      
      {showInfo && (
        <div className="mb-4 p-3 bg-white/5 border border-white/10 rounded-xl">
          <p className="text-white/80 text-sm">
            A qualidade do seu sono impacta diretamente seus resultados de treino.
            Monitore seus padrões de sono para otimizar sua recuperação.
          </p>
        </div>
      )}
      
      <div className="flex items-center justify-between mb-2">
        <span className="text-white/60 text-sm">Última semana</span>
        <div className="flex space-x-2">
          <button className="p-1 rounded-full bg-black/40 backdrop-blur-sm border border-white/10
                     text-white/70 hover:text-white hover:border-white/30 transition-all">
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button className="p-1 rounded-full bg-black/40 backdrop-blur-sm border border-white/10
                     text-white/70 hover:text-white hover:border-white/30 transition-all">
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <div className="h-64 w-full mt-1 -ml-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 10, right: 10, left: 0, bottom: 5 }}
            barGap={2}
          >
            <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis 
              dataKey="day" 
              tick={{ fill: 'rgba(255,255,255,0.6)' }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            />
            <YAxis 
              tick={{ fill: 'rgba(255,255,255,0.6)' }}
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              tickFormatter={(value) => `${value}h`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="deep" stackId="a" fill="#3b82f6" radius={[0, 0, 0, 0]} name="Sono Profundo" />
            <Bar dataKey="rem" stackId="a" fill="#22c55e" radius={[0, 0, 0, 0]} name="REM" />
            <Bar dataKey="light" stackId="a" fill="#a855f7" radius={[4, 4, 0, 0]} name="Sono Leve" />
            <Legend 
              iconType="circle" 
              iconSize={8}
              wrapperStyle={{ fontSize: '12px', color: 'white' }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="grid grid-cols-2 gap-3 mt-2">
        <div className="bg-white/5 rounded-xl p-3 border border-white/10">
          <p className="text-white/60 text-xs">Média de sono</p>
          <p className="text-white text-xl font-bold">
            {(data.reduce((sum, item) => sum + item.total, 0) / data.length).toFixed(1)}h
          </p>
        </div>
        <div className="bg-white/5 rounded-xl p-3 border border-white/10">
          <p className="text-white/60 text-xs">Qualidade média</p>
          <p className="text-white text-xl font-bold">
            {Math.round(data.reduce((sum, item) => sum + (item.deep + item.rem) / item.total * 100, 0) / data.length)}%
          </p>
        </div>
      </div>
    </div>
  );
};

export default SleepChart;