import React from 'react';
import { Star, MessageSquare, ArrowRight, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';
import { ProductListItem } from '../types/api';

interface ProductCardProps {
  product: ProductListItem;
  onSelect: (productId: string) => void;
  isSelected?: boolean;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onSelect,
  isSelected = false,
}) => {
  const { id, title, category, review_count, avg_rating, sentiment_summary } = product;

  // Calculate sentiment percentages
  const totalSentiments =
    (sentiment_summary?.positive || 0) +
    (sentiment_summary?.neutral || 0) +
    (sentiment_summary?.negative || 0);

  const posPct =
    totalSentiments > 0 ? Math.round(((sentiment_summary?.positive || 0) / totalSentiments) * 100) : 0;
  const neuPct =
    totalSentiments > 0 ? Math.round(((sentiment_summary?.neutral || 0) / totalSentiments) * 100) : 0;
  const negPct =
    totalSentiments > 0 ? 100 - posPct - neuPct : 0;

  return (
    <div
      onClick={() => onSelect(id)}
      className={`group relative bg-white rounded-2xl border transition-all duration-200 cursor-pointer overflow-hidden p-5 flex flex-col justify-between ${
        isSelected
          ? 'border-uzum-600 ring-2 ring-uzum-500/20 shadow-lg shadow-uzum-500/10'
          : 'border-slate-200 hover:border-uzum-300 hover:shadow-xl hover:shadow-slate-200/50 hover:-translate-y-0.5'
      }`}
    >
      <div>
        {/* Category & ID */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-700 uppercase tracking-wider">
            {category || 'Umumiy tovar'}
          </span>
          <span className="text-[11px] font-mono text-slate-400 font-medium truncate max-w-[120px]">
            {id}
          </span>
        </div>

        {/* Product Title */}
        <h3 className="font-bold text-slate-900 text-base leading-snug line-clamp-2 group-hover:text-uzum-700 transition">
          {title || `Mahsulot ${id}`}
        </h3>

        {/* Rating & Review Count */}
        <div className="flex items-center gap-4 mt-3 py-2 border-y border-slate-100 text-sm">
          <div className="flex items-center gap-1.5 font-bold text-slate-900">
            <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
            <span>{avg_rating !== null && avg_rating !== undefined ? avg_rating.toFixed(1) : '—'}</span>
            <span className="text-xs text-slate-400 font-normal">/ 5.0</span>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <MessageSquare className="w-4 h-4 text-slate-400" />
            <span>{review_count} ta sharh</span>
          </div>
        </div>

        {/* Sentiment Ratio Bar (Ijobiy / Neytral / Salbiy nisbati) */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs mb-1.5 font-semibold">
            <span className="text-slate-600">Kayfiyat nisbati:</span>
            <div className="flex items-center gap-2 text-[11px]">
              <span className="text-emerald-600 font-bold flex items-center gap-0.5">
                <ThumbsUp className="w-3 h-3" /> {posPct}%
              </span>
              <span className="text-amber-600 font-bold flex items-center gap-0.5">
                <Minus className="w-3 h-3" /> {neuPct}%
              </span>
              <span className="text-rose-600 font-bold flex items-center gap-0.5">
                <ThumbsDown className="w-3 h-3" /> {negPct}%
              </span>
            </div>
          </div>

          {/* Segmented Progress Bar */}
          <div className="h-2.5 w-full rounded-full bg-slate-100 overflow-hidden flex shadow-inner">
            <div
              style={{ width: `${posPct}%` }}
              className="bg-emerald-500 transition-all duration-500"
              title={`Ijobiy: ${sentiment_summary?.positive || 0} ta (${posPct}%)`}
            />
            <div
              style={{ width: `${neuPct}%` }}
              className="bg-amber-400 transition-all duration-500"
              title={`Neytral: ${sentiment_summary?.neutral || 0} ta (${neuPct}%)`}
            />
            <div
              style={{ width: `${negPct}%` }}
              className="bg-rose-500 transition-all duration-500"
              title={`Salbiy: ${sentiment_summary?.negative || 0} ta (${negPct}%)`}
            />
          </div>
        </div>
      </div>

      {/* Card Footer */}
      <div className="mt-5 pt-3 flex items-center justify-between text-xs font-semibold text-uzum-600 group-hover:text-uzum-700">
        <span>Tahlil va sharhlarni ko'rish</span>
        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
      </div>
    </div>
  );
};
