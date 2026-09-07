import { Bot, Sparkles, Activity, RefreshCw } from 'lucide-react';
import { ApiStatus } from '../services/api';

interface HeaderProps {
  apiStatus: ApiStatus;
  activeModelVersions: string[];
  onOpenLiveScorer: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
  selectedProductId: string | null;
  onResetSelection: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  apiStatus,
  activeModelVersions,
  onOpenLiveScorer,
  onRefresh,
  isRefreshing,
  selectedProductId,
  onResetSelection,
}) => {
  // Determine primary model version string to display
  const displayModel =
    activeModelVersions.length > 0
      ? activeModelVersions.join(' • ')
      : apiStatus.online
      ? "Mahsulot tanlanganda ko'rinadi"
      : "Gateway API ga ulanish kutilmoqda";

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-sm transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20 gap-4">
          {/* Brand Logo & Title */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={onResetSelection}>
            <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-gradient-to-br from-uzum-500 to-uzum-700 flex items-center justify-center text-white shadow-md shadow-uzum-500/20 ring-2 ring-uzum-400/30">
              <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl sm:text-2xl font-black tracking-tight text-slate-900">
                  uzum<span className="text-uzum-600">.ai</span>
                </span>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-uzum-50 text-uzum-700 border border-uzum-200">
                  Review Intelligence
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium hidden md:block">
                O'zbek tili uchun sun'iy intellekt tahlil platformasi
              </p>
            </div>
          </div>

          {/* Model Version Badge & Status Bar (MANDATORY REQUIREMENT) */}
          <div className="hidden lg:flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 border border-slate-200 text-xs font-medium text-slate-700 shadow-inner">
              <Bot className="w-4 h-4 text-uzum-600" />
              <span className="text-slate-500">Faol Model:</span>
              <span
                className="font-mono font-bold text-uzum-700 max-w-xs truncate"
                title={displayModel}
              >
                {displayModel}
              </span>
            </div>

            {/* Gateway Status Indicator */}
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-medium bg-white shadow-sm">
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  apiStatus.online
                    ? 'bg-emerald-500 shadow-sm shadow-emerald-500/50 animate-pulse'
                    : 'bg-rose-500'
                }`}
              />
              <span className="text-slate-600">
                {apiStatus.online ? 'Gateway Online' : 'Gateway Offline'}
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {selectedProductId && (
              <button
                onClick={onResetSelection}
                className="px-3 py-2 text-xs sm:text-sm font-semibold text-slate-700 hover:text-uzum-700 hover:bg-slate-100 rounded-lg transition"
              >
                ← Barcha mahsulotlar
              </button>
            )}

            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              title="Yangilash"
              className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-uzum-600' : ''}`} />
            </button>

            <button
              onClick={onOpenLiveScorer}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold text-white bg-gradient-to-r from-uzum-600 to-uzum-700 hover:from-uzum-700 hover:to-uzum-800 shadow-md shadow-uzum-500/25 active:scale-95 transition"
            >
              <Activity className="w-4 h-4" />
              <span>Jonli Tahlil</span>
            </button>
          </div>
        </div>

        {/* Mobile Model Version display banner */}
        <div className="lg:hidden py-1.5 px-2 flex items-center justify-between border-t border-slate-100 text-[11px] text-slate-600">
          <div className="flex items-center gap-1 font-mono truncate">
            <span className="font-semibold text-uzum-600">Model:</span>
            <span className="truncate max-w-[200px]">{displayModel}</span>
          </div>
          <span
            className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
              apiStatus.online ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
            }`}
          >
            {apiStatus.online ? 'Online' : 'Offline'}
          </span>
        </div>
      </div>
    </header>
  );
};
