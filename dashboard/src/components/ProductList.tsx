import React, { useState, useMemo } from 'react';
import { Search, Filter, Layers, SlidersHorizontal } from 'lucide-react';
import { ProductListItem } from '../types/api';
import { ProductCard } from './ProductCard';

interface ProductListProps {
  products: ProductListItem[];
  selectedProductId: string | null;
  onSelectProduct: (id: string) => void;
  isLoading: boolean;
}

export const ProductList: React.FC<ProductListProps> = ({
  products,
  selectedProductId,
  onSelectProduct,
  isLoading,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'reviews' | 'rating' | 'positive'>('reviews');
  const [visibleCount, setVisibleCount] = useState(36);

  React.useEffect(() => {
    setVisibleCount(36);
  }, [searchQuery, selectedCategory, sortBy]);

  // Extract unique categories
  const categories = useMemo(() => {
    const cats = new Set<string>();
    products.forEach((p) => {
      if (p.category) cats.add(p.category);
    });
    return Array.from(cats);
  }, [products]);

  // Filter and sort products
  const filteredProducts = useMemo(() => {
    return products
      .filter((p) => {
        const matchesSearch =
          (p.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.id.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesCat = selectedCategory === 'all' || p.category === selectedCategory;
        return matchesSearch && matchesCat;
      })
      .sort((a, b) => {
        if (sortBy === 'reviews') {
          return b.review_count - a.review_count;
        }
        if (sortBy === 'rating') {
          return (b.avg_rating || 0) - (a.avg_rating || 0);
        }
        if (sortBy === 'positive') {
          const aTotal =
            (a.sentiment_summary?.positive || 0) +
            (a.sentiment_summary?.neutral || 0) +
            (a.sentiment_summary?.negative || 0);
          const aPos = aTotal > 0 ? (a.sentiment_summary?.positive || 0) / aTotal : 0;

          const bTotal =
            (b.sentiment_summary?.positive || 0) +
            (b.sentiment_summary?.neutral || 0) +
            (b.sentiment_summary?.negative || 0);
          const bPos = bTotal > 0 ? (b.sentiment_summary?.positive || 0) / bTotal : 0;

          return bPos - aPos;
        }
        return 0;
      });
  }, [products, searchQuery, selectedCategory, sortBy]);

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
          <span>Total: {products.length} products</span>
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
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
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
              onChange={(e) => setSortBy(e.target.value as any)}
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
      ) : filteredProducts.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <p className="text-base font-semibold text-slate-700">No products found</p>
          <p className="text-xs text-slate-400 mt-1">
            Try adjusting your search query or selected category
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredProducts.slice(0, visibleCount).map((prod) => (
              <ProductCard
                key={prod.id}
                product={prod}
                onSelect={onSelectProduct}
                isSelected={selectedProductId === prod.id}
              />
            ))}
          </div>

          {visibleCount < filteredProducts.length && (
            <div className="text-center pt-4">
              <button
                onClick={() => setVisibleCount((prev) => prev + 36)}
                className="px-6 py-2.5 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 font-semibold text-xs rounded-xl shadow-sm hover:shadow transition"
              >
                Show more ({filteredProducts.length - visibleCount} remaining)
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
