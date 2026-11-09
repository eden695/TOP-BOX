import React from 'react';
import { usePOS } from '../context/POSContext';
import { EmbeddedCalculator } from './EmbeddedCalculator';
import {
  TrendingUp,
  Receipt,
  Package,
  AlertTriangle,
  ArrowUpRight,
  ShoppingCart,
  CalendarCheck,
  CheckCircle2,
  Banknote,
  Smartphone,
  Calendar,
  Layers,
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const {
    sales,
    products,
    formatMoney,
    settings,
    setCurrentPage,
    adjustStock,
    isCalculatorVisible,
    setIsCalculatorVisible,
  } = usePOS();

  const now = new Date();
  const todayStr = now.toISOString().substring(0, 10);
  const currentMonthPrefix = now.toISOString().substring(0, 7);

  const safeSales = Array.isArray(sales) ? sales : [];
  const safeProducts = Array.isArray(products) ? products : [];

  const todaySales = safeSales.filter((s) => s && s.date && String(s.date).startsWith(todayStr));
  const monthSales = safeSales.filter((s) => s && s.date && String(s.date).startsWith(currentMonthPrefix));

  // Revenue computations
  const totalRevenueToday = todaySales.reduce((acc, s) => acc + (Number(s.total) || 0), 0);
  const salesCountToday = todaySales.length;
  const avgBasketToday = salesCountToday > 0 ? totalRevenueToday / salesCountToday : 0;

  // Breakdown by payment method today (Cash vs Mobile Money Congo)
  const cashSalesToday = todaySales
    .filter((s) => s && s.payment_method === 'CASH')
    .reduce((acc, s) => acc + (Number(s.total) || 0), 0);

  const momoSalesToday = todaySales
    .filter((s) => s && (s.payment_method === 'MOMO_CONGO' || s.payment_method === 'AIRTEL_CONGO'))
    .reduce((acc, s) => acc + (Number(s.total) || 0), 0);

  const totalRevenueMonth = monthSales.reduce((acc, s) => acc + (Number(s.total) || 0), 0);

  const threshold = Number(settings?.stock_threshold) || 5;
  const lowStockProducts = safeProducts.filter((p) => p && (Number(p.qty) || 0) <= threshold);
  const outOfStockProducts = safeProducts.filter((p) => p && (Number(p.qty) || 0) <= 0);

  // Past 7 days analytics calculation
  const last7Days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (6 - i));
    const dayKey = d.toISOString().substring(0, 10);
    const dayName = d.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric' });
    const daySales = sales.filter((s) => s.date.startsWith(dayKey));
    const revenue = daySales.reduce((acc, s) => acc + s.total, 0);
    const count = daySales.length;
    return { dayKey, dayName, revenue, count };
  });

  const weekRevenue = last7Days.reduce((acc, d) => acc + d.revenue, 0);
  const maxRevenue = Math.max(...last7Days.map((d) => d.revenue), 10000);

  // Top 5 selling products across all sales
  const salesCountMap: { [prodName: string]: { qty: number; revenue: number } } = {};
  sales.forEach((s) => {
    s.items.forEach((it) => {
      if (!salesCountMap[it.name]) {
        salesCountMap[it.name] = { qty: 0, revenue: 0 };
      }
      salesCountMap[it.name].qty += it.qty;
      salesCountMap[it.name].revenue += it.total;
    });
  });

  const topSelling = Object.entries(salesCountMap)
    .map(([name, data]) => ({ name, ...data }))
    .sort((a, b) => b.qty - a.qty)
    .slice(0, 5);

  const maxSoldQty = Math.max(...topSelling.map((t) => t.qty), 1);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            Tableau de Bord
          </h1>
          <p className="text-sm text-slate-400">
            Suivi des encaissements en direct, trésorerie et rentabilité du magasin.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentPage('pos')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-black text-sm shadow-lg shadow-blue-600/30 transition-all cursor-pointer"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Ouvrir la Caisse</span>
          </button>
          <button
            onClick={() => setCurrentPage('closings')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-sm border border-slate-700 transition-all cursor-pointer"
          >
            <CalendarCheck className="w-4 h-4 text-emerald-400" />
            <span>Clôture Z</span>
          </button>
        </div>
      </div>

      {/* =========================================================================
          ZONE MAJEURE HAUTE VISIBILITÉ : CHIFFRE D'AFFAIRES & TRÉSORERIE EN DIRECT
         ========================================================================= */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/70 border-2 border-blue-500/40 rounded-3xl p-6 sm:p-7 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 space-y-6">
          {/* Header of Revenue section */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-600 to-sky-400 flex items-center justify-center shadow-lg shadow-blue-500/30 text-white">
                <TrendingUp className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[11px] font-black uppercase tracking-widest text-sky-400">
                  RECETTES & ENCAISSEMENTS DU JOUR
                </span>
                <h2 className="text-lg font-black text-white">
                  Chiffre d’Affaires Réalisé (Aujourd’hui)
                </h2>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-300 text-xs font-bold border border-emerald-500/30">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span>En direct • {salesCountToday} vente{salesCountToday > 1 ? 's' : ''}</span>
              </span>
            </div>
          </div>

          {/* Big Hero Number & Method Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            {/* Primary Gigantic Metric */}
            <div className="lg:col-span-6 space-y-2">
              <div className="text-4xl sm:text-5xl lg:text-6xl font-black text-white font-mono tracking-tight drop-shadow-md">
                {formatMoney(totalRevenueToday)}
              </div>
              <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-slate-300 pt-1">
                <span>
                  Panier moyen : <strong className="text-sky-300 font-mono font-bold">{formatMoney(avgBasketToday)}</strong>
                </span>
                <span>•</span>
                <span>
                  Articles vendus aujourd’hui : <strong className="text-emerald-300 font-bold">
                    {todaySales.reduce((acc, s) => acc + s.items.reduce((a, b) => a + b.qty, 0), 0)} unités
                  </strong>
                </span>
              </div>
            </div>

            {/* Trésorerie Breakdown: Espèces vs Mobile Money Congo */}
            <div className="lg:col-span-6 grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {/* Espèces (Cash) */}
              <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800/80 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400 mb-1">
                    <Banknote className="w-4 h-4" />
                    <span>Espèces (Tiroir Cash)</span>
                  </div>
                  <div className="text-xl font-black text-white font-mono">
                    {formatMoney(cashSalesToday)}
                  </div>
                  <span className="text-[10px] text-slate-400 font-medium">
                    {totalRevenueToday > 0 ? `${Math.round((cashSalesToday / totalRevenueToday) * 100)}% des recettes` : '0%'}
                  </span>
                </div>
              </div>

              {/* Mobile Money Congo (MTN & Airtel) */}
              <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800/80 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-1.5 text-xs font-bold text-sky-400 mb-1">
                    <Smartphone className="w-4 h-4" />
                    <span>Mobile Money Congo</span>
                  </div>
                  <div className="text-xl font-black text-white font-mono">
                    {formatMoney(momoSalesToday)}
                  </div>
                  <span className="text-[10px] text-slate-400 font-medium">
                    MTN MoMo (*105#) & Airtel (*128#)
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Sub-strip: Weekly & Monthly Comparison */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 border-t border-slate-800/70 text-xs">
            <div className="flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400 font-medium">Semaine en cours (7j) :</span>
              <strong className="text-white font-mono font-bold text-sm">{formatMoney(weekRevenue)}</strong>
            </div>
            <div className="flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400 font-medium">Mois en cours :</span>
              <strong className="text-white font-mono font-bold text-sm">{formatMoney(totalRevenueMonth)}</strong>
            </div>
            <div className="flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400 font-medium">Articles au catalogue :</span>
              <strong className="text-sky-300 font-bold text-sm">{products.length} références</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Flex container showing Dashboard sections + Optional Embedded Calculator */}
      <div className="flex flex-col lg:flex-row gap-6 items-start">
        <div className="flex-1 space-y-6 min-w-0 w-full">
          {/* Main Grid: 7-Day Chart & Top Sellers */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Cols: 7-Day Revenue Bar Chart */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-base font-bold text-white">Chiffre d’affaires des 7 derniers jours</h3>
                  <p className="text-xs text-slate-400">Évolution journalière des encaissements</p>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="w-3 h-3 rounded bg-blue-500 inline-block" />
                  <span>Chiffre net ({settings.currency})</span>
                </div>
              </div>

              {/* Responsive Bar Chart */}
              <div className="h-60 flex items-end justify-between gap-3 pt-6 border-b border-slate-800">
                {last7Days.map((d) => {
                  const heightPercent = Math.max(8, Math.min(100, Math.round((d.revenue / maxRevenue) * 100)));
                  const isToday = d.dayKey === todayStr;
                  return (
                    <div key={d.dayKey} className="flex-1 flex flex-col items-center h-full justify-end group">
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity text-[11px] font-mono font-bold bg-slate-800 text-sky-300 px-2 py-1 rounded shadow -translate-y-2 pointer-events-none whitespace-nowrap">
                        {formatMoney(d.revenue)} ({d.count} v.)
                      </div>
                      <div
                        style={{ height: `${heightPercent}%` }}
                        className={`w-full max-w-[48px] rounded-t-lg transition-all duration-500 relative ${
                          isToday
                            ? 'bg-gradient-to-t from-blue-700 to-sky-400 shadow-lg shadow-blue-500/20'
                            : 'bg-slate-800 hover:bg-slate-700'
                        }`}
                      />
                      <span className={`mt-3 text-xs font-semibold capitalize ${isToday ? 'text-sky-400 font-bold' : 'text-slate-400'}`}>
                        {d.dayName}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right 1 Col: Top 5 Best Sellers */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-bold text-white">Top 5 Ventes</h3>
                <span className="text-xs text-slate-400">Par volume</span>
              </div>

              <div className="space-y-4 flex-1">
                {topSelling.length === 0 ? (
                  <p className="text-sm text-slate-500 py-6 text-center">Aucune vente enregistrée pour le moment.</p>
                ) : (
                  topSelling.map((it, idx) => {
                    const percent = Math.round((it.qty / maxSoldQty) * 100);
                    return (
                      <div key={it.name} className="space-y-1.5">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-slate-200 truncate pr-2">
                            {idx + 1}. {it.name}
                          </span>
                          <span className="font-mono font-bold text-sky-400 shrink-0">
                            {it.qty} vendus
                          </span>
                        </div>
                        <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                          <div
                            style={{ width: `${percent}%` }}
                            className="h-full rounded-full bg-gradient-to-r from-blue-600 to-sky-400"
                          />
                        </div>
                        <div className="text-[11px] text-slate-400 text-right font-mono">
                          {formatMoney(it.revenue)}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>

          {/* Low Stock Warning Table & Fast Restock */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>Articles nécessitant un réapprovisionnement</span>
                </h3>
                <p className="text-xs text-slate-400">Stock inférieur ou égal au seuil de sécurité ({settings.stock_threshold} unités)</p>
              </div>
              <button
                onClick={() => setCurrentPage('products')}
                className="text-xs font-semibold text-sky-400 hover:text-sky-300 transition-colors"
              >
                Gérer les stocks →
              </button>
            </div>

            {lowStockProducts.length === 0 ? (
              <div className="p-6 text-center text-sm text-emerald-400 flex items-center justify-center gap-2">
                <CheckCircle2 className="w-5 h-5" />
                <span>Tous les articles ont un niveau de stock suffisant.</span>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 text-xs font-bold text-slate-400 uppercase">
                      <th className="py-3 px-4">Article</th>
                      <th className="py-3 px-4">Rayon</th>
                      <th className="py-3 px-4 text-center">Stock Actuel</th>
                      <th className="py-3 px-4 text-right">Prix Unitaire</th>
                      <th className="py-3 px-4 text-center">Réappro. Rapide</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {lowStockProducts.slice(0, 5).map((p) => (
                      <tr key={p.id} className="hover:bg-slate-850/40 transition-colors">
                        <td className="py-3 px-4 font-semibold text-white">
                          {p.name}
                        </td>
                        <td className="py-3 px-4 text-slate-400">{p.category}</td>
                        <td className="py-3 px-4 text-center">
                          <span
                            className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold ${
                              p.qty <= 0
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            }`}
                          >
                            {p.qty <= 0 ? 'RUPTURE' : `${p.qty} restant(s)`}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right font-mono font-bold text-slate-200">
                          {formatMoney(p.price)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <div className="flex items-center justify-center gap-1.5">
                            <button
                              onClick={() => adjustStock(p.id, 5)}
                              title="Ajouter 5 unités au stock"
                              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs font-bold text-sky-400 border border-slate-700 transition-all cursor-pointer"
                            >
                              +5
                            </button>
                            <button
                              onClick={() => adjustStock(p.id, 10)}
                              title="Ajouter 10 unités au stock"
                              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs font-bold text-emerald-400 border border-slate-700 transition-all cursor-pointer"
                            >
                              +10
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Embedded Calculator side-panel if toggled */}
        {isCalculatorVisible && (
          <div className="shrink-0 w-full lg:w-auto flex justify-center">
            <EmbeddedCalculator onClose={() => setIsCalculatorVisible(false)} />
          </div>
        )}
      </div>
    </div>
  );
};
