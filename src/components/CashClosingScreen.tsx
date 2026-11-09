import React, { useState } from 'react';
import { usePOS } from '../context/POSContext';
import { CalendarCheck, DollarSign, CheckCircle2, Printer, AlertCircle } from 'lucide-react';

export const CashClosingScreen: React.FC = () => {
  const { sales, closings, performDailyClosing, formatMoney, settings } = usePOS();
  const [closingNotes, setClosingNotes] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const todayPrefix = new Date().toISOString().substring(0, 10);
  const todaySales = sales.filter((s) => s.date.startsWith(todayPrefix));

  const totalSalesToday = todaySales.reduce((acc, s) => acc + s.total, 0);
  const cashReceivedToday = todaySales.reduce((acc, s) => acc + s.received, 0);
  const changeGivenToday = todaySales.reduce((acc, s) => acc + s.change_amt, 0);
  const discountsToday = todaySales.reduce((acc, s) => acc + s.discount, 0);

  const handlePerformClosing = () => {
    if (confirm('Voulez-vous enregistrer officiellement la clôture de caisse (Z-Report) pour cette journée ?')) {
      performDailyClosing(closingNotes);
      setClosingNotes('');
      setSuccessMessage('Clôture journalière enregistrée avec succès dans la base de données !');
      setTimeout(() => setSuccessMessage(''), 5000);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
          Clôture de Caisse & Rapport Journalier (Z)
        </h1>
        <p className="text-sm text-slate-400">
          Arrêté des comptes de la journée, contrôle du tiroir-caisse et archivage comptable.
        </p>
      </div>

      {successMessage && (
        <div className="p-4 rounded-2xl bg-emerald-950/60 border border-emerald-800/80 text-emerald-300 text-sm font-bold flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Today's Z-Report Active Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-800">
          <div>
            <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">
              Opérations du Jour ({todayPrefix})
            </span>
            <h2 className="text-xl font-black text-white">Bilan Actuel de Caisse</h2>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-400">Caissier en service :</span>
            <p className="text-sm font-bold text-slate-200">{settings.cashier}</p>
          </div>
        </div>

        {/* 4 Stats Boxes */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
            <span className="text-xs font-bold text-slate-400">Chiffre d’affaires Net</span>
            <div className="text-xl font-black text-white font-mono mt-1">
              {formatMoney(totalSalesToday)}
            </div>
            <span className="text-[11px] text-slate-500">{todaySales.length} transaction(s)</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
            <span className="text-xs font-bold text-slate-400">Espèces Reçues</span>
            <div className="text-xl font-black text-sky-400 font-mono mt-1">
              {formatMoney(cashReceivedToday)}
            </div>
            <span className="text-[11px] text-slate-500">Tiroir caisse brut</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
            <span className="text-xs font-bold text-slate-400">Monnaie Rendue</span>
            <div className="text-xl font-black text-amber-400 font-mono mt-1">
              {formatMoney(changeGivenToday)}
            </div>
            <span className="text-[11px] text-slate-500">Rendus clients</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
            <span className="text-xs font-bold text-slate-400">Remises Accordées</span>
            <div className="text-xl font-black text-rose-400 font-mono mt-1">
              {formatMoney(discountsToday)}
            </div>
            <span className="text-[11px] text-slate-500">Geste commercial</span>
          </div>
        </div>

        {/* Closing Notes & Validate Button */}
        <div className="space-y-4 pt-4 border-t border-slate-800">
          <div>
            <label className="text-xs font-bold text-slate-300 block mb-1">
              Observations / Fond de caisse physique vérifié
            </label>
            <input
              type="text"
              value={closingNotes}
              onChange={(e) => setClosingNotes(e.target.value)}
              placeholder="Ex : Fond de caisse vérifié, espèces conformes aux tickets, aucun incident."
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-medium focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <AlertCircle className="w-4 h-4 text-sky-400" />
              <span>
                La clôture enregistre un instantané permanent dans la table <code>cash_closings</code>.
              </span>
            </div>

            <button
              onClick={handlePerformClosing}
              className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs shadow-lg shadow-emerald-600/30 flex items-center gap-2 transition-all cursor-pointer"
            >
              <CalendarCheck className="w-4 h-4" />
              <span>ENREGISTRER LA CLÔTURE DE CAISSE (Z)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Historical Closings Archive */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h2 className="text-base font-bold text-white mb-4">Historique des Clôtures de Caisse</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/60 border-b border-slate-800 text-xs font-bold text-slate-400 uppercase">
              <tr>
                <th className="py-3 px-4">Date & Heure</th>
                <th className="py-3 px-4 text-center">Ventes</th>
                <th className="py-3 px-4 text-right">Chiffre Net</th>
                <th className="py-3 px-4 text-right">Espèces Reçues</th>
                <th className="py-3 px-4 text-right">Monnaie Rendue</th>
                <th className="py-3 px-4 text-right">Remises</th>
                <th className="py-3 px-4">Notes de Caisse</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {closings.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 font-semibold">
                    Aucune clôture archivée pour le moment.
                  </td>
                </tr>
              ) : (
                closings.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-850/50 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-xs font-bold text-sky-400">
                      {c.closed_at}
                    </td>
                    <td className="py-3.5 px-4 text-center text-xs font-bold text-slate-200">
                      {c.sales_count}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-black text-white">
                      {formatMoney(c.total_sales)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-xs text-slate-300">
                      {formatMoney(c.cash_received)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-xs text-amber-400">
                      {formatMoney(c.change_given)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-xs text-rose-400">
                      {formatMoney(c.discount_total)}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400 max-w-[240px] truncate">
                      {c.notes || '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
