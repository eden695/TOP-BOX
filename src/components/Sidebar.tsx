import React from 'react';
import { usePOS } from '../context/POSContext';
import { PageId } from '../types';
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  ReceiptText,
  Users,
  CalendarCheck,
  BookOpen,
  UserCog,
  Settings,
  CircleDot,
  LogOut,
  Lock,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { currentPage, setCurrentPage, settings, quickAlertsCount, currentUser, isAdmin } = usePOS();

  const navItems: { id: PageId; label: string; icon: React.ReactNode; badge?: number }[] = [
    {
      id: 'dashboard',
      label: 'Tableau de bord',
      icon: <LayoutDashboard className="w-5 h-5" />,
      badge: quickAlertsCount.lowStock > 0 ? quickAlertsCount.lowStock : undefined,
    },
    {
      id: 'pos',
      label: 'Nouvelle Vente',
      icon: <ShoppingCart className="w-5 h-5" />,
    },
    {
      id: 'products',
      label: 'Produits & Stocks',
      icon: <Package className="w-5 h-5" />,
    },
    {
      id: 'history',
      label: 'Historique Ventes',
      icon: <ReceiptText className="w-5 h-5" />,
    },
    {
      id: 'clients',
      label: 'Clients & Fidélité',
      icon: <Users className="w-5 h-5" />,
    },
    {
      id: 'closings',
      label: 'Clôture de Caisse',
      icon: <CalendarCheck className="w-5 h-5" />,
    },
    {
      id: 'users',
      label: 'Caissiers & Sessions',
      icon: <UserCog className="w-5 h-5 text-sky-400" />,
    },
    {
      id: 'notes',
      label: 'Carnet de Caisse',
      icon: <BookOpen className="w-5 h-5" />,
    },
    {
      id: 'settings',
      label: 'Paramètres & Thème',
      icon: <Settings className="w-5 h-5" />,
    },
  ];

  return (
    <aside className="w-64 bg-slate-950 text-slate-200 border-r border-slate-800/80 flex flex-col shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 via-blue-600 to-sky-400 flex items-center justify-center shadow-lg shadow-blue-500/20 shrink-0">
            <span className="text-white font-black text-xl tracking-tighter">TB</span>
          </div>
          <div className="overflow-hidden">
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg text-white tracking-tight">TOP-BOX</span>
              <span className="text-[10px] font-bold text-sky-400 bg-sky-950/80 border border-sky-800 px-1.5 py-0.2 rounded">PRO</span>
            </div>
            <p className="text-xs text-slate-400 truncate font-medium">{settings.company}</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all cursor-pointer ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/25'
                  : 'text-slate-300 hover:text-white hover:bg-slate-900/90'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={isActive ? 'text-white' : 'text-slate-400'}>{item.icon}</span>
                <span>{item.label}</span>
              </div>
              <div className="flex items-center gap-2">
                {(item.id === 'users' || item.id === 'settings') && !isAdmin && (
                  <span
                    title="Verrouillé — Réservé à l'Administrateur"
                    className="p-1 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30"
                  >
                    <Lock className="w-3 h-3" />
                  </span>
                )}
                {item.badge !== undefined && (
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                      isActive ? 'bg-white text-blue-700' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </nav>

      {/* Active Cashier Session Badge */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/50">
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900 border border-slate-800">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
              currentUser?.role === 'Administrateur' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-blue-600/20 text-sky-300'
            }`}>
              {(currentUser?.fullName || currentUser?.username || 'C').charAt(0)}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-bold text-slate-200 truncate">
                {currentUser?.fullName || currentUser?.username || settings?.cashier || 'Caissier'}
              </p>
              <div className="flex items-center gap-1.5 text-[11px] text-emerald-400">
                <CircleDot className="w-2.5 h-2.5 animate-pulse" />
                <span>{currentUser?.role || 'Session Active'}</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => setCurrentPage('users')}
            title="Changer de session / Gérer les caissiers"
            className="p-1.5 rounded-md hover:bg-slate-800 text-slate-400 hover:text-sky-300 transition-colors ml-1 cursor-pointer"
          >
            <UserCog className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
