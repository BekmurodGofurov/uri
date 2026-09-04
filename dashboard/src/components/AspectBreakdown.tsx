import React from 'react';
import {
  Package,
  Truck,
  DollarSign,
  UserCheck,
  Box,
  HelpCircle,
  BarChart3,
  ThumbsUp,
  ThumbsDown,
} from 'lucide-react';
import { AspectPolaritySummary } from '../types/api';

interface AspectBreakdownProps {
  aspects: AspectPolaritySummary[];
}

const ASPECT_CONFIG: Record<
  string,
  { label: string; icon: React.FC<{ className?: string }>; color: string }
> = {
  quality: {
    label: 'Mahsulot sifati',
    icon: Package,
    color: 'text-indigo-600 bg-indigo-50 border-indigo-100',
  },
  delivery: {
    label: 'Yetkazib berish',
    icon: Truck,
    color: 'text-blue-600 bg-blue-50 border-blue-100',
  },
  price: {
    label: 'Narx va qiymat',
    icon: DollarSign,
    color: 'text-emerald-600 bg-emerald-50 border-emerald-100',
  },
  seller: {
    label: 'Sotuvchi xizmati',
    icon: UserCheck,
    color: 'text-purple-600 bg-purple-50 border-purple-100',
  },
  packaging: {
    label: 'Qadoqlanish holati',
    icon: Box,
    color: 'text-amber-600 bg-amber-50 border-amber-100',
  },
  other: {
    label: 'Boshqa jihatlar',
    icon: HelpCircle,
    color: 'text-slate-600 bg-slate-50 border-slate-100',
  },
};

export const AspectBreakdown: React.FC<AspectBreakdownProps> = ({ aspects }) => {
  if (!aspects || aspects.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center flex flex-col items-center justify-center min-h-[300px]">
        <BarChart3 className="w-8 h-8 text-slate-300 mb-2" />
        <p className="text-sm font-semibold text-slate-600">Jihatlar tahlili mavjud emas</p>
        <p className="text-xs text-slate-400 mt-1">
          Hozircha jihatlar bo'yicha tahlil qilingan sharhlar topilmadi
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-uzum-50 text-uzum-600 border border-uzum-100">
            <BarChart3 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-sm sm:text-base">
              Jihatlar tahlili (Aspect Breakdown)
            </h3>
            <p className="text-xs text-slate-500">
              Sifat, yetkazib berish, narx va qadoqlash bo'yicha xaridorlar munosabati
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 pt-2">
        {aspects.map((item) => {
          const config = ASPECT_CONFIG[item.aspect.toLowerCase()] || {
            label: item.aspect,
            icon: HelpCircle,
            color: 'text-slate-600 bg-slate-50 border-slate-100',
          };
          const Icon = config.icon;

          const total = item.total || item.positive + item.neutral + item.negative;
          const posPct = total > 0 ? Math.round((item.positive / total) * 100) : 0;
          const neuPct = total > 0 ? Math.round((item.neutral / total) * 100) : 0;
          const negPct = total > 0 ? 100 - posPct - neuPct : 0;

          return (
            <div
              key={item.aspect}
              className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-slate-50 hover:border-slate-200 transition-colors flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2.5">
                    <div className={`p-1.5 rounded-lg border ${config.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-800 text-sm">{config.label}</h4>
                      <span className="text-[11px] text-slate-400 font-medium">
                        {total} ta sharhda tilga olingan
                      </span>
                    </div>
                  </div>

                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                      posPct >= 60
                        ? 'bg-emerald-100 text-emerald-800'
                        : negPct >= 40
                        ? 'bg-rose-100 text-rose-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {posPct}% ijobiy
                  </span>
                </div>

                {/* Progress bar */}
                <div className="h-2 w-full rounded-full bg-slate-200 overflow-hidden flex my-3">
                  <div
                    style={{ width: `${posPct}%` }}
                    className="bg-emerald-500 transition-all duration-300"
                    title={`Ijobiy: ${item.positive} ta (${posPct}%)`}
                  />
                  <div
                    style={{ width: `${neuPct}%` }}
                    className="bg-amber-400 transition-all duration-300"
                    title={`Neytral: ${item.neutral} ta (${neuPct}%)`}
                  />
                  <div
                    style={{ width: `${negPct}%` }}
                    className="bg-rose-500 transition-all duration-300"
                    title={`Salbiy: ${item.negative} ta (${negPct}%)`}
                  />
                </div>
              </div>

              {/* Detailed tallies */}
              <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-200/60 text-slate-500 font-medium">
                <span className="flex items-center gap-1 text-emerald-700 font-semibold">
                  <ThumbsUp className="w-3 h-3" /> {item.positive} ijobiy
                </span>
                <span className="text-amber-700 font-semibold">{item.neutral} neytral</span>
                <span className="flex items-center gap-1 text-rose-700 font-semibold">
                  <ThumbsDown className="w-3 h-3" /> {item.negative} salbiy
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
