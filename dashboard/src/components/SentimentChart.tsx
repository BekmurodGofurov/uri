import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Calendar, TrendingUp } from 'lucide-react';
import { SentimentTimePoint } from '../types/api';

interface SentimentChartProps {
  data: SentimentTimePoint[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const total = payload.reduce((acc: number, curr: any) => acc + (curr.value || 0), 0);
    return (
      <div className="bg-slate-900/95 text-white p-3 rounded-xl shadow-xl border border-slate-700 text-xs backdrop-blur-sm min-w-[160px]">
        <div className="font-bold border-b border-slate-800 pb-1.5 mb-2 text-slate-300 flex items-center justify-between">
          <span>{label}</span>
          <span className="text-[10px] text-slate-400 font-mono">Jami: {total}</span>
        </div>
        <div className="space-y-1.5">
          {payload.map((item: any) => (
            <div key={item.dataKey} className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-1.5">
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <span className="capitalize text-slate-300">
                  {item.dataKey === 'positive'
                    ? 'Ijobiy'
                    : item.dataKey === 'neutral'
                    ? 'Neytral'
                    : 'Salbiy'}
                </span>
              </div>
              <span className="font-bold font-mono text-white">{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }
  return null;
};

export const SentimentChart: React.FC<SentimentChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center flex flex-col items-center justify-center min-h-[300px]">
        <Calendar className="w-8 h-8 text-slate-300 mb-2" />
        <p className="text-sm font-semibold text-slate-600">
          Vaqt bo'yicha kayfiyat ma'lumotlari mavjud emas
        </p>
        <p className="text-xs text-slate-400 mt-1">
          Hozircha vaqt kesimida tahlil qilingan sharhlar soni kam
        </p>
      </div>
    );
  }

  // Format dates for nicer X axis
  const formattedData = data.map((d) => ({
    ...d,
    displayDate: d.date.length > 5 ? d.date.substring(5) : d.date, // e.g. 08-28 instead of 2026-08-28
  }));

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-uzum-50 text-uzum-600 border border-uzum-100">
            <TrendingUp className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-sm sm:text-base">
              Vaqt bo'yicha kayfiyat o'zgarishi
            </h3>
            <p className="text-xs text-slate-500">
              Sharhlarning kunlar bo'yicha ijobiy, neytral va salbiy dinamikasi
            </p>
          </div>
        </div>
      </div>

      {/* Chart container */}
      <div className="h-[280px] w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPositive" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="colorNeutral" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="colorNegative" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis
              dataKey="displayDate"
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
              tick={{ fill: '#64748b', fontSize: 11 }}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#64748b', fontSize: 11 }}
              allowDecimals={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="top"
              align="right"
              iconType="circle"
              wrapperStyle={{ paddingBottom: '12px', fontSize: '11px', fontWeight: 600 }}
              formatter={(value) =>
                value === 'positive'
                  ? 'Ijobiy'
                  : value === 'neutral'
                  ? 'Neytral'
                  : 'Salbiy'
              }
            />

            <Area
              type="monotone"
              dataKey="positive"
              stroke="#10B981"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#colorPositive)"
            />
            <Area
              type="monotone"
              dataKey="neutral"
              stroke="#F59E0B"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorNeutral)"
            />
            <Area
              type="monotone"
              dataKey="negative"
              stroke="#EF4444"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorNegative)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
