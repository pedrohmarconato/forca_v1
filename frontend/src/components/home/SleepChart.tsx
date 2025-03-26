import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { ChevronLeft, ChevronRight, Info } from 'lucide-react';
import { healthApi } from '../../utils/api';

interface SleepData {
  day: string;
  date: string;
  deep: number;
  light: number;
  rem: number;
  total: number;
}

// Mapear dias da semana
const getDayName = (dateString: string): string => {
  const days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
  const date = new Date(dateString);
  return days[date.getDay()];
};

// Formatar data para YYYY-MM-DD
const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

// Obter data de 7 dias atrás
const getLastWeekDate = (): string => {
  const date = new Date();
  date.setDate(date.getDate() - 6);
  return formatDate(date);
};

// Obter data atual
const getCurrentDate = (): string => {
  return formatDate(new Date());
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    
    return (
      <div className="bg-black/80 backdrop-blur-sm border border-white/10 p-3 rounded-lg shadow-lg">
        <p className="text-white font-medium">{label}</p>
        <p className="text-[#EBFF00] font-bold">Total: {data.total.toFixed(1)}h</p>
        <div className="space-y-1 mt-1">
          <p className="text-blue-400 text-sm">Sono Profundo: {data.deep.toFixed(1)}h</p>
          <p className="text-green-400 text-sm">REM: {data.rem.toFixed(1)}h</p>
          <p className="text-purple-400 text-sm">Sono Leve: {data.light.toFixed(1)}h</p>
        </div>
      </div>
    );
  }

  return null;
};

const SleepChart: React.FC = () => {
  const [data, setData] = useState<SleepData[]>([]);
  const [showInfo, setShowInfo] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState({
    startDate: getLastWeekDate(),
    endDate: getCurrentDate()
  });
  
  const toggleInfo = () => {
    setShowInfo(!showInfo);
  };
  
  // Navegar para semana anterior
  const goToPreviousWeek = () => {
    const newStartDate = new Date(dateRange.startDate);
    newStartDate.setDate(newStartDate.getDate() - 7);
    
    const newEndDate = new Date(dateRange.endDate);
    newEndDate.setDate(newEndDate.getDate() - 7);
    
    setDateRange({
      startDate: formatDate(newStartDate),
      endDate: formatDate(newEndDate)
    });
  };
  
  // Navegar para próxima semana
  const goToNextWeek = () => {
    const today = formatDate(new Date());
    
    const newStartDate = new Date(dateRange.startDate);
    newStartDate.setDate(newStartDate.getDate() + 7);
    
    const newEndDate = new Date(dateRange.endDate);
    newEndDate.setDate(newEndDate.getDate() + 7);
    
    // Não permitir navegar para datas futuras
    if (formatDate(newEndDate) > today) {
      return;
    }
    
    setDateRange({
      startDate: formatDate(newStartDate),
      endDate: formatDate(newEndDate)
    });
  };
  
  // Calcular média de sono
  const calculateAverageSleep = (): number => {
    if (data.length === 0) return 0;
    return data.reduce((sum, item) => sum + item.total, 0) / data.length;
  };
  
  // Calcular qualidade média (sono profundo + REM) / total * 100
  const calculateAverageQuality = (): number => {
    if (data.length === 0) return 0;
    return Math.round(data.reduce((sum, item) => 
      sum + ((item.deep + item.rem) / (item.total || 1)) * 100, 0) / data.length);
  };
  
  // Buscar dados de sono do Supabase
  useEffect(() => {
    const fetchSleepData = async () => {
      setLoading(true);
      setError('');
      
      try {
        const response = await healthApi.getSleepData(dateRange.startDate, dateRange.endDate);
        
        // Se não houver dados, mostrar dados vazios para os dias no intervalo
        if (!response || response.length === 0) {
          const emptyData: SleepData[] = [];
          const start = new Date(dateRange.startDate);
          const end = new Date(dateRange.endDate);
          
          for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
            const dateStr = formatDate(d);
            emptyData.push({
              day: getDayName(dateStr),
              date: dateStr,
              deep: 0,
              light: 0,
              rem: 0,
              total: 0
            });
          }
          
          setData(emptyData);
        } else {
          // Transformar dados para o formato esperado pelo gráfico
          const formattedData: SleepData[] = response.map(record => ({
            day: getDayName(record.date),
            date: record.date,
            deep: record.deep_sleep_hours || 0,
            light: record.light_sleep_hours || 0,
            rem: record.rem_sleep_hours || 0,
            total: record.total_sleep_hours || 0
          }));
          
          setData(formattedData);
        }
      } catch (err) {
        console.error('Erro ao buscar dados de sono:', err);
        setError('Não foi possível carregar os dados de sono.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchSleepData();
  }, [dateRange]);
  
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
        <span className="text-white/60 text-sm">
          {dateRange.startDate} a {dateRange.endDate}
        </span>
        <div className="flex space-x-2">
          <button 
            onClick={goToPreviousWeek}
            className="p-1 rounded-full bg-black/40 backdrop-blur-sm border border-white/10
                   text-white/70 hover:text-white hover:border-white/30 transition-all"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button 
            onClick={goToNextWeek}
            disabled={dateRange.endDate === getCurrentDate()}
            className="p-1 rounded-full bg-black/40 backdrop-blur-sm border border-white/10
                   text-white/70 hover:text-white hover:border-white/30 transition-all
                   disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {error && (
        <div className="p-3 bg-red-900/50 border border-red-500/50 rounded-xl text-white text-sm my-4">
          {error}
        </div>
      )}
      
      {loading ? (
        <div className="h-64 w-full flex items-center justify-center">
          <div className="text-white/60">Carregando dados...</div>
        </div>
      ) : (
        <>
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
                {calculateAverageSleep().toFixed(1)}h
              </p>
            </div>
            <div className="bg-white/5 rounded-xl p-3 border border-white/10">
              <p className="text-white/60 text-xs">Qualidade média</p>
              <p className="text-white text-xl font-bold">
                {calculateAverageQuality()}%
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default SleepChart;