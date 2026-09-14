import React, { useState, useEffect } from 'react';
import { Search, Filter, Layers, SlidersHorizontal, ChevronLeft, ChevronRight } from 'lucide-react';
import { ProductListResponse } from '../types/api';
import { fetchProducts, errorMessage, ProductSortBy } from '../services/api';
import { ProductCard } from './ProductCard';

interface ProductListProps {
  selectedProductId: string | null;
  onSelectProduct: (id: string) => void;
}

const PAGE_SIZE = 18;
const SEARCH_DEBOUNCE_MS = 300;

/** First 2, last 2, and the current page with one neighbor on each side,
 *  with "…" filling any real gap (a single skipped page is shown directly
 *  instead of a "…"). E.g. page 10 of 327 -> 1 2 … 9 10 11 … 326 327. */
function getPageNumbers(current: number, total: number): (number | 'ellipsis')[] {
  const pages = new Set<number>([1, 2, total - 1, total, current - 1, current, current + 1]);
  const sorted = Array.from(pages)
    .filter((p) => p >= 1 && p <= total)
    .sort((a, b) => a - b);

  const result: (number | 'ellipsis')[] = [];
  let prev = 0;
  for (const p of sorted) {
    if (prev) {
      if (p - prev === 2) {
        result.push(prev + 1);
      } else if (p - prev > 2) {
        result.push('ellipsis');
      }
    }
    result.push(p);
    prev = p;
  }
  return result;
}

export const ProductList: React.FC<ProductListProps> = ({
  selectedProductId,
  onSelectProduct,
}) => {
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<ProductSortBy>('reviews');
  const [page, setPage] = useState(1);
  const [data, setData] = useState<ProductListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Debounce the raw search input before it drives a network request.
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchInput), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [searchInput]);

  // Any filter/sort change starts back at page 1.
  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, selectedCategory, sortBy]);

  // Fetch the current page from the gateway whenever a param changes.
  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    fetchProducts({
      page,
      pageSize: PAGE_SIZE,
      search: debouncedSearch || undefined,
      category: selectedCategory,
      sortBy,
    })
      .then((res) => {
        if (isMounted) {
          setData(res);
          setIsLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setError(errorMessage(err, 'Failed to load products'));
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [page, debouncedSearch, selectedCategory, sortBy]);

  const products = data?.items ?? [];
  const categories = data?.categories ?? [];
  const totalPages = data?.pagination.total_pages ?? 0;
  const totalCount = data?.pagination.total ?? 0;

  return (
    <div className="space-y-6">
      {/* Top Banner / Hero Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Product Catalog
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Analytical ratings, reviews, and AI insights for Uzum Market products
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-xl bg-uzum-50 border border-uzum-100 text-uzum-700 w-fit">
          <Layers className="w-4 h-4" />
          <span>Total: {totalCount} products</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm space-y-3 sm:space-y-0 sm:flex sm:items-center sm:justify-between sm:gap-4">
        {/* Search input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by product name or ID..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-uzum-500/20 focus:border-uzum-500 transition"
          />
        </div>

        <div className="flex items-center gap-3">
          {/* Category filter */}
          <div className="relative flex-1 sm:w-52">
            <Filter className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full pl-8 pr-8 py-2 text-xs font-medium bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-uzum-500/20 focus:border-uzum-500 appearance-none text-slate-700 cursor-pointer"
            >
              <option value="all">All categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Sort dropdown */}
          <div className="relative flex-1 sm:w-48">
            <SlidersHorizontal className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as ProductSortBy)}
              className="w-full pl-8 pr-8 py-2 text-xs font-medium bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-uzum-500/20 focus:border-uzum-500 appearance-none text-slate-700 cursor-pointer"
            >
              <option value="reviews">Most reviews</option>
              <option value="rating">Highest rating</option>
              <option value="positive">Most positive products</option>
            </select>
          </div>
        </div>
      </div>

      {/* Product Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[1, 2, 3, 4, 5, 6].map((idx) => (
            <div
              key={idx}
              className="bg-white rounded-2xl border border-slate-200 p-5 h-56 animate-pulse flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="h-4 bg-slate-200 rounded w-1/3" />
                <div className="h-5 bg-slate-200 rounded w-3/4" />
                <div className="h-4 bg-slate-100 rounded w-1/2" />
              </div>
              <div className="h-3 bg-slate-200 rounded-full w-full" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <p className="text-base font-semibold text-rose-600">{error}</p>
        </div>
      ) : products.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <p className="text-base font-semibold text-slate-700">No products found</p>
          <p className="text-xs text-slate-400 mt-1">
            Try adjusting your search query or selected category
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {products.map((prod) => (
              <ProductCard
                key={prod.id}
                product={prod}
                onSelect={onSelectProduct}
                isSelected={selectedProductId === prod.id}
              />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-1.5 pt-4 flex-wrap">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="p-2 rounded-xl bg-slate-100 text-slate-600 hover:bg-uzum-600 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-slate-100 disabled:hover:text-slate-600 transition"
                aria-label="Previous page"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              {getPageNumbers(page, totalPages).map((n, idx) =>
                n === 'ellipsis' ? (
                  <span
                    key={`ellipsis-${idx}`}
                    className="px-1.5 text-xs font-bold text-slate-400 select-none"
                  >
                    …
                  </span>
                ) : (
                  <button
                    key={n}
                    onClick={() => setPage(n)}
                    className={`min-w-[2.25rem] px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                      n === page
                        ? 'bg-uzum-600 text-white shadow-sm shadow-uzum-500/20'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {n}
                  </button>
                )
              )}

              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="p-2 rounded-xl bg-slate-100 text-slate-600 hover:bg-uzum-600 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-slate-100 disabled:hover:text-slate-600 transition"
                aria-label="Next page"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
