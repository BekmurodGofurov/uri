import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Activity, Info } from 'lucide-react';
import { isModifiedClick } from '../utils/route';

interface HeaderProps {
  onOpenLiveScorer: () => void;
  onResetSelection: () => void;
  isAboutPage: boolean;
  onNavigateAbout: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenLiveScorer,
  onResetSelection,
  isAboutPage,
  onNavigateAbout,
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isHovered, setIsHovered] = useState(false);
  const lastScrollYRef = useRef(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearTimer = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  useEffect(() => {
    lastScrollYRef.current = window.scrollY;
    // Eng tepada doimiy ko'rinadi
    if (window.scrollY <= 20) {
      setIsVisible(true);
    }

    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const lastScrollY = lastScrollYRef.current;
      const diff = currentScrollY - lastScrollY;

      // 1. Eng tepada (scrollY <= 20): doimiy turadi, umuman yo'q bo'lmaydi
      if (currentScrollY <= 20) {
        clearTimer();
        setIsVisible(true);
        lastScrollYRef.current = currentScrollY;
        return;
      }

      // 2. Pastga scroll qilayotganda: darhol yo'q bo'ladi
      if (diff > 5) {
        clearTimer();
        setIsVisible(false);
      }
      // 3. Tepaga scroll qilayotganda: paydo bo'ladi
      else if (diff < -5) {
        setIsVisible(true);
        clearTimer();
        // O'zining eng tepa joyiga hali yetmagan bo'lsa, 3 sekunddan keyin yana yashirinadi
        timeoutRef.current = setTimeout(() => {
          setIsVisible(false);
        }, 3000);
      }

      lastScrollYRef.current = currentScrollY;
    };

    const handleMouseMove = (e: MouseEvent) => {
      // Sichqoncha eng tepaga (36px ichiga) borsa, headerni ochish
      if (e.clientY <= 36) {
        setIsVisible(true);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('mousemove', handleMouseMove, { passive: true });

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('mousemove', handleMouseMove);
      clearTimer();
    };
  }, []);

  // Sahifa almashganda yoki yuqoriga qaytganda headerni ko'rsatish
  useEffect(() => {
    if (window.scrollY <= 20) {
      clearTimer();
      setIsVisible(true);
    }
  }, [isAboutPage]);

  const shouldShow = isVisible || isHovered;

  const handleHomeClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (isModifiedClick(e)) return;
    e.preventDefault();
    onResetSelection();
  };

  const handleAboutClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (isModifiedClick(e)) return;
    e.preventDefault();
    onNavigateAbout();
  };

  return (
    <header
      onMouseEnter={() => {
        setIsHovered(true);
        clearTimer();
      }}
      onMouseLeave={() => {
        setIsHovered(false);
        // Agar eng tepada bo'lmasa, sichqoncha ketgach 3s timer bilan yashirish
        if (window.scrollY > 20) {
          clearTimer();
          timeoutRef.current = setTimeout(() => {
            setIsVisible(false);
          }, 3000);
        }
      }}
      className={`fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm transition-all duration-300 ease-in-out ${
        shouldShow
          ? 'translate-y-0 opacity-100 pointer-events-auto'
          : '-translate-y-full opacity-0 pointer-events-none'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20 gap-4">
          {/* Left: Brand Logo & Subtitle */}
          <a
            href="/"
            onClick={handleHomeClick}
            className="flex items-center space-x-3 cursor-pointer text-inherit no-underline"
          >
            <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-gradient-to-br from-uzum-500 to-uzum-700 flex items-center justify-center text-white shadow-md shadow-uzum-500/20 ring-2 ring-uzum-400/30">
              <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 animate-pulse" />
            </div>
            <div>
              <span className="text-xl sm:text-2xl font-black tracking-tight text-slate-900 block leading-tight">
                uzum<span className="text-uzum-600">.ai</span>
              </span>
              <p className="text-xs text-slate-500 font-medium hidden sm:block">
                AI Review Intelligence Platform for Uzbek Language
              </p>
            </div>
          </a>

          {/* Right: About Link & Live Scorer Button */}
          <div className="flex items-center space-x-3 sm:space-x-4">
            <a
              href="/about"
              onClick={handleAboutClick}
              className={`px-3 py-2 text-xs sm:text-sm font-semibold rounded-xl transition inline-flex items-center gap-1.5 ${
                isAboutPage
                  ? 'bg-uzum-50 text-uzum-700 font-bold border border-uzum-200 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Info className="w-4 h-4" />
              <span>About</span>
            </a>

            <button
              onClick={onOpenLiveScorer}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold text-white bg-gradient-to-r from-uzum-600 to-uzum-700 hover:from-uzum-700 hover:to-uzum-800 shadow-md shadow-uzum-500/25 active:scale-95 transition"
            >
              <Activity className="w-4 h-4" />
              <span>Live Scorer</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
