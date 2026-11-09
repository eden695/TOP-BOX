import React, { useState } from 'react';
import { usePOS } from '../context/POSContext';
import { User } from '../types';
import {
  UserCog,
  Plus,
  KeyRound,
  Trash2,
  CheckCircle2,
  UserCheck,
  Shield,
  ShieldAlert,
  Edit2,
  X,
  Lock,
  LogIn,
} from 'lucide-react';

export const UsersScreen: React.FC = () => {
  const { users, currentUser, switchCashier, addUser, updateUser, deleteUser } = usePOS();

  // Modals state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [selectedUserForPass, setSelectedUserForPass] = useState<User | null>(null);
  const [newPassword, setNewPassword] = useState('');
  const [statusMsg, setStatusMsg] = useState('');

  // Add form state
  const [formData, setFormData] = useState({
    username: '',
    fullName: '',
    passwordHash: '',
    role: 'Caissier' as 'Administrateur' | 'Caissier',
    active: true,
  });

  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.username.trim() || !formData.fullName.trim() || !formData.passwordHash.trim()) {
      alert('Veuillez renseigner tous les champs obligatoires.');
      return;
    }

    // Check unique username
    if (users.some((u) => u.username.toLowerCase() === formData.username.toLowerCase().trim())) {
      alert(`L'identifiant "${formData.username}" existe déjà. Veuillez en choisir un autre.`);
      return;
    }

    addUser(formData);
    setFormData({
      username: '',
      fullName: '',
      passwordHash: '',
      role: 'Caissier',
      active: true,
    });
    setIsAddModalOpen(false);
    setStatusMsg('Nouveau caissier ajouté avec succès !');
    setTimeout(() => setStatusMsg(''), 4000);
  };

  const handleUpdatePassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUserForPass || !newPassword.trim()) return;

    updateUser(selectedUserForPass.id, { passwordHash: newPassword.trim() });
    setIsPasswordModalOpen(false);
    setSelectedUserForPass(null);
    setNewPassword('');
    setStatusMsg(`Mot de passe mis à jour pour ${selectedUserForPass.fullName} !`);
    setTimeout(() => setStatusMsg(''), 4000);
  };

  const toggleActiveStatus = (user: User) => {
    if (user.id === currentUser?.id) {
      alert('Vous ne pouvez pas désactiver votre propre session active.');
      return;
    }
    updateUser(user.id, { active: !user.active });
  };

  const handleDelete = (user: User) => {
    if (user.id === currentUser?.id) {
      alert('Vous ne pouvez pas supprimer le compte actuellement connecté.');
      return;
    }
    if (user.role === 'Administrateur' && users.filter((u) => u.role === 'Administrateur').length <= 1) {
      alert('Le système doit conserver au moins un compte Administrateur.');
      return;
    }
    if (confirm(`Confirmer la suppression définitive du compte de "${user.fullName}" ?`)) {
      deleteUser(user.id);
      setStatusMsg(`Compte "${user.fullName}" supprimé.`);
      setTimeout(() => setStatusMsg(''), 4000);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            Gestion des Caissiers & Sessions
          </h1>
          <p className="text-sm text-slate-400">
            Contrôle des accès, ouverture de session caissier, modification des mots de passe.
          </p>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-lg shadow-blue-600/30 transition-all cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Ajouter un Caissier</span>
        </button>
      </div>

      {statusMsg && (
        <div className="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs font-bold flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{statusMsg}</span>
        </div>
      )}

      {/* ACTIVE CAISSIER SESSION CARD */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950/40 to-slate-900 border border-blue-900/60 rounded-3xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-600/20 text-sky-400 border border-blue-500/30 flex items-center justify-center text-2xl font-black shrink-0">
              {(currentUser?.fullName || currentUser?.username || 'C').charAt(0)}
            </div>
            <div>
              <span className="text-[11px] font-bold text-sky-400 uppercase tracking-wider flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                SESSION ACTIVE EN COURS
              </span>
              <h2 className="text-xl font-black text-white">{currentUser?.fullName || currentUser?.username || 'Utilisateur'}</h2>
              <p className="text-xs text-slate-400">
                Identifiant : <code className="text-slate-300 font-bold">{currentUser?.username}</code> • Rôle :{' '}
                <strong className={currentUser?.role === 'Administrateur' ? 'text-amber-400' : 'text-sky-400'}>
                  {currentUser?.role}
                </strong>
              </p>
            </div>
          </div>

          {/* Quick Cashier Switcher */}
          <div className="flex items-center gap-2 bg-slate-950 p-2 rounded-2xl border border-slate-800 shrink-0">
            <span className="text-xs text-slate-400 px-2 font-medium">Basculer de session :</span>
            <select
              value={currentUser?.id || ''}
              onChange={(e) => switchCashier(parseInt(e.target.value))}
              className="bg-slate-900 text-xs font-bold text-white border border-slate-700 rounded-xl px-3 py-2 focus:outline-none focus:border-blue-500 cursor-pointer"
            >
              {users
                .filter((u) => u.active)
                .map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.fullName} ({u.role})
                  </option>
                ))}
            </select>
          </div>
        </div>
      </div>

      {/* ALL USERS TABLE */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Shield className="w-4 h-4 text-sky-400" />
            <span>Comptes Caissiers & Administrateurs Enregistrés</span>
          </h2>
          <span className="text-xs text-slate-400 font-medium">
            {users.length} compte{users.length > 1 ? 's' : ''} au total
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/60 border-b border-slate-800 text-xs font-bold text-slate-400 uppercase">
              <tr>
                <th className="py-3.5 px-4">Utilisateur / Caissier</th>
                <th className="py-3.5 px-4">Identifiant</th>
                <th className="py-3.5 px-4">Rôle</th>
                <th className="py-3.5 px-4 text-center">État du Compte</th>
                <th className="py-3.5 px-4">Créé le</th>
                <th className="py-3.5 px-4 text-right">Actions Administrateur</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {users.map((u) => {
                const isCurrent = u.id === currentUser?.id;
                return (
                  <tr key={u.id} className="hover:bg-slate-850/50 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-8 h-8 rounded-full font-bold flex items-center justify-center text-xs shrink-0 ${
                            u.role === 'Administrateur'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'bg-blue-600/20 text-sky-300'
                          }`}
                        >
                          {u.fullName.charAt(0)}
                        </div>
                        <div>
                          <span className="font-bold text-white block text-sm">{u.fullName}</span>
                          {isCurrent && (
                            <span className="text-[10px] text-emerald-400 font-extrabold">
                              ● Connecté actuellement
                            </span>
                          )}
                        </div>
                      </div>
                    </td>

                    <td className="py-3.5 px-4 font-mono text-xs text-slate-300">
                      {u.username}
                    </td>

                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold ${
                          u.role === 'Administrateur'
                            ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                            : 'bg-slate-800 text-slate-300 border border-slate-700'
                        }`}
                      >
                        {u.role}
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      <button
                        onClick={() => toggleActiveStatus(u)}
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold cursor-pointer transition-all ${
                          u.active
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30'
                            : 'bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30'
                        }`}
                        title="Cliquer pour activer ou désactiver ce compte"
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${u.active ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                        <span>{u.active ? 'Actif' : 'Désactivé'}</span>
                      </button>
                    </td>

                    <td className="py-3.5 px-4 text-xs font-mono text-slate-400">
                      {u.createdAt ? u.createdAt.substring(0, 10) : '—'}
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {/* Switch button */}
                        {!isCurrent && u.active && (
                          <button
                            onClick={() => switchCashier(u.id)}
                            className="px-2.5 py-1 rounded-lg bg-blue-600/20 hover:bg-blue-600 text-sky-400 hover:text-white text-xs font-bold transition-all cursor-pointer"
                            title="Ouvrir la session avec ce caissier"
                          >
                            Ouvrir session
                          </button>
                        )}

                        {/* Change password button */}
                        <button
                          onClick={() => {
                            setSelectedUserForPass(u);
                            setNewPassword('');
                            setIsPasswordModalOpen(true);
                          }}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all cursor-pointer"
                          title="Modifier le mot de passe / Code PIN"
                        >
                          <KeyRound className="w-3.5 h-3.5 text-amber-400" />
                        </button>

                        {/* Delete account */}
                        {!isCurrent && (
                          <button
                            onClick={() => handleDelete(u)}
                            className="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-950/60 text-slate-400 hover:text-rose-400 transition-all cursor-pointer"
                            title="Supprimer ce compte"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* MODAL 1: AJOUTER UN CAISSIER */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-md overflow-hidden shadow-2xl">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <UserCog className="w-4 h-4 text-sky-400" />
                <span>Nouveau Compte Caissier</span>
              </h3>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="p-6 space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Nom complet du caissier *
                </label>
                <input
                  type="text"
                  required
                  value={formData.fullName}
                  onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                  placeholder="Ex : Grace Mabiala"
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-semibold focus:outline-none focus:border-blue-500"
                  autoFocus
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Identifiant de connexion (login unique) *
                </label>
                <input
                  type="text"
                  required
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="Ex : grace"
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-mono focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Mot de passe ou Code PIN de caisse *
                </label>
                <input
                  type="password"
                  required
                  value={formData.passwordHash}
                  onChange={(e) => setFormData({ ...formData, passwordHash: e.target.value })}
                  placeholder="4 chiffres ou mot de passe"
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-mono focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Rôle & Permissions
                </label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-bold focus:outline-none focus:border-blue-500 cursor-pointer"
                >
                  <option value="Caissier">Caissier (Ventes, tickets et clôtures)</option>
                  <option value="Administrateur">Administrateur (Accès total & gestion des caissiers)</option>
                </select>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-lg shadow-blue-600/30 cursor-pointer"
                >
                  Créer le Caissier
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: MODIFIER LE MOT DE PASSE DU CAISSIER */}
      {isPasswordModalOpen && selectedUserForPass && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-sm overflow-hidden shadow-2xl">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <KeyRound className="w-4 h-4 text-amber-400" />
                <span>Modifier le Mot de Passe</span>
              </h3>
              <button
                onClick={() => setIsPasswordModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdatePassword} className="p-6 space-y-4">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-[11px] text-slate-400 block">Caissier concerné :</span>
                <strong className="text-sm text-white font-bold">{selectedUserForPass.fullName}</strong>
                <span className="text-xs text-sky-400 font-mono block">({selectedUserForPass.username})</span>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1">
                  Nouveau mot de passe ou code PIN *
                </label>
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Saisissez le nouveau mot de passe"
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-mono focus:outline-none focus:border-blue-500"
                  autoFocus
                />
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setIsPasswordModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold shadow-lg shadow-amber-600/30 cursor-pointer"
                >
                  Enregistrer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
