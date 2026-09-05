import React, { useState } from 'react';
import {
  X,
  Sparkles,
  Send,
  Bot,
  Star,
} from 'lucide-react';
import { DEFAULT_PRODUCT_ID, errorMessage, scoreReviewInteractive } from '../services/api';
import { PreviewItemResult } from '../types/api';

interface LiveScorerModalProps {
  isOpen: boolean;
  onClose: () => void;
  productId?: string;
  onSuccess?: () => void;
}

const PRESET_EXAMPLES = [
  {
    text: "Yetkazib berish vaqtida keldi, qadoqlash ham ajoyib. Narxi biroz qimmat lekin sifati a'lo darajada!",
    rating: 5,
  },
  {
    text: "Umuman yoqmadi, mahsulot sifati juda past va plastik hidi bor. Sotuvchi ham qo'ng'iroqqa javob bermadi.",
    rating: 1,
  },
  {
    text: "O'rtacha tovar, rangi rasmdagidan ozgina farq qiladi, lekin narxiga yarasha normal holat.",
    rating: 3,
  },
];

export const LiveScorerModal: React.FC<LiveScorerModalProps> = ({
  isOpen,
  onClose,
  productId = DEFAULT_PRODUCT_ID,
  onSuccess,
}) => {
  const [reviewText, setReviewText] = useState('');
  const [rating, setRating] = useState<number>(5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PreviewItemResult | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewText.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const resp = await scoreReviewInteractive(reviewText, rating, productId);
      if (resp.predictions && resp.predictions.length > 0) {
        setResult(resp.predictions[0]);
        if (onSuccess) onSuccess();
      }
    } catch (err: unknown) {
      setError(
        errorMessage(
          err,
          "Gateway API ga ulanishda xatolik yuz berdi. Backend ishlayotganligini tekshiring."
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectExample = (ex: { text: string; rating: number }) => {
    setReviewText(ex.text);
    setRating(ex.rating);
    setResult(null);
    setError(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-xl bg-white rounded-3xl border border-slate-200 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-gradient-to-r from-purple-50 to-white">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-uzum-600 text-white shadow-md shadow-uzum-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-900 text-base">Jonli AI Tahlil (Live Scorer)</h3>
              <p className="text-xs text-slate-500">
                Sharh yozing va Gateway ML xizmatlaridan natijani real vaqtda oling
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 max-h-[80vh] overflow-y-auto">
          {/* Quick preset examples */}
          <div>
            <span className="text-xs font-semibold text-slate-500 mb-2 block">
              Namunaviy o'zbekcha sharhlar:
            </span>
            <div className="flex flex-wrap gap-2">
              {PRESET_EXAMPLES.map((ex, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleSelectExample(ex)}
                  className="px-2.5 py-1 text-xs rounded-lg bg-slate-100 text-slate-700 hover:bg-uzum-50 hover:text-uzum-700 hover:border-uzum-200 border border-slate-200 transition font-medium text-left line-clamp-1 max-w-xs"
                >
                  {ex.rating}★: {ex.text.substring(0, 38)}...
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Rating selector */}
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-slate-700">Baholash:</span>
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    className="p-1 hover:scale-110 transition-transform"
                  >
                    <Star
                      className={`w-5 h-5 ${
                        star <= rating
                          ? 'fill-amber-400 text-amber-400'
                          : 'text-slate-200 fill-slate-100'
                      }`}
                    />
                  </button>
                ))}
              </div>
              <span className="text-xs font-mono font-bold text-slate-700">{rating} yulduz</span>
            </div>

            {/* Textarea */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Sharh matni (O'zbek tilida):
              </label>
              <textarea
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
                placeholder="Masalan: Mahsulot sifati juda ajoyib, yetkazib berish ham tez bo'ldi..."
                rows={4}
                className="w-full p-3.5 text-sm bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-uzum-500/20 focus:border-uzum-500 transition resize-none"
              />
            </div>

            {error && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 font-medium">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || !reviewText.trim()}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-uzum-600 to-uzum-700 hover:from-uzum-700 hover:to-uzum-800 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-uzum-500/20 transition active:scale-[0.99]"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>AI xizmatlari tahlil qilmoqda...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Gateway orqali tahlil qilish</span>
                </>
              )}
            </button>
          </form>

          {/* AI Result Card */}
          {result && (
            <div className="p-4 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 text-white shadow-xl space-y-3 animate-fade-in">
              <div className="flex items-center justify-between border-b border-slate-700 pb-2.5">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-uzum-400" />
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                    AI Tahlil Natijasi
                  </span>
                </div>

                {/* MANDATORY: model_version tag in prediction */}
                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-lg bg-slate-800 border border-slate-700 text-[11px] font-mono text-uzum-300">
                  <Bot className="w-3.5 h-3.5 text-uzum-400" />
                  <span className="text-[10px] text-slate-400">Model:</span>
                  <span className="font-bold truncate max-w-[180px]">{result.model_version}</span>
                </div>
              </div>

              {/* Sentiment outcome */}
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Kayfiyat:</span>
                <span
                  className={`px-2.5 py-1 rounded-lg text-xs font-extrabold uppercase ${
                    result.sentiment_label === 'positive'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : result.sentiment_label === 'negative'
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  }`}
                >
                  {result.sentiment_label === 'positive'
                    ? 'Ijobiy'
                    : result.sentiment_label === 'negative'
                    ? 'Salbiy'
                    : 'Neytral'}{' '}
                  ({Math.round(result.sentiment_confidence * 100)}%)
                </span>
              </div>

              {/* Aspects outcome */}
              <div>
                <span className="text-xs text-slate-400 block mb-1.5">Aniqlangan jihatlar:</span>
                {result.aspects && result.aspects.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {result.aspects.map((asp, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded-md text-xs font-mono bg-slate-800 border border-slate-700 text-slate-200"
                      >
                        {asp.aspect}: <strong className="text-uzum-300">{asp.polarity}</strong>
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-xs text-slate-500 italic">Jihatlar topilmadi</span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
