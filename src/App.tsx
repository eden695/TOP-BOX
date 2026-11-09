/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { POSProvider, usePOS } from './context/POSContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { POSScreen } from './components/POSScreen';
import { ProductsScreen } from './components/ProductsScreen';
import { SalesHistoryScreen } from './components/SalesHistoryScreen';
import { ClientsScreen } from './components/ClientsScreen';
import { CashClosingScreen } from './components/CashClosingScreen';
import { UsersScreen } from './components/UsersScreen';
import { NotesScreen } from './components/NotesScreen';
import { SettingsScreen } from './components/SettingsScreen';
import { ReceiptModal } from './components/ReceiptModal';
import { AdminLockScreen } from './components/AdminLockScreen';

const MainLayout: React.FC = () => {
  const { currentPage, isAdmin } = usePOS();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 font-sans text-slate-100 antialiased">
      {/* Permanent Left Navigation */}
      <Sidebar />

      {/* Main Center & Right Work Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-slate-950">
        <Header />

        {/* Dynamic Page Router */}
        <main className="flex-1 overflow-hidden flex flex-col">
          {currentPage === 'dashboard' && <Dashboard />}
          {currentPage === 'pos' && <POSScreen />}
          {currentPage === 'products' && <ProductsScreen />}
          {currentPage === 'history' && <SalesHistoryScreen />}
          {currentPage === 'clients' && <ClientsScreen />}
          {currentPage === 'closings' && <CashClosingScreen />}
          {currentPage === 'users' && (isAdmin ? <UsersScreen /> : <AdminLockScreen pageTitle="Caissiers & Sessions" />)}
          {currentPage === 'notes' && <NotesScreen />}
          {currentPage === 'settings' && (isAdmin ? <SettingsScreen /> : <AdminLockScreen pageTitle="Paramètres & Thème" />)}
        </main>
      </div>

      {/* Global Thermal Receipt Modal */}
      <ReceiptModal />
    </div>
  );
};

export default function App() {
  return (
    <POSProvider>
      <MainLayout />
    </POSProvider>
  );
}
