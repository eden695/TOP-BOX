import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Trash2 } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('TOP-BOX Error caught by boundary:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleResetCache = () => {
    try {
      localStorage.removeItem('topbox_current_user');
      localStorage.removeItem('topbox_cart');
      window.location.reload();
    } catch {
      window.location.reload();
    }
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen w-screen items-center justify-center bg-slate-950 p-6 text-slate-100">
          <div className="max-w-md w-full rounded-2xl border border-rose-500/30 bg-slate-900 p-8 shadow-2xl text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-400">
              <AlertTriangle className="h-8 w-8" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">Une interruption inattendue est survenue</h2>
            <p className="text-sm text-slate-400 mb-6">
              L'application a détecté une anomalie d'affichage. Vous pouvez recharger l'interface en toute sécurité.
            </p>
            <div className="space-y-3">
              <button
                onClick={this.handleReload}
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white hover:bg-blue-500 transition-colors shadow-lg shadow-blue-500/20"
              >
                <RefreshCw className="h-4 w-4" />
                Recharger TOP-BOX POS
              </button>
              <button
                onClick={this.handleResetCache}
                className="w-full flex items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-2.5 text-xs font-medium text-slate-300 hover:bg-slate-700 transition-colors"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Réinitialiser la session temporaire
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
