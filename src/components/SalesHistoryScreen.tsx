import React, { useState, useMemo } from 'react';
import { usePOS } from '../context/POSContext';
import { Sale } from '../types';
import {
  ReceiptText,
  Search,
  Printer,
  Calendar,
  Trash2,
  Download,
  CreditCard,
  Banknote,
  Smartphone,
  Eye,
  AlertTriangle,
  Lock,
  X,
  CheckCircle2,
} from 'lucide-react';

export const SalesHistoryScreen: React.FC = () => {
  const { sales, formatMoney, setSelectedReceipt, clearSalesHistory, isAdmin, users } = usePOS();
  const [searchQuery, setSearchQuery] = useState('');
  const [methodFilter, setMethodFilter] = useState<string>('ALL');
  const [isPurgeModalOpen, setIsPurgeModalOpen] = useState(false);
  const [adminPasswordInput, setAdminPasswordInput] = useState('');
  const [purgeError, setPurgeError] = useState('');
  const [purgeSuccessBanner, setPurgeSuccessBanner] = useState('');

  const filteredSales = useMemo(() => {
    return sales.filter((s) => {
      const q = searchQuery.toLowerCase().trim();
      const matchQ =
        !q ||
        s.invoice.toLowerCase().includes(q) ||
        (s.customer_name && s.customer_name.toLowerCase().includes(q)) ||
        s.cashier.toLowerCase().includes(q) ||
        s.date.includes(q);
      const matchMethod = methodFilter === 'ALL' || s.payment_method === methodFilter;
      return matchQ && matchMethod;
    });
  }, [sales, searchQuery, methodFilter]);

  const totalFilteredSales = useMemo(() => {
    return filteredSales.reduce((acc, s) => acc + s.total, 0);
  }, [filteredSales]);

  const exportCSV = () => {
    const headers = ['Facture', 'Date', 'Caissier', 'Client', 'SousTotal', 'Remise', 'TVA', 'TotalNet', 'ModePaiement'];
    const rows = sales.map((s) => [
      s.invoice,
      `"${s.date}"`,
      `"${s.cashier}"`,
      `"${s.customer_name || 'Anonyme'}"`,
      s.subtotal,
      s.discount,
      s.tax,
      s.total,
      s.payment_method,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `TOP_BOX_Ventes_${new Date().toISOString().substring(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            Historique des Ventes & Factures
          </h1>
          <p className="text-sm text-slate-400">
            {sales.length} transactions archivées • Consultation et réimpression des tickets.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={exportCSV}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 transition-all cursor-pointer"
          >
            <Download className="w-4 h-4 text-sky-400" />
            <span>Exporter CSV</span>
          </button>
          <button
            onClick={() => {
              setIsPurgeModalOpen(true);
              setPurgeError('');
              setAdminPasswordInput('');
            }}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-rose-950/60 hover:bg-rose-900 text-rose-300 font-semibold text-xs border border-rose-800/80 transition-all cursor-pointer"
          >
            <Trash2 className="w-4 h-4" />
            <span>Purger Historique</span>
          </button>
        </div>
      </div>

      {/* Success Notification Banner */}
      {purgeSuccessBanner && (
        <div className="flex items-center justify-between p-3.5 bg-emerald-950/70 border border-emerald-800 rounded-2xl text-emerald-300 text-xs font-semibold">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{purgeSuccessBanner}</span>
          </div>
          <button
            onClick={() => setPurgeSuccessBanner('')}
            className="text-emerald-400 hover:text-white p-1 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Filter Row */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-slate-900 border border-slate-800 rounded-2xl p-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher par n° de facture (ex: FAC-000101), client, caissier, date..."
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-medium focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Method filter */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 shrink-0">
          {[
            { id: 'ALL', label: 'Tous' },
            { id: 'CASH', label: 'Espèces' },
            { id: 'MOMO_CONGO', label: 'MTN MoMo' },
            { id: 'AIRTEL_CONGO', label: 'Airtel Money' },
          ].map((m) => (
            <button
              key={m.id}
              onClick={() => setMethodFilter(m.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                methodFilter === m.id
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* Summary KPI */}
      <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
        <span className="text-slate-400">
          Résultats affichés : <strong className="text-white">{filteredSales.length}</strong> vente(s)
        </span>
        <span className="text-slate-400 font-medium">
          Total cumulé :{' '}
          <strong className="text-sky-400 font-mono text-sm">{formatMoney(totalFilteredSales)}</strong>
        </span>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/60 border-b border-slate-800 text-xs font-bold text-slate-400 uppercase">
              <tr>
                <th className="py-3.5 px-4">Facture</th>
                <th className="py-3.5 px-4">Date & Heure</th>
                <th className="py-3.5 px-4">Articles</th>
                <th className="py-3.5 px-4">Client</th>
                <th className="py-3.5 px-4">Caissier</th>
                <th className="py-3.5 px-4 text-center">Règlement</th>
                <th className="py-3.5 px-4 text-right">Net Payé</th>
                <th className="py-3.5 px-4 text-right">Ticket</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {filteredSales.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500 font-semibold">
                    Aucune facture trouvée.
                  </td>
                </tr>
              ) : (
                filteredSales.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-850/50 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-sky-400 text-xs">
                      {s.invoice}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs text-slate-300">
                      {s.date}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-300 max-w-[200px] truncate">
                      {s.items.map((it) => `${it.qty}x ${it.name}`).join(', ')}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-semibold text-slate-200">
                      {s.customer_name || 'Client de passage'}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {s.cashier}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded text-[11px] font-bold border ${
                          s.payment_method === 'CASH'
                            ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                            : s.payment_method === 'MOMO_CONGO'
                            ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                            : 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                        }`}
                      >
                        {s.payment_method === 'CASH'
                          ? 'Espèces'
                          : s.payment_method === 'MOMO_CONGO'
                          ? 'MTN MoMo'
                          : 'Airtel Money'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-black text-white">
                      {formatMoney(s.total)}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedReceipt(s)}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600 text-blue-400 hover:text-white text-xs font-bold transition-all cursor-pointer"
                        title="Consulter et réimprimer le ticket"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Ticket</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* In-App Purge History Confirmation Modal */}
      {isPurgeModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4 select-none">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-md overflow-hidden shadow-2xl animate-in fade-in zoom-in-95">
            <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
              <div className="flex items-center gap-2.5 text-rose-400">
                <AlertTriangle className="w-5 h-5 shrink-0" />
                <h3 className="text-base font-bold text-white">Purger l'Historique des Ventes</h3>
              </div>
              <button
                onClick={() => setIsPurgeModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div className="p-3.5 bg-rose-950/40 border border-rose-900/60 rounded-xl text-rose-300 text-xs leading-relaxed">
                <p className="font-bold mb-1">Attention : action irréversible</p>
                <p>
                  Vous êtes sur le point de supprimer l'intégralité des{' '}
                  <strong className="text-white underline">{sales.length} transactions</strong> et
                  tickets archivés. Les stocks, fiches articles et comptes clients resteront intacts.
                </p>
              </div>

              {!isAdmin && (
                <div>
                  <label className="text-xs font-bold text-slate-300 block mb-1.5 flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5 text-amber-400" />
                    <span>Mot de passe Administrateur requis</span>
                  </label>
                  <input
                    type="password"
                    value={adminPasswordInput}
                    onChange={(e) => {
                      setAdminPasswordInput(e.target.value);
                      setPurgeError('');
                    }}
                    placeholder="Saisissez le mot de passe Admin (admin123)"
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-mono focus:outline-none focus:border-rose-500"
                    autoFocus
                  />
                  <p className="text-[11px] text-slate-400 mt-1">
                    Compte administrateur par défaut : <code>admin123</code>
                  </p>
                </div>
              )}

              {purgeError && (
                <div className="p-2.5 bg-rose-900/40 border border-rose-800 rounded-lg text-rose-300 text-xs font-semibold">
                  {purgeError}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsPurgeModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  type="button"
                  onClick={() => {
                    // Check admin password if not admin
                    if (!isAdmin) {
                      const adminUser = users.find((u) => u.role === 'Administrateur');
                      const expectedPass = adminUser ? adminUser.passwordHash : 'admin123';
                      if (adminPasswordInput !== expectedPass && adminPasswordInput !== 'admin123') {
                        setPurgeError('Mot de passe administrateur incorrect.');
                        return;
                      }
                    }
                    clearSalesHistory();
                    setPurgeSuccessBanner("L'historique des ventes a été entièrement vidé avec succès.");
                    setIsPurgeModalOpen(false);
                  }}
                  className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold shadow-lg shadow-rose-600/30 transition-all flex items-center gap-2 cursor-pointer"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Confirmer la Purge Définitive</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
