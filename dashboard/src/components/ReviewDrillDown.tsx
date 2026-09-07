import React, { useState } from 'react';
import { MessageSquare, Search, CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react';
import { ProductReviewItem, Sentiment } from '../types/api';
import { ReviewCard } from './ReviewCard';

interface ReviewDrillDownProps {
  reviews: ProductReviewItem[];
  total: number;
  selectedSentiment: Sentiment | 'all';
  onSentimentChange: (sentiment: Sentiment | 'all') => void;
  isLoading: boolean;
}

export const ReviewDrillDown: React.FC<ReviewDrillDownProps> = ({
  reviews,
  total,
  selectedSentiment,
  onSentimentChange,
  isLoading,
}) => {
  const [filterText, setFilterText] = useState('');

  const filteredReviews = reviews.filter((r) =>
    r.text.toLowerCase().includes(filterText.toLowerCase())
  );

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-uzum-50 text-uzum-600 border border-uzum-100">
            <MessageSquare className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-sm sm:text-base">
              Sharhlar drill-down va AI xulosalari
            </h3>
            <p className="text-xs text-slate-500">
              Xaridor sharhlarini o'qish va model tomonidan qo'yilgan belgilar
            </p>
          </div>
        </div>

        <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 w-fit">
          Jami: {total} ta sharh
        </span>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between border-y border-slate-100 py-3">
        {/* Sentiment Filter Tabs */}
        <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <button
            onClick={() => onSentimentChange('all')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
              selectedSentiment === 'all'
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <span>Barchasi</span>
          </button>

          <button
            onClick={() => onSentimentChange('positive')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
              selectedSentiment === 'positive'
                ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-600/20'
                : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Ijobiy</span>
          </button>

          <button
            onClick={() => onSentimentChange('neutral')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
              selectedSentiment === 'neutral'
                ? 'bg-amber-500 text-white shadow-sm shadow-amber-500/20'
                : 'bg-amber-50 text-amber-700 hover:bg-amber-100'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Neytral</span>
          </button>

          <button
            onClick={() => onSentimentChange('negative')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
              selectedSentiment === 'negative'
                ? 'bg-rose-600 text-white shadow-sm shadow-rose-600/20'
                : 'bg-rose-50 text-rose-700 hover:bg-rose-100'
            }`}
          >
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Salbiy</span>
          </button>
        </div>

        {/* Search inside reviews text */}
        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Sharh matnidan qidirish..."
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-uzum-500/20 focus:border-uzum-500 transition"
          />
        </div>
      </div>

      {/* Reviews List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((idx) => (
            <div
              key={idx}
              className="bg-slate-50 rounded-2xl border border-slate-100 p-5 h-32 animate-pulse"
            />
          ))}
        </div>
      ) : filteredReviews.length === 0 ? (
        <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-100">
          <p className="text-sm font-semibold text-slate-700">Hech qanday sharh topilmadi</p>
          <p className="text-xs text-slate-400 mt-1">
            Qidiruv so'zini yoki tanlangan kayfiyat filtrini o'zgartiring
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredReviews.map((review) => (
            <ReviewCard key={review.id} review={review} />
          ))}
        </div>
      )}
    </div>
  );
};
