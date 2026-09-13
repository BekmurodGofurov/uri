/**
 * Routing and URL helper utilities for SPA navigation.
 * Keeps browser address bar in sync with selected products,
 * supports direct links, refresh persistence, and history navigation.
 */

/**
 * Extracts product ID from current browser location.
 * Supports:
 * - Path formats: /products/:id or /product/:id
 * - Query parameter format: ?product=:id
 */
export function getProductIdFromUrl(): string | null {
  if (typeof window === 'undefined') return null;

  // 1. Check path format: /products/<id> or /product/<id>
  const pathname = window.location.pathname;
  const pathMatch = pathname.match(/^\/(?:products|product)\/([^/?#]+)/);
  if (pathMatch && pathMatch[1]) {
    return decodeURIComponent(pathMatch[1]);
  }

  // 2. Check query param: ?product=<id>
  const searchParams = new URLSearchParams(window.location.search);
  const queryProduct = searchParams.get('product');
  if (queryProduct && queryProduct.trim()) {
    return queryProduct.trim();
  }

  return null;
}

/**
 * Returns canonical product URL path.
 */
export function getProductUrl(productId: string): string {
  return `/products/${encodeURIComponent(productId)}`;
}

/**
 * Navigates to a specific product using HTML5 History API.
 */
export function navigateToProduct(productId: string): void {
  const targetUrl = getProductUrl(productId);
  if (window.location.pathname !== targetUrl) {
    window.history.pushState({ productId }, '', targetUrl);
  }
}

/**
 * Navigates back to the root catalog.
 */
export function navigateToHome(): void {
  if (window.location.pathname !== '/' || window.location.search) {
    window.history.pushState({ productId: null }, '', '/');
  }
}

/**
 * Checks if a mouse click event has modifier keys pressed (e.g. Cmd+Click, Ctrl+Click)
 * or is a non-primary mouse button (e.g. middle-click), which should trigger
 * default browser behavior (opening in new tab/window).
 */
export function isModifiedClick(event: React.MouseEvent<HTMLAnchorElement>): boolean {
  return (
    event.metaKey ||
    event.ctrlKey ||
    event.shiftKey ||
    event.altKey ||
    event.button !== 0
  );
}
