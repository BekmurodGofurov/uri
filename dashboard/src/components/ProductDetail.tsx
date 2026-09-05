import React, { useState, useEffect, useRef } from 'react';
import {
  ArrowLeft,
  Star,
  MessageSquare,
  Bot,
  ThumbsUp,
  ThumbsDown,
  Minus,
  ShieldCheck,
} from 'lucide-react';
import {
  ProductDetailResponse,
  ProductReviewsResponse,
  Sentiment,
} from '../types/api';
import { fetchProductDetail, fetchProductReviews } from '../services/api';
import { SentimentChart } from './SentimentChart';
import { AspectBreakdown } from './AspectBreakdown';
import { ReviewDrillDown } from './ReviewDrillDown';

interface ProductDetailProps {
  productId: string;
  onBack: () => void;
  onUpdateActiveModels?: (models: string[]) => void;
}

export const ProductDetail: React.FC<ProductDetailProps> = ({
  productId,
  onBack,
  onUpdateActiveModels,
}) => {
  const [detail, setDetail] = useState<ProductDetailResponse | null>(null);
  const [reviewsData, setReviewsData] = useState<ProductReviewsResponse | null>(null);
  const [selectedSentiment, setSelectedSentiment] = useState<Sentiment | 'all'>('all');
  const [isLoadingDetail, setIsLoadingDetail] = useState(true);
  const [isLoadingReviews, setIsLoadingReviews] = useState(true);
  const [detailError, setDetailError] = useState<string | null>(null);

  const onUpdateActiveModelsRef = useRef(onUpdateActiveModels);
  useEffect(() => {
    onUpdateActiveModelsRef.current = onUpdateActiveModels;
  });

  // Load product detail
  useEffect(() => {
    let isMounted = true;
    setIsLoadingDetail(true);
    setDetailError(null);

    fetchProductDetail(productId)
      .then((data) => {
        if (isMounted) {
          setDetail(data);
          setIsLoadingDetail(false);
          if (data.active_model_versions) {
            onUpdateActiveModelsRef.current?.(data.active_model_versions);
          }
        }
      })
      .catch((err) => {
        if (isMounted) {
          setDetailError(err.message || "Tafsilotlarni yuklab bo'lmadi");
          setIsLoadingDetail(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [productId]);

  // Load product reviews with sentiment filter
  useEffect(() => {
    let isMounted = true;
    setIsLoadingReviews(true);

    const sentimentParam = selectedSentiment === 'all' ? undefined : selectedSentiment;
    fetchProductReviews(productId, { sentiment: sentimentParam })
      .then((data) => {
        if (isMounted) {
          setReviewsData(data);
          setIsLoadingReviews(false);
        }
      })
      .catch((err) => {
        console.error('Reviews loading error:', err);
        if (isMounted) {
          setIsLoadingReviews(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [productId, selectedSentiment]);

  if (detailError) {
    return (
      <div className="space-y-4">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-2 text-xs sm:text-sm font-bold text-slate-600 hover:text-uzum-600 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Barcha mahsulotlarga qaytish</span>
        </button>
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800">
          <p className="font-bold text-sm">Mahsulot ma'lumotlarini yuklab bo'lmadi</p>
          <p className="text-xs mt-1">{detailError}</p>
        </div>
      </div>
    );
  }

  if (isLoadingDetail || !detail) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-slate-200 rounded-lg w-48 animate-pulse" />
        <div className="bg-white rounded-2xl border border-slate-200 p-6 h-64 animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 h-80 animate-pulse" />
          <div className="bg-white rounded-2xl border border-slate-200 p-6 h-80 animate-pulse" />
        </div>
      </div>
    );
  }

  const {
    id,
    title,
    category,
    review_count,
    avg_rating,
    sentiment_summary,
    sentiment_over_time,
    aspect_breakdown,
    active_model_versions,
  } = detail;

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
    <div className="space-y-6">
      {/* Back button and breadcrumb */}
      <button
        onClick={onBack}
        className="inline-flex items-center gap-2 text-xs sm:text-sm font-bold text-slate-600 hover:text-uzum-600 transition group"
      >
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
        <span>Barcha mahsulotlarga qaytish</span>
      </button>

      {/* Top Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="space-y-1.5 flex-1">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-md text-xs font-semibold bg-slate-100 text-slate-700 uppercase tracking-wider">
                {category || 'Umumiy tovar'}
              </span>
              <span className="text-xs font-mono text-slate-400 font-medium">ID: {id}</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
              {title || `Mahsulot ${id}`}
            </h1>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center gap-4 bg-slate-50 p-3 rounded-2xl border border-slate-100 self-start lg:self-auto">
            <div className="px-3 text-center border-r border-slate-200">
              <div className="flex items-center justify-center gap-1 font-black text-lg text-slate-900">
                <Star className="w-5 h-5 fill-amber-400 text-amber-400" />
                <span>{avg_rating !== null && avg_rating !== undefined ? avg_rating.toFixed(1) : '—'}</span>
              </div>
              <span className="text-[11px] text-slate-500 font-medium">O'rtacha reyting</span>
            </div>

            <div className="px-3 text-center">
              <div className="flex items-center justify-center gap-1 font-black text-lg text-slate-900">
                <MessageSquare className="w-5 h-5 text-uzum-600" />
                <span>{review_count}</span>
              </div>
              <span className="text-[11px] text-slate-500 font-medium">Jami sharhlar</span>
            </div>
          </div>
        </div>

        {/* MANDATORY: Active AI Model Version Display Banner */}
        <div className="bg-gradient-to-r from-purple-50 via-indigo-50 to-purple-50 border border-uzum-200 rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-uzum-600 text-white shadow-sm">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                  Tahlil qiluvchi AI Modellar:
                </span>
                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-uzum-100 text-uzum-800">
                  <ShieldCheck className="w-3 h-3 mr-0.5 text-uzum-600" /> Verifikatsiya qilingan
                </span>
              </div>
              <p className="text-xs text-slate-600 font-medium mt-0.5">
                Ushbu tovarning barcha sharh va jihatlari quyidagi model versiyasi tomonidan qayta ishlangan
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {active_model_versions && active_model_versions.length > 0 ? (
              active_model_versions.map((version) => (
                <span
                  key={version}
                  className="px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-white text-uzum-700 border border-uzum-300 shadow-sm"
                >
                  {version}
                </span>
              ))
            ) : (
              <span className="px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-white text-uzum-700 border border-uzum-300 shadow-sm">
                uzum-sentiment-rubert-v1.2.0;uzum-aspect-xlm-v1.1.0
              </span>
            )}
          </div>
        </div>

        {/* High-Level Sentiment Stats Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-emerald-100 text-emerald-700">
                <ThumbsUp className="w-4 h-4" />
              </div>
              <div>
                <span className="text-xs text-emerald-800 font-medium">Ijobiy sharhlar</span>
                <div className="font-extrabold text-lg text-emerald-950">
                  {sentiment_summary?.positive || 0}{' '}
                  <span className="text-xs font-semibold font-mono">({posPct}%)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-amber-100 text-amber-700">
                <Minus className="w-4 h-4" />
              </div>
              <div>
                <span className="text-xs text-amber-800 font-medium">Neytral sharhlar</span>
                <div className="font-extrabold text-lg text-amber-950">
                  {sentiment_summary?.neutral || 0}{' '}
                  <span className="text-xs font-semibold font-mono">({neuPct}%)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-rose-50/70 border border-rose-200 rounded-xl p-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-rose-100 text-rose-700">
                <ThumbsDown className="w-4 h-4" />
              </div>
              <div>
                <span className="text-xs text-rose-800 font-medium">Salbiy sharhlar</span>
                <div className="font-extrabold text-lg text-rose-950">
                  {sentiment_summary?.negative || 0}{' '}
                  <span className="text-xs font-semibold font-mono">({negPct}%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Dynamic Charts & Aspect Breakdown Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SentimentChart data={sentiment_over_time} />
        <AspectBreakdown
          aspects={aspect_breakdown}
          activeModelVersions={active_model_versions}
        />
      </div>

      {/* Reviews Drill-down section */}
      <ReviewDrillDown
        reviews={reviewsData?.reviews || []}
        total={reviewsData?.total || 0}
        selectedSentiment={selectedSentiment}
        onSentimentChange={setSelectedSentiment}
        isLoading={isLoadingReviews}
      />
    </div>
  );
};
