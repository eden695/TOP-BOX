import React, { useState, useEffect } from 'react';
import { usePOS } from '../context/POSContext';
import { Calculator, AlertTriangle, Clock, ShieldCheck, UserCheck } from 'lucide-react';

export const Header: React.FC = () => {
  const {
    settings,
    quickAlertsCount,
    setCurrentPage,
    currentUser,
    isCalculatorVisible,
    setIsCalculatorVisible,
  } = usePOS();
  const [timeStr, setTimeStr] = useState<string>('');
  const [dateStr, setDateStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
      setDateStr(now.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 px-6 flex items-center justify-between shrink-0 select-none">
      {/* Left: Register & Active Status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-xs font-semibold text-slate-200">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>{settings.register}</span>
        </div>
        <div className="hidden md:flex items-center gap-2 text-xs text-slate-400 capitalize">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{dateStr}</span>
          <span className="font-mono font-bold text-slate-200 bg-slate-800 px-2 py-0.5 rounded">{timeStr}</span>
        </div>
      </div>

      {/* Right: Quick Tools & Alerts */}
      <div className="flex items-center gap-3">
        {/* Low Stock Alert Button */}
        {quickAlertsCount.lowStock > 0 && (
          <button
            onClick={() => setCurrentPage('products')}
            title="Articles en rupture ou stock critique"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/15 text-amber-300 border border-amber-500/30 text-xs font-bold hover:bg-amber-500/25 transition-all cursor-pointer"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>{quickAlertsCount.lowStock} Alerte{quickAlertsCount.lowStock > 1 ? 's' : ''} Stock</span>
          </button>
        )}

        {/* Integrated Calculator Toggle */}
        <button
          onClick={() => setIsCalculatorVisible((prev) => !prev)}
          title="Afficher/Masquer la calculatrice intégrée"
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all cursor-pointer ${
            isCalculatorVisible
              ? 'bg-blue-600 text-white border-blue-500 shadow-sm shadow-blue-500/20'
              : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
          }`}
        >
          <Calculator className="w-4 h-4 text-sky-400" />
          <span className="hidden sm:inline">Calculatrice Intégrée</span>
        </button>

        {/* Cashier Session Quick Switch */}
        <button
          onClick={() => setCurrentPage('users')}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold transition-all cursor-pointer"
          title="Changer de session de caissier"
        >
          <UserCheck className="w-4 h-4 text-emerald-400" />
          <span className="hidden md:inline">{currentUser?.fullName || 'Caissier'}</span>
          <span className="text-[10px] text-sky-400 font-mono">({currentUser?.role || 'Session'})</span>
        </button>
      </div>
    </header>
  );
};
