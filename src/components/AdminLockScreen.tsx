import React, { useState } from 'react';
import { usePOS } from '../context/POSContext';
import { Lock, ShieldAlert, KeyRound, ArrowLeft, CheckCircle2 } from 'lucide-react';

interface AdminLockScreenProps {
  pageTitle: string;
  onUnlocked?: () => void;
}

export const AdminLockScreen: React.FC<AdminLockScreenProps> = ({ pageTitle, onUnlocked }) => {
  const { currentUser, users, loginUser, setCurrentPage } = usePOS();
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleUnlock = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    // Find any admin user or default admin credentials
    const adminUser = users.find((u) => u.role === 'Administrateur');
    const validPassword = adminUser ? adminUser.passwordHash : 'admin123';

    if (password === validPassword || password === 'admin123') {
      const adminUsername = adminUser ? adminUser.username : 'admin';
      loginUser(adminUsername, password);
      setSuccessMsg('Accès Administrateur déverrouillé !');
      setTimeout(() => {
        if (onUnlocked) onUnlocked();
      }, 400);
    } else {
      setErrorMsg('Mot de passe administrateur incorrect.');
    }
  };

  return (
    <div className="flex-1 overflow-y-auto flex items-center justify-center p-6 bg-slate-950 select-none">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-md p-8 shadow-2xl text-center space-y-6 animate-in fade-in zoom-in-95">
        <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mx-auto shadow-lg shadow-amber-500/10">
          <Lock className="w-8 h-8" />
        </div>

        <div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-bold mb-3">
            <ShieldAlert className="w-3.5 h-3.5" />
            Accès Réservé Administrateur
          </span>
          <h2 className="text-xl font-black text-white tracking-tight">
            Onglet « {pageTitle} » Verrouillé
          </h2>
          <p className="text-xs text-slate-400 mt-2 leading-relaxed">
            La session caissier actuelle (<strong className="text-slate-200">{currentUser?.fullName}</strong>) n'a pas les droits pour accéder à cette section.
          </p>
        </div>

        <form onSubmit={handleUnlock} className="space-y-4 text-left">
          <div>
            <label className="text-xs font-bold text-slate-300 block mb-1.5 flex items-center gap-1.5">
              <KeyRound className="w-3.5 h-3.5 text-sky-400" />
              <span>Mot de passe Administrateur</span>
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setErrorMsg('');
              }}
              placeholder="Entrez le mot de passe Admin (admin123)"
              className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white text-sm font-mono focus:outline-none focus:border-blue-500 transition-colors"
              autoFocus
            />
            <p className="text-[11px] text-slate-400 mt-1">
              Code par défaut : <code>admin123</code>
            </p>
          </div>

          {errorMsg && (
            <div className="p-3 bg-rose-950/60 border border-rose-800/80 rounded-xl text-rose-300 text-xs font-semibold">
              {errorMsg}
            </div>
          )}

          {successMsg && (
            <div className="p-3 bg-emerald-950/60 border border-emerald-800/80 rounded-xl text-emerald-300 text-xs font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <div className="flex flex-col gap-2 pt-2">
            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs uppercase tracking-wider transition-all shadow-lg shadow-blue-600/25 flex items-center justify-center gap-2 cursor-pointer"
            >
              <KeyRound className="w-4 h-4" />
              <span>Déverrouiller avec le compte Admin</span>
            </button>

            <button
              type="button"
              onClick={() => setCurrentPage('pos')}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Retour à la Caisse (Nouvelle Vente)</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
