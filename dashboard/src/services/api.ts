import {
  ProductListItem,
  ProductDetailResponse,
  ProductReviewsResponse,
  PreviewScoreResponse,
  Sentiment,
} from '../types/api';

export const BASE_URL = import.meta.env.VITE_API_URL || '';
export const DEFAULT_PRODUCT_ID = 'prod_1';

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
      error: errorMessage(err, 'Gateway API ga ulanib bo‘lmadi'),
    };
  }
}

export async function fetchProducts(): Promise<ProductListItem[]> {
  const res = await fetch(`${BASE_URL}/api/products`);
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Mahsulotlarni yuklashda xatolik (${res.status}): ${errText}`);
  }
  const data = await res.json();
  return Array.isArray(data) ? data : [];
}

export async function fetchProductDetail(productId: string): Promise<ProductDetailResponse> {
  const res = await fetch(`${BASE_URL}/api/products/${encodeURIComponent(productId)}`);
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Mahsulot tafsilotini yuklashda xatolik (${res.status}): ${errText}`);
  }
  return res.json();
}

export async function fetchProductReviews(
  productId: string,
  params?: { limit?: number; offset?: number; sentiment?: Sentiment }
): Promise<ProductReviewsResponse> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  if (params?.sentiment) query.set('sentiment', params.sentiment);

  const url = `${BASE_URL}/api/products/${encodeURIComponent(productId)}/reviews?${query.toString()}`;
  const res = await fetch(url);
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Sharhlarni yuklashda xatolik (${res.status}): ${errText}`);
  }
  return res.json();
}

export async function scoreReviewInteractive(
  reviewText: string,
  rating?: number,
  productId?: string
): Promise<PreviewScoreResponse> {
  const reqPayload = {
    reviews: [
      {
        text: reviewText,
        rating: rating ?? 5,
        product_id: productId || DEFAULT_PRODUCT_ID,
      },
    ],
  };

  const res = await fetch(`${BASE_URL}/api/score/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reqPayload),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Tahlil qilishda xatolik (${res.status}): ${errText}`);
  }

  return res.json();
}
