import React, { useState } from 'react';
import { usePOS } from '../context/POSContext';
import { Settings, Save, RotateCcw, Download, ShieldCheck, Palette, CheckCircle2 } from 'lucide-react';

export const SettingsScreen: React.FC = () => {
  const { settings, updateSettings, resetAllData } = usePOS();
  const [formData, setFormData] = useState({ ...settings });
  const [savedSuccess, setSavedSuccess] = useState(false);

  const themeOptions = [
    { id: 'Bleu TOP-BOX', name: 'Bleu TOP-BOX (Pro Sombre)', color: 'bg-blue-600' },
    { id: 'Bleu', name: 'Bleu Classique', color: 'bg-blue-500' },
    { id: 'Bleu Royal', name: 'Bleu Royal', color: 'bg-indigo-600' },
    { id: 'Bleu Nuit', name: 'Bleu Nuit Profond', color: 'bg-sky-500' },
    { id: 'Émeraude', name: 'Émeraude Végétal', color: 'bg-emerald-600' },
    { id: 'Turquoise', name: 'Turquoise Lagon', color: 'bg-teal-500' },
    { id: 'Violet', name: 'Violet Améthyste', color: 'bg-purple-600' },
    { id: 'Orange', name: 'Orange Énergie', color: 'bg-orange-600' },
    { id: 'Sombre', name: 'Noir Carbone', color: 'bg-slate-700' },
  ];

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateSettings(formData);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 4000);
  };

  const exportBackupJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(
      JSON.stringify({
        date: new Date().toISOString(),
        settings: formData,
        products: JSON.parse(localStorage.getItem('topbox_products') || '[]'),
        sales: JSON.parse(localStorage.getItem('topbox_sales') || '[]'),
        clients: JSON.parse(localStorage.getItem('topbox_clients') || '[]'),
        closings: JSON.parse(localStorage.getItem('topbox_closings') || '[]'),
      }, null, 2)
    );
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `TOP_BOX_Sauvegarde_${new Date().toISOString().substring(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
          Paramètres du Logiciel & Personnalisation
        </h1>
        <p className="text-sm text-slate-400">
          Configuration de la boutique, en-tête des tickets, devises et thèmes visuels.
        </p>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm font-bold flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span>Tous les paramètres ont été enregistrés avec succès !</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Section 1: Identité du commerce */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <ShieldCheck className="w-4 h-4 text-sky-400" />
              <span>Identité Commerciale</span>
            </h2>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">
                Nom de l’établissement *
              </label>
              <input
                type="text"
                required
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-bold focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Nom de la caisse
                </label>
                <input
                  type="text"
                  value={formData.register}
                  onChange={(e) => setFormData({ ...formData, register: e.target.value })}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-semibold focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Devise Monétaire
                </label>
                <input
                  type="text"
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  placeholder="FCFA, EUR, USD..."
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-mono font-bold focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">
                Caissier en service
              </label>
              <input
                type="text"
                value={formData.cashier}
                onChange={(e) => setFormData({ ...formData, cashier: e.target.value })}
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-semibold focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Numéro de Téléphone
                </label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-mono focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  E-mail de contact
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">
                Adresse physique
              </label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Section 2: Ticket & Sécurité */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <Palette className="w-4 h-4 text-emerald-400" />
              <span>Ticket & Paramètres de Caisse</span>
            </h2>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">
                Slogan / En-tête de ticket
              </label>
              <input
                type="text"
                value={formData.header}
                onChange={(e) => setFormData({ ...formData, header: e.target.value })}
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-semibold focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-300 block mb-1">
                Message de pied de ticket
              </label>
              <input
                type="text"
                value={formData.footer}
                onChange={(e) => setFormData({ ...formData, footer: e.target.value })}
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Seuil stock faible alerte
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.stock_threshold}
                  onChange={(e) => setFormData({ ...formData, stock_threshold: parseInt(e.target.value) || 5 })}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-mono font-bold focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Taux TVA par défaut (%)
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={formData.tax_rate}
                  onChange={(e) => setFormData({ ...formData, tax_rate: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-mono font-bold focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            {/* Negative stock toggle */}
            <div className="pt-2">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={formData.allow_negative_stock}
                  onChange={(e) => setFormData({ ...formData, allow_negative_stock: e.target.checked })}
                  className="w-4 h-4 rounded text-blue-600 focus:ring-0 bg-slate-950 border-slate-800"
                />
                <span className="text-xs text-slate-300 font-semibold">
                  Autoriser les ventes en stock négatif (dépassement autorisé)
                </span>
              </label>
            </div>

            {/* Theme selector */}
            <div className="pt-2">
              <label className="text-xs font-bold text-slate-300 block mb-2">
                Palette de couleurs (Synchronisée Windows & Web)
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {themeOptions.map((th) => (
                  <button
                    key={th.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, theme: th.id })}
                    className={`p-2 rounded-xl text-[11px] font-bold flex items-center gap-2 border text-left transition-all cursor-pointer ${
                      formData.theme === th.id
                        ? 'border-blue-500 bg-blue-600/20 text-white'
                        : 'border-slate-800 bg-slate-950 text-slate-400 hover:text-white'
                    }`}
                  >
                    <span className={`w-3 h-3 rounded-full ${th.color} shrink-0`} />
                    <span className="truncate">{th.id}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Action Bottom Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              type="button"
              onClick={exportBackupJSON}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition-all cursor-pointer"
            >
              <Download className="w-4 h-4 text-sky-400" />
              <span>Sauvegarde (JSON)</span>
            </button>
            <a
              href="/TOP-BOX.zip"
              download="TOP-BOX.zip"
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-sky-300 text-xs font-bold border border-slate-700 transition-all cursor-pointer"
            >
              <Download className="w-4 h-4 text-sky-400" />
              <span>Package Windows (.ZIP)</span>
            </a>
            <button
              type="button"
              onClick={() => {
                if (confirm('Attention : Réinitialiser rechargera les données de démonstration avec 16 articles frais et 4 clients. Confirmer ?')) {
                  resetAllData();
                  setFormData({ ...settings });
                }
              }}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-rose-950/60 hover:bg-rose-900 text-rose-300 text-xs font-bold border border-rose-800/80 transition-all cursor-pointer"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Réinitialiser Caisse</span>
            </button>
          </div>

          <button
            type="submit"
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-black shadow-lg shadow-blue-600/30 transition-all cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>ENREGISTRER TOUS LES PARAMÈTRES</span>
          </button>
        </div>
      </form>
    </div>
  );
};
