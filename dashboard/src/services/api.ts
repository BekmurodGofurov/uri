import {
  ProductListResponse,
  ProductDetailResponse,
  ProductReviewsResponse,
  PreviewScoreResponse,
  Sentiment,
} from '../types/api';

export type ProductSortBy = 'reviews' | 'rating' | 'positive';

const rawApiUrl = import.meta.env.VITE_API_URL;

if (!rawApiUrl || !rawApiUrl.trim()) {
  console.error(
    "[URI Dashboard] ERROR: VITE_API_URL is not set in .env file! " +
    "Please specify VITE_API_URL in dashboard/.env (e.g. http://<host>:<port>)."
  );
}

export const BASE_URL = (rawApiUrl || '').trim().replace(/\/+$/, '');
export const DEFAULT_PRODUCT_ID = 'prod_1';

export function requireApiUrl(): string {
  if (!BASE_URL) {
    throw new Error(
      "VITE_API_URL is not specified! Please set VITE_API_URL in dashboard/.env."
    );
  }

  return BASE_URL;
}

export function errorMessage(err: unknown, fallback: string): string {
  if (err instanceof Error) return err.message;
  if (typeof err === 'string') return err;
  return fallback;
}

export interface ApiStatus {
  online: boolean;
  service?: string;
  error?: string;
}

export async function checkGatewayHealth(): Promise<ApiStatus> {
  if (!BASE_URL) {
    return {
      online: false,
      error: "VITE_API_URL is not specified in .env file! Please check dashboard/.env.",
    };
  }
  try {
    const res = await fetch(`${BASE_URL}/api/health`, {
      headers: { Accept: 'application/json' },
    });
    if (res.ok) {
      const data = await res.json();
      return {
        online: true,
        service: data.service,
      };
    }
    return {
      online: false,
      error: `Gateway status error: ${res.status}`,
    };
  } catch (err: unknown) {
    return {
      online: false,
      error: errorMessage(err, 'Failed to connect to Gateway API'),
    };
  }
}

export async function fetchProducts(params?: {
  page?: number;
  pageSize?: number;
  search?: string;
  category?: string;
  sortBy?: ProductSortBy;
}): Promise<ProductListResponse> {
  const baseUrl = requireApiUrl();
  const query = new URLSearchParams();
  if (params?.page) query.set('page', String(params.page));
  if (params?.pageSize) query.set('page_size', String(params.pageSize));
  if (params?.search) query.set('search', params.search);
  if (params?.category && params.category !== 'all') query.set('category', params.category);
  if (params?.sortBy) query.set('sort_by', params.sortBy);

  const res = await fetch(`${baseUrl}/api/products?${query.toString()}`);
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Failed to load products (${res.status}): ${errText}`);
  }
  return res.json();
}

export async function fetchProductDetail(productId: string): Promise<ProductDetailResponse> {
  const baseUrl = requireApiUrl();
  const res = await fetch(`${baseUrl}/api/products/${encodeURIComponent(productId)}`);
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Failed to load product details (${res.status}): ${errText}`);
  }
  return res.json();
}

export async function fetchProductReviews(
  productId: string,
  params?: { limit?: number; offset?: number; sentiment?: Sentiment }
): Promise<ProductReviewsResponse> {
  const baseUrl = requireApiUrl();
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  if (params?.sentiment) query.set('sentiment', params.sentiment);

  const url = `${baseUrl}/api/products/${encodeURIComponent(productId)}/reviews?${query.toString()}`;
  const res = await fetch(url);
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Failed to load reviews (${res.status}): ${errText}`);
  }
  return res.json();
}

export async function scoreReviewInteractive(
  reviewText: string,
  rating?: number,
  productId?: string
): Promise<PreviewScoreResponse> {
  const baseUrl = requireApiUrl();
  const reqPayload = {
    reviews: [
      {
        text: reviewText,
        rating: rating ?? 5,
        product_id: productId || DEFAULT_PRODUCT_ID,
      },
    ],
  };

  const res = await fetch(`${baseUrl}/api/score/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reqPayload),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Scoring failed (${res.status}): ${errText}`);
  }

  return res.json();
}
