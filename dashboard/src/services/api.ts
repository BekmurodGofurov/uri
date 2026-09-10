import {
  ProductListItem,
  ProductDetailResponse,
  ProductReviewsResponse,
  PreviewScoreResponse,
  Sentiment,
} from '../types/api';

const rawApiUrl = import.meta.env.VITE_API_URL;

if (!rawApiUrl || !rawApiUrl.trim()) {
  console.error(
    "[URI Dashboard] XATOLIK: VITE_API_URL .env faylida ko'rsatilmagan! " +
    "Iltimos, dashboard/.env faylida VITE_API_URL=http://localhost:8000 deb belgilang."
  );
}

export const BASE_URL = (rawApiUrl || '').trim().replace(/\/+$/, '');
export const DEFAULT_PRODUCT_ID = 'prod_1';

export function requireApiUrl(): string {
  if (!BASE_URL) {
    throw new Error(
      "VITE_API_URL belgilanmagan! Iltimos, dashboard/.env faylida VITE_API_URL ni ko'rsating " +
      "(masalan: VITE_API_URL=http://localhost:8000)."
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
      error: "VITE_API_URL .env faylida belgilanmagan! dashboard/.env faylini tekshiring.",
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
      error: errorMessage(err, 'Gateway API ga ulanib bo‘lmadi'),
    };
  }
}

export async function fetchProducts(): Promise<ProductListItem[]> {
  const baseUrl = requireApiUrl();
  const res = await fetch(`${baseUrl}/api/products`);
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Mahsulotlarni yuklashda xatolik (${res.status}): ${errText}`);
  }
  const data = await res.json();
  return Array.isArray(data) ? data : [];
}

export async function fetchProductDetail(productId: string): Promise<ProductDetailResponse> {
  const baseUrl = requireApiUrl();
  const res = await fetch(`${baseUrl}/api/products/${encodeURIComponent(productId)}`);
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
  const baseUrl = requireApiUrl();
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.offset) query.set('offset', String(params.offset));
  if (params?.sentiment) query.set('sentiment', params.sentiment);

  const url = `${baseUrl}/api/products/${encodeURIComponent(productId)}/reviews?${query.toString()}`;
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
    throw new Error(`Tahlil qilishda xatolik (${res.status}): ${errText}`);
  }

  return res.json();
}
