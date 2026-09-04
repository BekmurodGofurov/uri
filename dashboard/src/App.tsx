import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { ProductList } from './components/ProductList';
import { ProductDetail } from './components/ProductDetail';
import { LiveScorerModal } from './components/LiveScorerModal';
import { checkGatewayHealth, fetchProducts, ApiStatus } from './services/api';
import { ProductListItem } from './types/api';
import { ShieldCheck } from 'lucide-react';

export const App: React.FC = () => {
  const [products, setProducts] = useState<ProductListItem[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null);
  const [activeModelVersions, setActiveModelVersions] = useState<string[]>([]);
  const [apiStatus, setApiStatus] = useState<ApiStatus>({ online: false });
  const [isLiveScorerOpen, setIsLiveScorerOpen] = useState<boolean>(false);
  const [isLoadingProducts, setIsLoadingProducts] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Load products and health status
  const loadData = useCallback(async () => {
    setIsRefreshing(true);
    setApiError(null);
    try {
      const health = await checkGatewayHealth();
      setApiStatus(health);

      if (!health.online) {
        setApiError(
          "Gateway API ga ulanib bo'lmadi (http://localhost:8000). Iltimos, backend xizmatini ishga tushiring."
        );
      }

      const prods = await fetchProducts();
      setProducts(prods);
    } catch (e: any) {
      console.error('Failed to load dashboard data:', e);
      setApiError(e.message || "Mahsulotlarni Gateway API'dan yuklab bo'lmadi");
    } finally {
      setIsLoadingProducts(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    // Poll health periodically every 30s
    const interval = setInterval(async () => {
      const health = await checkGatewayHealth();
      setApiStatus(health);
    }, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleSelectProduct = (id: string) => {
    setSelectedProductId(id);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleResetSelection = () => {
    setSelectedProductId(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleUpdateActiveModels = useCallback((models: string[]) => {
    setActiveModelVersions((prev) => {
      if (prev.length === models.length && prev.every((m, i) => m === models[i])) {
        return prev;
      }
      return models;
    });
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-uzum-500 selection:text-white">
      {/* Top Navigation */}
      <Header
        apiStatus={apiStatus}
        activeModelVersions={activeModelVersions}
        onOpenLiveScorer={() => setIsLiveScorerOpen(true)}
        onRefresh={loadData}
        isRefreshing={isRefreshing}
        selectedProductId={selectedProductId}
        onResetSelection={handleResetSelection}
      />

      {/* Gateway Error / Warning Banner */}
      {apiError && (
        <div className="bg-amber-50 border-b border-amber-200 px-4 py-2.5 text-xs text-amber-900">
          <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
            <span className="font-semibold">{apiError}</span>
            <button
              onClick={loadData}
              className="px-2.5 py-1 rounded-md bg-amber-200/60 hover:bg-amber-200 text-amber-950 font-bold transition shrink-0"
            >
              Qayta urinish
            </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {selectedProductId ? (
          <ProductDetail
            productId={selectedProductId}
            onBack={handleResetSelection}
            onUpdateActiveModels={handleUpdateActiveModels}
          />
        ) : (
          <ProductList
            products={products}
            selectedProductId={selectedProductId}
            onSelectProduct={handleSelectProduct}
            isLoading={isLoadingProducts}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="font-black text-slate-900">uzum<span className="text-uzum-600">.ai</span></span>
            <span>—</span>
            <span>Uzum Review Intelligence Platform (URI)</span>
          </div>

          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1 font-mono">
              <ShieldCheck className="w-3.5 h-3.5 text-uzum-600" />
              Day 2-3 Milestone: React Dashboard + Gateway API
            </span>
          </div>
        </div>
      </footer>

      {/* Interactive Scoring Modal */}
      <LiveScorerModal
        isOpen={isLiveScorerOpen}
        onClose={() => setIsLiveScorerOpen(false)}
        productId={selectedProductId || products[0]?.id || 'uzum-phone-redmi13'}
        onSuccess={loadData}
      />
    </div>
  );
};

export default App;
