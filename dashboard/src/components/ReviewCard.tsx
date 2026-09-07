import React from 'react';
import { Star, Bot, Sparkles, CheckCircle2, AlertCircle, HelpCircle, Tag } from 'lucide-react';
import { ProductReviewItem } from '../types/api';

interface ReviewCardProps {
  review: ProductReviewItem;
}

export const ReviewCard: React.FC<ReviewCardProps> = ({ review }) => {
  const { id, text, rating, created_at, prediction } = review;

  const formatDate = (isoStr: string) => {
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('uz-UZ', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return isoStr;
    }
  };

  const getSentimentBadge = (label?: string) => {
    switch (label) {
      case 'positive':
        return {
          text: 'Ijobiy',
          bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
          icon: CheckCircle2,
        };
      case 'negative':
        return {
          text: 'Salbiy',
          bg: 'bg-rose-50 text-rose-700 border-rose-200',
          icon: AlertCircle,
        };
      case 'neutral':
      default:
        return {
          text: 'Neytral',
          bg: 'bg-amber-50 text-amber-700 border-amber-200',
          icon: HelpCircle,
        };
    }
  };

  const sentimentInfo = prediction ? getSentimentBadge(prediction.sentiment_label) : null;
  const SentimentIcon = sentimentInfo?.icon;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-all space-y-4">
      {/* Top Header: Rating, Date & ID */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {/* Star rating */}
          <div className="flex items-center gap-0.5">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star
                key={star}
                className={`w-4 h-4 ${
                  rating && star <= rating
                    ? 'fill-amber-400 text-amber-400'
                    : 'text-slate-200 fill-slate-100'
                }`}
              />
            ))}
          </div>
          {rating && <span className="text-xs font-bold text-slate-700">{rating}.0</span>}
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 font-medium">
          <span>{formatDate(created_at)}</span>
          <span>•</span>
          <span className="font-mono text-[11px]">{id}</span>
        </div>
      </div>

      {/* Review Text */}
      <p className="text-slate-800 text-sm leading-relaxed font-normal bg-slate-50/50 p-3.5 rounded-xl border border-slate-100 italic">
        "{text}"
      </p>

      {/* AI Intelligence Block (AI xulosalari va MODEL_VERSION) */}
      {prediction ? (
        <div className="pt-3 border-t border-slate-100 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            {/* Sentiment label and confidence */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500">AI Xulosasi:</span>
              <div
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold border ${sentimentInfo?.bg}`}
              >
                {SentimentIcon && <SentimentIcon className="w-3.5 h-3.5" />}
                <span>{sentimentInfo?.text}</span>
                <span className="text-[10px] font-mono opacity-80">
                  ({Math.round((prediction.sentiment_confidence || 0) * 100)}%)
                </span>
              </div>
            </div>

            {/* MANDATORY: Model Version Tag */}
            <div
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-mono font-bold bg-purple-50 text-uzum-700 border border-uzum-200 shadow-sm"
              title="Ushbu xulosani chiqargan AI model versiyasi"
            >
              <Bot className="w-3.5 h-3.5 text-uzum-600 shrink-0" />
              <span className="text-uzum-500 font-sans font-semibold">Model:</span>
              <span className="truncate max-w-[240px]">{prediction.model_version}</span>
            </div>
          </div>

          {/* Aspect tags */}
          {prediction.aspects && prediction.aspects.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-xs text-slate-400 font-medium mr-1 flex items-center gap-1">
                <Tag className="w-3 h-3" /> Jihatlar:
              </span>
              {prediction.aspects.map((asp, idx) => {
                const isPos = asp.polarity === 'positive';
                const isNeg = asp.polarity === 'negative';
                return (
                  <span
                    key={idx}
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold border ${
                      isPos
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : isNeg
                        ? 'bg-rose-50 text-rose-700 border-rose-200'
                        : 'bg-amber-50 text-amber-700 border-amber-200'
                    }`}
                  >
                    <span className="capitalize">{asp.aspect}</span>
                    <span className="text-[9px] opacity-75">
                      ({isPos ? 'ijobiy' : isNeg ? 'salbiy' : 'neytral'})
                    </span>
                  </span>
                );
              })}
            </div>
          )}
        </div>
      ) : (
        <div className="pt-2 border-t border-slate-100 flex items-center gap-2 text-xs text-slate-400">
          <Sparkles className="w-3.5 h-3.5 text-slate-300" />
          <span>Ushbu sharh hali AI tomonidan baholanmagan</span>
        </div>
      )}
    </div>
  );
};
