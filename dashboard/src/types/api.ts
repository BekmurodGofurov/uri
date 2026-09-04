export type Sentiment = 'positive' | 'neutral' | 'negative';

export interface SentimentSummary {
  positive: number;
  neutral: number;
  negative: number;
}

export interface ProductListItem {
  id: string;
  title: string | null;
  category: string | null;
  review_count: number;
  avg_rating: number | null;
  sentiment_summary: SentimentSummary;
}

export interface AspectPolaritySummary {
  aspect: string;
  positive: number;
  neutral: number;
  negative: number;
  total: number;
}

export interface SentimentTimePoint {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
}

export interface ProductDetailResponse {
  id: string;
  title: string | null;
  category: string | null;
  review_count: number;
  avg_rating: number | null;
  sentiment_summary: SentimentSummary;
  sentiment_over_time: SentimentTimePoint[];
  aspect_breakdown: AspectPolaritySummary[];
  active_model_versions: string[];
}

export interface AspectHit {
  aspect: string;
  polarity: Sentiment;
  confidence?: number;
}

export interface ReviewPredictionItem {
  id: number;
  sentiment_label: Sentiment;
  sentiment_confidence: number;
  aspects: AspectHit[];
  model_version: string;
  created_at: string;
}

export interface ProductReviewItem {
  id: string;
  text: string;
  rating: number | null;
  created_at: string;
  prediction: ReviewPredictionItem | null;
}

export interface ProductReviewsResponse {
  product_id: string;
  total: number;
  limit: number;
  offset: number;
  reviews: ProductReviewItem[];
}

export interface ScoreItemRequest {
  id: string;
  text: string;
  rating?: number;
  product_id?: string;
}

export interface ScoreItemResult {
  id: number;
  review_id: string;
  sentiment_label: Sentiment;
  sentiment_confidence: number;
  aspects: AspectHit[];
  model_version: string;
}

export interface GatewayScoreResponse {
  scored_count: number;
  predictions: ScoreItemResult[];
}

export interface HealthResponse {
  status: string;
  service: string;
  model_version?: string;
}
